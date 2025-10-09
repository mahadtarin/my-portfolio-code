import os
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except Exception:
    PYMUPDF_AVAILABLE = False
try:
    import pdfplumber  # type: ignore
    PDFPLUMBER_AVAILABLE = True
except Exception:
    PDFPLUMBER_AVAILABLE = False

# Configuration - Update these paths for your files
PDF_FILE = r"path/to/your/document.pdf"
MD_FOLDER = r"path/to/your/markdown/folder"
OUTPUT_HTML = r"image_verification_report.html"

# --- Configuration ---
# If MD file prefix 1_ corresponds to PDF physical page N, set PAGE_OFFSET = (N-1)
# Example: if 1_ maps to PDF page 5 -> PAGE_OFFSET = 4
PAGE_OFFSET = 0

# Tolerance mode: consider a page "matched" if PDF has AT LEAST as many images as MD expects
TOLERANCE_MODE = True
# Report any difference (pdf != md) in mismatch details even if tolerated
REPORT_ALL_DIFFERENCES = True
# New: In per-page Status column treat any difference as MISMATCH (ignores tolerance for display)
STATUS_STRICT_DIFFERENCE = True

# Ignore MD files with zero images? (keeps them for completeness)
IGNORE_ZERO_IMAGE_MD = True

# New: count every drawn image/icon occurrence (appearance-based) when using PyMuPDF
STRICT_PYMUPDF_APPEARANCE_MODE = True  # set False to revert to unique resource image counting
# New: enable deeper PyPDF2 recursive /XObject + inline image scan
ENHANCED_PYPDF2_IMAGE_SCAN = True

try:
    import PyPDF2  # type: ignore
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False

def find_md_images(md_folder: str) -> Dict[str, List[str]]:
    """Return mapping of md filename -> list of image filenames (basename).
    Supports:
      - Markdown images: ![alt](path/to/img.png "optional")
      - HTML <img> tags: <img src="path/to/img.png" alt="..."> (case-insensitive)
    """
    files_with_images: Dict[str, List[str]] = {}
    for fname in sorted(os.listdir(md_folder)):
        if not fname.lower().endswith('.md'):
            continue
        path = os.path.join(md_folder, fname)
        try:
            with open(path, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Failed to read {fname}: {e}")
            continue

        # Markdown image syntax
        md_matches = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content)

        # HTML <img> tag src= (handles single/double quotes, extra attributes)
        html_matches = re.findall(
            r'<img\b[^>]*?\bsrc\s*=\s*["\']([^"\']+)["\']',
            content,
            flags=re.IGNORECASE
        )

        combined: List[str] = []
        for src in md_matches + html_matches:
            # Strip any trailing title (Markdown) or fragment/query if needed
            cleaned = src.strip()
            # Remove optional title after space (Markdown)
            if ' ' in cleaned and cleaned.startswith(('http://', 'https://')) is False:
                # Keep only the first token for local paths
                cleaned = cleaned.split()[0]
            # Normalize to basename
            basename = os.path.basename(cleaned)
            if basename and basename not in combined:
                combined.append(basename)

        if combined:
            files_with_images[fname] = combined
    return files_with_images

def map_md_files_to_pages(md_images: Dict[str, List[str]]) -> Dict[int, Dict[str, Any]]:
    """Map MD numeric prefix (e.g., 1_intro.md) to its image count applying PAGE_OFFSET."""
    page_map: Dict[int, Dict[str, Any]] = {}
    prefix_re = re.compile(r'^(\d+)_')
    for fname, imgs in md_images.items():
        m = prefix_re.match(fname)
        if not m:
            continue  # skip files without numeric prefix
        page = int(m.group(1)) + PAGE_OFFSET
        if IGNORE_ZERO_IMAGE_MD and len(imgs) == 0:
            continue
        page_map[page] = {
            'md_file': fname,
            'md_image_count': len(imgs),
            'md_images': imgs,
        }
    return page_map

def count_pdf_images(pdf_path: str, verbose: bool = False) -> Tuple[Dict[int, int], int, str]:
    """
    Robust image occurrence counter per 1-based page index.
    Tries PyMuPDF heuristics first (if available), then a PyPDF2 fallback that:
      - counts /Name Do occurrences in content streams,
      - inspects XObject entries and recursively counts Form XObjects' internal images,
      - counts inline images (BI...EI).
    Returns (page_counts_dict, total_images, method_used_string).
    """
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return {}, 0, 'none'

    page_counts: Dict[int, int] = {}
    methods_used = []

    # --- Helper: PyPDF2 page-level robust counter (counts Do occurrences, inline images, recurses Forms) ---
    def _count_images_pypdf2_for_page(reader, page_index: int) -> int:
        try:
            page = reader.pages[page_index - 1]
        except Exception:
            return 0

        # build content bytes
        content_bytes = b''
        try:
            contents = page.get_contents()
        except Exception:
            contents = None
        if contents:
            if isinstance(contents, list):
                for c in contents:
                    try:
                        content_bytes += c.get_data()
                    except Exception:
                        try:
                            content_bytes += c.get_object().get_data()
                        except Exception:
                            pass
            else:
                try:
                    content_bytes += contents.get_data()
                except Exception:
                    try:
                        content_bytes += contents.get_object().get_data()
                    except Exception:
                        pass

        # inline images (BI ... EI)
        inline_imgs = re.findall(br'\bBI\b.*?\bEI\b', content_bytes, flags=re.DOTALL)
        inline_count = len(inline_imgs)

        # find Do uses: "/Name Do"
        do_names = re.findall(br'/([^\s/]+)\s+Do', content_bytes)

        # build XObject mapping (name -> object)
        try:
            resources = page.get('/Resources') or {}
        except Exception:
            resources = {}
        xobjects = resources.get('/XObject') or {}
        name_to_xobj = {}
        try:
            for name, xo in getattr(xobjects, 'items', lambda: [])():
                # name might be a NameObject like '/Im0' -> str(name) -> '/Im0'
                try:
                    nstr = str(name)
                except Exception:
                    try:
                        nstr = name.decode('latin1') if isinstance(name, bytes) else str(name)
                    except Exception:
                        nstr = str(name)
                if nstr.startswith('/'):
                    nstr = nstr[1:]
                try:
                    xo_obj = xo.get_object()
                except Exception:
                    xo_obj = xo
                name_to_xobj[nstr] = xo_obj
        except Exception:
            name_to_xobj = {}

        # recursive counter for an XObject invoked once
        def _count_images_in_xobj(xobj, visited) -> int:
            try:
                oid = id(xobj)
                if oid in visited:
                    return 0
                visited.add(oid)
            except Exception:
                pass

            try:
                subtype = xobj.get('/Subtype')
            except Exception:
                subtype = None

            # direct image XObject
            if subtype == '/Image':
                return 1

            # Form XObject: check its internal XObjects + inline images inside its stream
            if subtype == '/Form':
                total = 0
                # nested XObjects inside the form
                try:
                    fres = xobj.get('/Resources') or {}
                    fnested = fres.get('/XObject') or {}
                    for n, v in getattr(fnested, 'items', lambda: [])():
                        try:
                            vobj = v.get_object()
                        except Exception:
                            vobj = v
                        total += _count_images_in_xobj(vobj, visited)
                except Exception:
                    pass
                # inline images inside the form's own stream(s)
                try:
                    form_data = xobj.get_data()
                    total += len(re.findall(br'\bBI\b.*?\bEI\b', form_data, flags=re.DOTALL))
                except Exception:
                    pass
                return total

            return 0

        total = inline_count
        # for every Do occurrence, add images inside that XObject invocation
        for nm_bytes in do_names:
            try:
                nm = nm_bytes.decode('latin1')
            except Exception:
                nm = str(nm_bytes)
            xobj = name_to_xobj.get(nm)
            if xobj:
                total += _count_images_in_xobj(xobj, set())
            else:
                # If referenced name not found in XObject map, still count as 1 usage (best-effort)
                total += 1

        return total

    # --- PyMuPDF heuristics (appearance-oriented) ---
    pymupdf_counts: Dict[int, int] = {}
    pymupdf_methods_used = []
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            for i, page in enumerate(doc, start=1):
                candidates = []

                # 1) direct page.get_image_info (if available)
                try:
                    if hasattr(page, 'get_image_info'):
                        try:
                            info = page.get_image_info(xrefs=True)
                            cnt = len(info) if info is not None else 0
                            candidates.append(('pymupdf.image_info', cnt))
                        except Exception:
                            pass
                except Exception:
                    pass

                # 2) page.get_text('rawdict') block scan (counts image blocks)
                try:
                    raw = page.get_text("rawdict")
                    blocks = raw.get("blocks", []) if isinstance(raw, dict) else []
                    cnt = sum(1 for blk in blocks if blk.get("type") == 1)
                    candidates.append(('pymupdf.rawdict_blocks', cnt))
                except Exception:
                    pass

                # 3) displaylist -> textpage -> rawdict (deeper)
                try:
                    dlist = page.get_displaylist()
                    tp = dlist.get_textpage()
                    # either extractRAWDICT or get_text("rawdict") of textpage - fallback to get_text
                    try:
                        raw2 = tp.extractRAWDICT()
                        blocks2 = raw2.get("blocks", []) if isinstance(raw2, dict) else []
                        cnt2 = sum(1 for blk in blocks2 if blk.get("type") == 1)
                    except Exception:
                        raw2 = tp.get_text("rawdict")
                        blocks2 = raw2.get("blocks", []) if isinstance(raw2, dict) else []
                        cnt2 = sum(1 for blk in blocks2 if blk.get("type") == 1)
                    candidates.append(('pymupdf.displaylist_blocks', cnt2))
                except Exception:
                    pass

                # 4) unique resource-based images (page.get_images(full=True)) - helpful but dedupes reused images
                try:
                    imgs = page.get_images(full=True)
                    cnt_unique = len(imgs) if imgs is not None else 0
                    candidates.append(('pymupdf.unique_images', cnt_unique))
                except Exception:
                    pass

                # choose best candidate (max) for this page (0 if none)
                best_count = 0
                best_methods = []
                for m, c in candidates:
                    if c > best_count:
                        best_count = c
                        best_methods = [m]
                    elif c == best_count:
                        best_methods.append(m)
                pymupdf_counts[i] = best_count
                pymupdf_methods_used.append((i, best_methods, candidates))
            doc.close()
            methods_used.append('pymupdf')
        except Exception as e:
            if verbose:
                print(f"[count_pdf_images] pymupdf attempt failed: {e}")

    # --- PyPDF2 fallback (robust 'Do' & forms expansion) ---
    pypdf2_counts: Dict[int, int] = {}
    if PYPDF2_AVAILABLE:
        try:
            reader = PyPDF2.PdfReader(pdf_path)
            for i in range(1, len(reader.pages) + 1):
                try:
                    c = _count_images_pypdf2_for_page(reader, i)
                    pypdf2_counts[i] = c
                except Exception as e:
                    pypdf2_counts[i] = 0
            methods_used.append('pypdf2_do_scan')
        except Exception as e:
            if verbose:
                print(f"[count_pdf_images] PyPDF2 fallback failed: {e}")

    # --- pdfplumber lightweight fallback (placement-aware) ---
    pdfplumber_counts: Dict[int, int] = {}
    if PDFPLUMBER_AVAILABLE:
        try:
            import pdfplumber  # re-import safe
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    try:
                        imgs = getattr(page, 'images', []) or []
                        pdfplumber_counts[i] = len(imgs)
                    except Exception:
                        pdfplumber_counts[i] = 0
            methods_used.append('pdfplumber')
        except Exception as e:
            if verbose:
                print(f"[count_pdf_images] pdfplumber attempt failed: {e}")

    # --- Combine: for each page, take maximum reported by available methods (best-effort) ---
    all_pages = set()
    all_pages.update(pymupdf_counts.keys())
    all_pages.update(pypdf2_counts.keys())
    all_pages.update(pdfplumber_counts.keys())
    # if none of the above produced pages, try a very crude fallback scanning entire PDF bytes for /Subtype /Image
    fallback_total = 0
    if not all_pages:
        try:
            with open(pdf_path, 'rb') as f:
                data = f.read()
            fallback_total = len(re.findall(br'/Subtype\s*/Image', data))
            if fallback_total:
                page_counts[1] = fallback_total
                methods_used.append('fallback_text_scan')
                if verbose:
                    print("[count_pdf_images] used fallback_text_scan")
                return page_counts, fallback_total, '|'.join(methods_used)
        except Exception:
            pass

    for p in sorted(all_pages):
        candidates = []
        if p in pymupdf_counts:
            candidates.append(('pymupdf_best', pymupdf_counts[p]))
        if p in pypdf2_counts:
            candidates.append(('pypdf2_do', pypdf2_counts[p]))
        if p in pdfplumber_counts:
            candidates.append(('pdfplumber', pdfplumber_counts[p]))

        if candidates:
            # choose max across candidates (appearance-based goal)
            chosen_method, chosen_count = max(candidates, key=lambda t: t[1])
            page_counts[p] = chosen_count
            if verbose:
                print(f"[count_pdf_images] page {p}: chosen {chosen_method} => {chosen_count}; raw_candidates={candidates}")
        else:
            page_counts[p] = 0

    # Per-page decrement: total PDF image = total PDF image -1 for every PDF page
    if page_counts:
        for k in page_counts:
            page_counts[k] = max(0, page_counts[k] - 1)
        methods_used.append('minus1_per_page')
    total_images = sum(page_counts.values())
    method_str = '|'.join(methods_used) if methods_used else 'none'
    return page_counts, total_images, method_str


def build_comparison(md_page_map: Dict[int, Dict[str, Any]], pdf_page_counts: Dict[int, int]) -> List[Dict[str, Any]]:
    """Create list of comparison rows per page present in either source, applying tolerance if enabled."""
    all_pages = sorted(set(md_page_map.keys()) | set(pdf_page_counts.keys()))
    rows: List[Dict[str, Any]] = []
    for p in all_pages:
        md_entry = md_page_map.get(p)
        md_cnt = md_entry['md_image_count'] if md_entry else 0
        pdf_cnt = pdf_page_counts.get(p, 0)
        if TOLERANCE_MODE:
            match_flag = pdf_cnt >= md_cnt
        else:
            match_flag = (md_cnt == pdf_cnt)
        diff = pdf_cnt - md_cnt
        rows.append({
            'page': p,
            'md_file': md_entry['md_file'] if md_entry else None,
            'md_image_count': md_cnt,
            'pdf_image_count': pdf_cnt,
            'match': match_flag,
            'exact_match': md_cnt == pdf_cnt,
            'diff': diff,
            'different': diff != 0
        })
    return rows

def generate_html_report(files_with_images, md_folder, output_path,
                         comparison_rows=None, pdf_total=0, md_total=0, method_used=''):
    with open(output_path, 'w', encoding='utf-8') as html_file:
        html_file.write("""
        <html>
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Verification Report</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: #f9f9f9; 
                line-height: 1.6; 
            }
            h1 { 
                color: #2c3e50; 
                border-bottom: 3px solid #3498db; 
                padding-bottom: 10px; 
            }
            h2 { 
                color: #2c3e50; 
                border-bottom: 2px solid #eee; 
                padding-bottom: 5px; 
                margin-top: 30px;
            }
            .file-section { 
                background: #fff; 
                margin-bottom: 30px; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            }
            .filename { 
                background: #e8f4fd; 
                padding: 5px 10px; 
                border-radius: 4px; 
                font-family: 'Courier New', monospace; 
                font-size: 0.9em; 
                color: #2c3e50;
            }
            .heading { 
                background: #e8f6e8; 
                padding: 8px 12px; 
                border-radius: 4px; 
                font-weight: bold; 
                color: #2c3e50;
                margin: 10px 0;
            }
            .image-list { 
                background: #f8f9fa; 
                padding: 15px; 
                border-left: 4px solid #3498db; 
                margin: 10px 0; 
            }
            .image-item { 
                margin: 8px 0; 
                padding: 5px 0; 
                font-family: 'Courier New', monospace; 
                color: #34495e;
            }
            .summary { 
                background: #fff; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                margin-bottom: 30px;
            }
            .count { 
                color: #3498db; 
                font-weight: bold; 
                font-size: 1.2em; 
            }
            .no-images { 
                background: #fff3cd; 
                color: #856404; 
                padding: 20px; 
                border-radius: 8px; 
                border: 1px solid #ffeaa7; 
                text-align: center;
            }
        </style>
        </head>
        <body>
            <h1>Image Verification Report</h1>
            <p><strong>Purpose:</strong> Verify that image counts per page in PDF match counts per corresponding Markdown file (numeric prefix mapping).</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """)

        if files_with_images:
            # Summary section
            total_files = len(files_with_images)
            total_images = sum(len(images) for images in files_with_images.values())

            html_file.write(f"""
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total MD files with images:</strong> <span class="count">{total_files}</span></p>
                <p><strong>Total MD images referenced:</strong> <span class="count">{total_images}</span></p>
                <p><strong>Total PDF images counted:</strong> <span class="count">{pdf_total}</span> (method: {method_used})</p>
                <p><strong>Pages compared:</strong> <span class="count">{len(comparison_rows) if comparison_rows else 0}</span></p>
                <p><strong>Config:</strong> offset={PAGE_OFFSET}, tolerance={'on' if TOLERANCE_MODE else 'off'}, strict_appearance={'on' if STRICT_PYMUPDF_APPEARANCE_MODE else 'off'}</p>
            </div>
            """)

            # New mismatch details section (before per-page comparison)
            if comparison_rows:
                # Use differences (any diff) or strict mismatches based on config
                if REPORT_ALL_DIFFERENCES:
                    mismatches = [r for r in comparison_rows if r.get('different')]
                else:
                    mismatches = [r for r in comparison_rows if not r['match']]
                if mismatches:
                    html_file.write("""
                    <div class="file-section">
                        <h2>Mismatch Details</h2>
                        <table style="width:100%;border-collapse:collapse;font-size:14px;">
                            <tr style="background:#ffecec;">
                                <th style="border:1px solid #ccc;padding:6px;">Page</th>
                                <th style="border:1px solid #ccc;padding:6px;">MD File</th>
                                <th style="border:1px solid #ccc;padding:6px;">MD</th>
                                <th style="border:1px solid #ccc;padding:6px;">PDF</th>
                                <th style="border:1px solid #ccc;padding:6px;">Diff</th>
                                <th style="border:1px solid #ccc;padding:6px;">Status</th>
                            </tr>
                    """)
                    for r in mismatches:
                        md_file_display = r['md_file'] or '—'
                        status = 'TOLERATED' if r['match'] and r['diff'] != 0 else ('MISMATCH' if not r['match'] else 'OK')
                        diff_color = '#c62828' if r['diff'] != 0 else '#2e7d32'
                        html_file.write(f"""
                            <tr>
                                <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{r['page']}</td>
                                <td style='border:1px solid #ccc;padding:6px;'>{md_file_display}</td>
                                <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{r['md_image_count']}</td>
                                <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{r['pdf_image_count']}</td>
                                <td style='border:1px solid #ccc;padding:6px;text-align:center;color:{diff_color};'>{r['diff']}</td>
                                <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{status}</td>
                            </tr>
                        """)
                    html_file.write("""
                        </table>
                    </div>
                    """)

            # Comparison table
            if comparison_rows:
                html_file.write("""
                <div class="file-section">
                    <h2>Per-Page Comparison</h2>
                    <table style="width:100%;border-collapse:collapse;font-size:14px;">
                        <tr style="background:#f0f0f0;">
                            <th style="border:1px solid #ccc;padding:6px;">Page</th>
                            <th style="border:1px solid #ccc;padding:6px;">MD File</th>
                            <th style="border:1px solid #ccc;padding:6px;">MD Images</th>
                            <th style="border:1px solid #ccc;padding:6px;">PDF Images</th>
                            <th style="border:1px solid #ccc;padding:6px;">Status</th>
                            <th style="border:1px solid #ccc;padding:6px;">Exact</th>
                        </tr>
                """)
                for row in comparison_rows:
                    if STATUS_STRICT_DIFFERENCE:
                        status_is_match = (row['diff'] == 0)
                    else:
                        status_is_match = row['match']
                    status = 'MATCH' if status_is_match else 'MISMATCH'
                    color = '#2e7d32' if status_is_match else '#c62828'
                    md_file_display = row['md_file'] or '—'
                    html_file.write(f"""
                        <tr>
                            <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{row['page']}</td>
                            <td style='border:1px solid #ccc;padding:6px;'>{md_file_display}</td>
                            <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{row['md_image_count']}</td>
                            <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{row['pdf_image_count']}</td>
                            <td style='border:1px solid #ccc;padding:6px;font-weight:bold;color:{color};'>{status}</td>
                            <td style='border:1px solid #ccc;padding:6px;text-align:center;'>{'✓' if row['exact_match'] else ''}</td>
                        </tr>
                    """)
                html_file.write("""
                    </table>
                </div>
                """)
        else:
            html_file.write("""
            <div class="no-images">
                <h2>No Images Found</h2>
                <p>No images were found in any Markdown files in the specified directory.</p>
            </div>
            """)

        html_file.write("""
        </body>
        </html>
        """)

def main():
    print("Starting image count verification...")
    md_images = find_md_images(MD_FOLDER)
    md_page_map = map_md_files_to_pages(md_images)
    pdf_page_counts, pdf_total, method_used = count_pdf_images(PDF_FILE)
    comparison_rows = build_comparison(md_page_map, pdf_page_counts)

    md_total = sum(len(v) for v in md_images.values())
    mismatches = [r for r in comparison_rows if not r['match']]
    difference_pages = [r for r in comparison_rows if r.get('different')]
    if method_used == 'fallback_text_scan':
        print("WARNING: Using crude fallback image scan; per-page counts unreliable. Install 'pymupdf' (pip install pymupdf) for accurate results.")

    # Console summary
    print(f"MD files with images: {len(md_images)} | Total MD images: {md_total}")
    print(f"PDF total images ({method_used}): {pdf_total} | Pages compared: {len(comparison_rows)}")
    print(f"Mismatched pages (tolerance logic): {len(mismatches)} | Pages with any difference: {len(difference_pages)}")
    if difference_pages and len(mismatches) == 0 and REPORT_ALL_DIFFERENCES:
        print("Note: Differences exist but are tolerated (PDF >= MD). They will appear in the HTML mismatch section.")
    if mismatches:
        for r in mismatches[:20]:  # limit console noise
            print(f"  Page {r['page']}: MD={r['md_image_count']} vs PDF={r['pdf_image_count']} (file={r['md_file']})")
    else:
        print("All compared pages match image counts.")

    if pdf_total == 0:
        print("NOTICE: 0 images detected. If the PDF has images, install 'pymupdf' (pip install pymupdf) for accurate appearance counting.")

    generate_html_report(md_images, MD_FOLDER, OUTPUT_HTML, comparison_rows, pdf_total, md_total, method_used)
    print(f"HTML report generated: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()