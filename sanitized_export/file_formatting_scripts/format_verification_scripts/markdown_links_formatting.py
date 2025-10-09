#!/usr/bin/env python3
"""
PDF Hyperlink Extractor - Simple and Effective
Extracts ALL hyperlinks (internal and external) from PDF pages
"""

import os
import sys
import re
from typing import List, Dict, Any
from datetime import datetime

# Try multiple PDF libraries for maximum hyperlink detection
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

print(f"PDF Libraries Available: PyPDF2={PYPDF2_AVAILABLE}, pdfplumber={PDFPLUMBER_AVAILABLE}, PyMuPDF={PYMUPDF_AVAILABLE}")

if not any([PYPDF2_AVAILABLE, PDFPLUMBER_AVAILABLE, PYMUPDF_AVAILABLE]):
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2
    PYPDF2_AVAILABLE = True

class PDFLinkExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        # Keep file handle open for PyPDF2 (lazy stream access); None for other libs
        self._pdf_file_handle = None  # type: ignore

    def open_pdf(self):
        """Open the PDF document using the best available library"""
        try:
            if PYMUPDF_AVAILABLE:
                import fitz
                self.doc = fitz.open(self.pdf_path)
                print(f"Opened PDF with PyMuPDF: {os.path.basename(self.pdf_path)}")
                print(f"Total pages: {self.doc.page_count}")
                return True
            elif PDFPLUMBER_AVAILABLE:
                import pdfplumber
                self.doc = pdfplumber.open(self.pdf_path)
                print(f"Opened PDF with pdfplumber: {os.path.basename(self.pdf_path)}")
                print(f"Total pages: {len(self.doc.pages)}")
                return True
            elif PYPDF2_AVAILABLE:
                import PyPDF2
                # Keep file handle open (no context manager) so PdfReader can access streams lazily
                self._pdf_file_handle = open(self.pdf_path, 'rb')
                self.doc = PyPDF2.PdfReader(self._pdf_file_handle)
                print(f"Opened PDF with PyPDF2: {os.path.basename(self.pdf_path)}")
                try:
                    print(f"Total pages: {len(self.doc.pages)}")
                except Exception as e:
                    print(f"Warning: Could not determine page count immediately: {e}")
                return True
        except Exception as e:
            print(f"Failed to open PDF: {e}")
            return False
    
    def close_pdf(self):
        """Close the PDF document"""
        # Some libraries require explicit close; PyPDF2's PdfReader has no close()
        try:
            if self.doc and hasattr(self.doc, 'close'):
                self.doc.close()
        except Exception as e:
            print(f"Warning closing doc: {e}")
        # Close underlying file handle if we opened one for PyPDF2
        if self._pdf_file_handle:
            try:
                self._pdf_file_handle.close()
            except Exception as e:
                print(f"Warning closing file handle: {e}")
            finally:
                self._pdf_file_handle = None
    
    def extract_page_links(self, page_num: int) -> List[Dict[str, Any]]:
        if not self.doc:
            return []
        
        links = []
        print(f"Scanning page {page_num} for ALL hyperlinks (including blue clickable text)...")
        
        try:
            if PYMUPDF_AVAILABLE and hasattr(self.doc, 'page_count'):
                # Use PyMuPDF - COMPREHENSIVE link detection
                page = self.doc[page_num - 1]
                
                # Method 1: Extract ALL link annotations (most comprehensive)
                page_links = page.get_links()
                print(f"Found {len(page_links)} link annotations")
                
                for link in page_links:
                    rect = link.get('from', None)
                    link_text = ""
                    if rect:
                        try:
                            link_text = page.get_textbox(rect).strip()
                        except:
                            pass
                    
                    if 'uri' in link and link['uri']:
                        # External URL
                        uri = str(link['uri']).strip()
                        links.append({
                            'page': page_num,
                            'type': 'external_link',
                            'uri': uri,
                            'text': link_text,
                            'rect': rect
                        })
                        print(f"  EXTERNAL: {uri} (text: '{link_text}')")
                    
                    elif 'page' in link:
                        # Internal page reference
                        target_page = link['page']
                        links.append({
                            'page': page_num,
                            'type': 'page_reference',
                            'uri': f"page_{target_page}",
                            'text': link_text,
                            'rect': rect
                        })
                        print(f"  PAGE_REF: page_{target_page} (text: '{link_text}')")
                    
                    elif 'kind' in link:
                        # Other internal links
                        link_kind = link['kind']
                        
                        if link_kind == 1:  # LINK_GOTO (internal navigation)
                            dest = link.get('to', {})
                            if 'page' in dest:
                                target_page = dest['page']
                                links.append({
                                    'page': page_num,
                                    'type': 'goto_link',
                                    'uri': f"goto_page_{target_page}",
                                    'text': link_text,
                                    'rect': rect
                                })
                                print(f"  GOTO: page_{target_page} (text: '{link_text}')")
                            elif 'name' in dest:
                                dest_name = dest['name']
                                links.append({
                                    'page': page_num,
                                    'type': 'named_destination',
                                    'uri': f"dest_{dest_name}",
                                    'text': link_text,
                                    'rect': rect
                                })
                                print(f"  NAMED_DEST: {dest_name} (text: '{link_text}')")
                        
                        elif link_kind == 3:  # LINK_LAUNCH
                            file_path = link.get('file', '')
                            links.append({
                                'page': page_num,
                                'type': 'file_launch',
                                'uri': f"launch:{file_path}",
                                'text': link_text,
                                'rect': rect
                            })
                            print(f"  LAUNCH: {file_path} (text: '{link_text}')")
                        
                        elif link_kind == 4:  # LINK_NAMED
                            name = link.get('name', '')
                            links.append({
                                'page': page_num,
                                'type': 'named_link',
                                'uri': f"named:{name}",
                                'text': link_text,
                                'rect': rect
                            })
                            print(f"  NAMED: {name} (text: '{link_text}')")
                        
                        else:
                            # Unknown internal link type
                            links.append({
                                'page': page_num,
                                'type': 'unknown_internal',
                                'uri': f"internal_kind_{link_kind}",
                                'text': link_text,
                                'rect': rect
                            })
                            print(f"  UNKNOWN_INTERNAL: kind_{link_kind} (text: '{link_text}')")
                
                # Method 2: AGGRESSIVE blue text detection (capture ALL blue text first)
                all_blue_text = self._extract_all_blue_text_debug(page, page_num)
                links.extend(all_blue_text)
                
                # Method 3: Extract internal page-jumping links (PRIORITY for internal links)
                internal_jumps = self._extract_internal_page_jumps(page, page_num)
                links.extend(internal_jumps)
                
                # Method 4: Detect blue/colored clickable text (often missed internal links)
                colored_links = self._extract_colored_text_links(page, page_num)
                links.extend(colored_links)
                
                # Method 4: Extract underlined text (potential links)
                underlined_links = self._extract_underlined_text_links(page, page_num)
                links.extend(underlined_links)
                
                # Method 5: Text-based URL extraction
                text = page.get_text()
                text_urls = self._extract_text_urls_advanced(text, page_num)
                links.extend(text_urls)
                        
            elif PDFPLUMBER_AVAILABLE and hasattr(self.doc, 'pages'):
                # Fallback to pdfplumber
                page = self.doc.pages[page_num - 1]
                try:
                    hyperlinks = getattr(page, 'hyperlinks', [])
                    print(f"Found {len(hyperlinks)} hyperlinks with pdfplumber")
                    for link in hyperlinks:
                        if 'uri' in link:
                            links.append({
                                'page': page_num,
                                'type': 'hyperlink',
                                'uri': str(link['uri']).strip(),
                                'text': str(link.get('text', ''))
                            })
                            print(f"  HYPERLINK: {link['uri']}")
                except:
                    pass
                
                text = page.extract_text() or ""
                urls = re.findall(r'https?://[^\s<>"\'\(\)\[\]{}]+', text, re.IGNORECASE)
                existing = [l['uri'] for l in links]
                for url in urls:
                    url = url.rstrip('.,;:!?)')
                    if url and url not in existing:
                        links.append({
                            'page': page_num,
                            'type': 'text_url',
                            'uri': url,
                            'text': ''
                        })
                        print(f"  TEXT_URL: {url}")
                        
            elif PYPDF2_AVAILABLE and hasattr(self.doc, 'pages'):
                # Fallback to PyPDF2
                page = self.doc.pages[page_num - 1]
                if '/Annots' in page:
                    try:
                        annotations = page['/Annots']
                        print(f"Found {len(annotations)} annotations with PyPDF2")
                        for annotation in annotations:
                            annotation_obj = annotation.get_object()
                            if '/A' in annotation_obj and '/URI' in annotation_obj['/A']:
                                uri = annotation_obj['/A']['/URI']
                                links.append({
                                    'page': page_num,
                                    'type': 'annotation',
                                    'uri': str(uri),
                                    'text': ''
                                })
                                print(f"  ANNOTATION: {uri}")
                    except:
                        pass
                
                text = page.extract_text()
                urls = re.findall(r'https?://[^\s<>"\'\(\)\[\]{}]+', text, re.IGNORECASE)
                existing = [l['uri'] for l in links]
                for url in urls:
                    url = url.rstrip('.,;:!?)')
                    if url and url not in existing:
                        links.append({
                            'page': page_num,
                            'type': 'text_url',
                            'uri': url,
                            'text': ''
                        })
                        print(f"  TEXT_URL: {url}")
                        
        except Exception as e:
            print(f"Error extracting links: {e}")
        
        # Summary of link types found
        external_count = len([l for l in links if l['type'] in ['external_link', 'hyperlink', 'annotation', 'enhanced_text_url']])
        internal_count = len([l for l in links if l['type'] in ['page_reference', 'goto_link', 'named_destination', 
                                                               'file_launch', 'named_link', 'unknown_internal',
                                                               'colored_text_link', 'underlined_text_link', 'internal',
                                                               'internal_page_jump', 'text_page_reference', 'blue_internal_text']])
        text_url_count = len([l for l in links if l['type'] == 'text_url'])
        
        print(f"TOTAL LINKS FOUND ON PAGE {page_num}: {len(links)}")
        print(f"  External: {external_count}, Internal: {internal_count}, Text URLs: {text_url_count}")
        return links
    
    def extract_all_links(self) -> Dict[int, List[Dict[str, Any]]]:
        """Extract links from all pages"""
        if not self.doc:
            print("PDF not opened")
            return {}
        
        all_links = {}
        total_links = 0
        
        # Get page count based on library
        if hasattr(self.doc, 'page_count'):
            total_pages = self.doc.page_count
        elif hasattr(self.doc, 'pages'):
            total_pages = len(self.doc.pages)
        else:
            print("Cannot determine page count")
            return {}
        
        print(f"\nExtracting links from all {total_pages} pages...")
        
        for page_num in range(1, total_pages + 1):
            page_links = self.extract_page_links(page_num)
            all_links[page_num] = page_links
            total_links += len(page_links)
        
        print(f"\nEXTRACTION COMPLETE")
        print(f"Total links found: {total_links}")
        print(f"Pages with links: {len([p for p, links in all_links.items() if links])}")
        
        return all_links
    
    def generate_html_report(self, all_links: Dict[int, List[Dict[str, Any]]], output_file: str = None):
        """Generate HTML report of all found links"""
        # Set output file path in same directory as PDF if not provided
        if output_file is None:
            pdf_dir = os.path.dirname(self.pdf_path)
            pdf_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_file = os.path.join(pdf_dir, f"{pdf_name}_links_report.html")
        
        external_count = 0
        internal_count = 0
        text_url_count = 0
        total_pages_with_links = len([p for p, links in all_links.items() if links])
        
        # Count link types
        for page_num, links in all_links.items():
            for link in links:
                if link['type'] in ['external_link', 'hyperlink', 'annotation', 'enhanced_text_url']:
                    external_count += 1
                elif link['type'] in ['page_reference', 'goto_link', 'named_destination', 'file_launch', 
                                     'named_link', 'unknown_internal', 'colored_text_link', 'underlined_text_link', 'internal',
                                     'internal_page_jump', 'text_page_reference', 'blue_internal_text']:
                    internal_count += 1
                elif link['type'] == 'text_url':
                    text_url_count += 1
        
        total_count = external_count + internal_count + text_url_count
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Hyperlinks Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .summary {{ background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .stats {{ display: flex; justify-content: space-around; flex-wrap: wrap; }}
        .stat-box {{ background: #3498db; color: white; padding: 15px; margin: 5px; border-radius: 5px; text-align: center; min-width: 120px; }}
        .page-section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }}
        .page-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .link-item {{ margin: 5px 0; padding: 8px; background-color: white; border-radius: 3px; }}
        .external {{ border-left: 4px solid #e74c3c; }}
        .internal {{ border-left: 4px solid #27ae60; }}
        .text-url {{ border-left: 4px solid #f39c12; }}
        .link-url {{ font-family: monospace; color: #2c3e50; }}
        .link-text {{ color: #7f8c8d; font-size: 0.9em; margin-top: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF Hyperlinks Extraction Report</h1>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="stats">
                <div class="stat-box">
                    <div style="font-size: 2em; font-weight: bold;">{total_count}</div>
                    <div>Total Links</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 2em; font-weight: bold;">{external_count}</div>
                    <div>External Links</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 2em; font-weight: bold;">{internal_count}</div>
                    <div>Internal Links</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 2em; font-weight: bold;">{text_url_count}</div>
                    <div>Text URLs</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 2em; font-weight: bold;">{total_pages_with_links}</div>
                    <div>Pages with Links</div>
                </div>
            </div>
        </div>

        <h2>Links by Page</h2>'''
        
        for page_num in sorted(all_links.keys()):
            links = all_links[page_num]
            if not links:
                continue
                
            html_content += f'''
        <div class="page-section">
            <div class="page-title">Page {page_num} ({len(links)} links)</div>'''
            
            for link in links:
                link_class = ""
                if link['type'] in ['external_link', 'hyperlink', 'annotation', 'enhanced_text_url']:
                    link_class = "external"
                elif link['type'] in ['page_reference', 'goto_link', 'named_destination', 'file_launch', 
                                     'named_link', 'unknown_internal', 'colored_text_link', 'underlined_text_link', 'internal',
                                     'internal_page_jump', 'text_page_reference', 'blue_internal_text']:
                    link_class = "internal"
                elif link['type'] == 'text_url':
                    link_class = "text-url"
                
                html_content += f'''
            <div class="link-item {link_class}">
                <div class="link-url">{link['uri']}</div>'''
                
                if link['text'] and link['text'] != link['uri'] and link['text'] != "No text":
                    html_content += f'<div class="link-text">Text: {link["text"]}</div>'
                
                html_content += '</div>'
            
            html_content += '</div>'
        
        html_content += f'''
        <div style="text-align: center; color: #7f8c8d; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
            Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>'''
        
        # Save HTML report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\nHTML report saved: {output_file}")
        print(f"Total links: {total_count} (External: {external_count}, Internal: {internal_count}, Text URLs: {text_url_count})")
        
        return output_file

    def _extract_colored_text_links(self, page, page_num):
        """Extract blue/colored text that indicates clickable links - COMPREHENSIVE VERSION"""
        colored_links = []
        try:
            # Get text with detailed formatting information
            blocks = page.get_text("dict")["blocks"]
            
            # Track all colored text first, then analyze patterns
            all_colored_text = []
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            text = span.get("text", "").strip()
                            font = span.get("font", "")
                            size = span.get("size", 0)
                            flags = span.get("flags", 0)
                            bbox = span.get("bbox", [])
                            
                            # Collect ALL non-black text for analysis
                            if color != 0 and text and len(text.strip()) > 0:
                                all_colored_text.append({
                                    'text': text,
                                    'color': color,
                                    'font': font,
                                    'size': size,
                                    'flags': flags,
                                    'bbox': bbox
                                })
            
            print(f"  Found {len(all_colored_text)} colored text elements")
            
            # Now apply multiple detection strategies
            for item in all_colored_text:
                text = item['text']
                color = item['color']
                bbox = item['bbox']
                
                is_clickable = False
                link_type = ""
                
                # Strategy 1: Pattern-based detection (original)
                if self._is_likely_clickable_text(text):
                    is_clickable = True
                    link_type = "pattern_match"
                
                # Strategy 2: Blue color detection (most common for links)
                elif self._is_blue_color(color):
                    is_clickable = True
                    link_type = "blue_color"
                
                # Strategy 3: URL-like text detection
                elif self._looks_like_url_text(text):
                    is_clickable = True
                    link_type = "url_like"
                
                # Strategy 4: Cross-reference detection (loose matching)
                elif self._is_cross_reference(text):
                    is_clickable = True
                    link_type = "cross_ref"
                
                # Strategy 5: Navigation text detection
                elif self._is_navigation_text(text):
                    is_clickable = True
                    link_type = "navigation"
                
                # Strategy 6: Numbered items that could be clickable
                elif self._is_numbered_item(text):
                    is_clickable = True
                    link_type = "numbered"
                
                # Strategy 7: Short colored text (often clickable)
                elif len(text) <= 50 and not text.isspace():
                    is_clickable = True
                    link_type = "short_colored"
                
                if is_clickable:
                    colored_links.append({
                        'page': page_num,
                        'type': 'colored_text_link',
                        'uri': f"colored_text:{text}",
                        'text': text,
                        'color': color,
                        'bbox': bbox,
                        'detection_strategy': link_type
                    })
                    print(f"  COLORED_LINK: '{text[:50]}...' (color: {color}, strategy: {link_type})")
                                    
        except Exception as e:
            print(f"  Error extracting colored text: {e}")
        
        return colored_links
    
    def _extract_underlined_text_links(self, page, page_num):
        """Extract underlined text that might be links"""
        underlined_links = []
        try:
            # Look for underlined text using text formatting
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            flags = span.get("flags", 0)
                            text = span.get("text", "").strip()
                            
                            # Check if text is underlined (flag 4)
                            if flags & 4 and text and len(text) > 2:
                                if self._is_likely_clickable_text(text):
                                    bbox = span.get("bbox", [])
                                    
                                    underlined_links.append({
                                        'page': page_num,
                                        'type': 'underlined_text_link',
                                        'uri': f"underlined_text:{text}",
                                        'text': text,
                                        'bbox': bbox
                                    })
                                    print(f"  UNDERLINED: '{text}'")
                                    
        except Exception as e:
            print(f"  Error extracting underlined text: {e}")
        
        return underlined_links
    
    def _is_likely_clickable_text(self, text):
        """Determine if text is likely to be clickable based on comprehensive patterns"""
        if not text or len(text.strip()) < 1:
            return False
            
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # Expanded patterns for clickable text
        clickable_patterns = [
            # Page/section references
            r'\bpage\s+\d+\b',  # "page 123"
            r'\bpg\.\s*\d+\b',  # "pg. 123"
            r'\bp\.\s*\d+\b',   # "p. 123"
            r'\bsee\s+(page\s+)?\d+\b',  # "see page 123" or "see 123"
            r'\bon\s+page\s+\d+\b',  # "on page 123"
            
            # Document structure references
            r'\bchapter\s+\d+\b',  # "chapter 5"
            r'\bch\.\s*\d+\b',     # "ch. 5"
            r'\bsection\s+\d+(\.\d+)*\b',  # "section 5.1.2"
            r'\bsec\.\s*\d+(\.\d+)*\b',    # "sec. 5.1"
            r'\bpart\s+\d+\b',     # "part 2"
            r'\bunit\s+\d+\b',     # "unit 3"
            
            # Figure/table references
            r'\bfigure\s+\d+\b',   # "figure 10"
            r'\bfig\.\s*\d+\b',    # "fig. 10"
            r'\btable\s+\d+\b',    # "table 5"
            r'\btbl\.\s*\d+\b',    # "tbl. 5"
            r'\bdiagram\s+\d+\b',  # "diagram 7"
            r'\bchart\s+\d+\b',    # "chart 3"
            r'\bexample\s+\d+\b',  # "example 4"
            
            # Appendix references
            r'\bappendix\s+[a-z]\b',      # "appendix a"
            r'\bapp\.\s*[a-z]\b',         # "app. a"
            r'\bannex\s+[a-z]\b',         # "annex b"
            
            # Numbered items and lists
            r'^\d+(\.\d+)*\s*$',          # "5.2.1" (standalone numbers)
            r'^\d+(\.\d+)*\s+[A-Z]',      # "5.2.1 Something"
            r'^\d+\.\s+',                 # "1. Something"
            r'^\d+\)\s+',                 # "1) Something"
            r'^\([a-z]\)\s+',             # "(a) Something"
            r'^\([0-9]+\)\s+',            # "(1) Something"
            
            # Navigation and action words
            r'\b(next|previous|prev|back|forward)\b',
            r'\b(home|index|contents?|toc|menu)\b',
            r'\b(click|here|link|more|details|info)\b',
            r'\b(continue|proceed|go\s+to|jump\s+to)\b',
            r'\b(return|back\s+to|top|bottom)\b',
            
            # Common link text patterns
            r'\b(read\s+more|learn\s+more|find\s+out)\b',
            r'\b(download|view|open|access)\b',
            r'\b(contact|support|help|faq)\b',
            r'\b(login|sign\s+in|register)\b',
            
            # Title case patterns (often clickable headings)
            r'^[A-Z][a-zA-Z\s]+[A-Z][a-zA-Z\s]*$',  # "Title Case Text"
            
            # URLs and web patterns
            r'www\.',
            r'https?://',
            r'\.com\b|\.org\b|\.net\b|\.edu\b|\.gov\b',
            r'@.*\.',  # Email patterns
            
            # Cross-reference indicators
            r'\b(see|refer\s+to|reference|check|view|visit)\b',
            r'\b(above|below|earlier|later|following|preceding)\b',
            r'\b(as\s+shown|as\s+described|as\s+mentioned)\b',
            
            # Special characters that often indicate links
            r'→|←|↑|↓',  # Arrow symbols
            r'»|«|›|‹',   # Angle brackets
            r'▶|▼|▲|◄',   # Triangle symbols
        ]
        
        # Check against all patterns
        for pattern in clickable_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Additional checks for common link formats
        
        # Check for typical cross-reference formats
        if re.match(r'^[A-Z][a-zA-Z\s]+\d+$', text_clean):  # "Chapter 5", "Figure 10"
            return True
        
        # Check for numbered references (loose)
        if re.match(r'^\d+(\.\d+)*$', text_clean):  # "5.2.1"
            return True
            
        # Check for bracketed references
        if re.match(r'^\[.*\]$', text_clean):  # "[Reference]"
            return True
        
        # Check for parenthetical references
        if re.match(r'^\(.*\)$', text_clean) and len(text_clean) > 3:  # "(Something)"
            return True
        
        # Check for ALL CAPS text (often headings/links)
        if text_clean.isupper() and len(text_clean) > 2 and len(text_clean) < 50:
            return True
            
        # Check for mixed case with no spaces (often identifiers/codes)
        if re.match(r'^[A-Z][a-zA-Z0-9]+[0-9]$', text_clean):  # "ABC123"
            return True
        
        # Check for text that contains numbers and letters (codes, IDs)
        if re.search(r'\d', text_clean) and re.search(r'[a-zA-Z]', text_clean) and len(text_clean) < 20:
            return True
        
        return False
    
    def _extract_text_urls_advanced(self, text, page_num):
        """Advanced URL extraction with better patterns"""
        text_urls = []
        
        # Enhanced URL patterns
        url_patterns = [
            r'https?://[^\s<>"\'\(\)\[\]{}]+',  # Standard URLs
            r'www\.[^\s<>"\'\(\)\[\]{}]+',  # www URLs
            r'[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|io|co\.uk|de|fr|jp)\b[^\s<>"\'\(\)\[\]{}]*',  # Domain-based
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',  # Email addresses
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match.group(0)
                
                # Clean URL
                url = url.rstrip('.,;:!?)]}>').strip()
                
                if url and len(url) > 5:  # Minimum length check
                    # Normalize URL
                    if not url.startswith(('http://', 'https://', 'mailto:')):
                        if url.startswith('www.'):
                            url = 'https://' + url
                        elif '@' in url:
                            url = 'mailto:' + url
                        elif '.' in url:
                            url = 'https://' + url
                    
                    text_urls.append({
                        'page': page_num,
                        'type': 'enhanced_text_url',
                        'uri': url,
                        'text': url,
                        'position': match.start()
                    })
                    print(f"  ENHANCED_URL: {url}")
        
        return text_urls

    def _is_blue_color(self, color):
        """Check if the color is blue or blue-ish with comprehensive detection"""
        if color == 0:
            return False
        
        # Common blue colors in PDFs (expanded list)
        blue_patterns = [
            0x0000ff,  # Pure blue
            0x0066cc,  # Light blue
            0x336699,  # Medium blue
            0x003366,  # Dark blue
            0x6699ff,  # Sky blue
            0x3366ff,  # Bright blue
            0x0099ff,  # Azure blue
            0x4169e1,  # Royal blue
            0x1e90ff,  # Dodger blue
            0x6495ed,  # Cornflower blue
            0x87ceeb,  # Sky blue light
            0x4682b4,  # Steel blue
            0x5f9ea0,  # Cadet blue
            0x0080ff,  # Electric blue
            0x007fff,  # Azure
            0x0066ff,  # Blue RYB
        ]
        
        # Check exact matches first
        if color in blue_patterns:
            return True
        
        # Extract RGB components for sophisticated blue detection
        try:
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            
            # Multiple blue detection strategies:
            
            # Strategy 1: Blue dominant (classic approach)
            if b > r and b > g and b > 100:
                return True
            
            # Strategy 2: Blue is significantly higher than others
            if b > (r + g) / 2 and b > 80:
                return True
            
            # Strategy 3: Blue-ish colors (blue is strong component)
            if b > 150 and (b > r * 1.5 or b > g * 1.5):
                return True
            
            # Strategy 4: Dark blue detection (low overall but blue dominant)
            if b > r and b > g and b > 50 and (r + g + b) < 200:
                return True
            
            # Strategy 5: Light blue detection (high blue with other components)
            if b > 180 and b > r and b > g:
                return True
                
            # Strategy 6: Blue in any position (for non-standard color formats)
            total = r + g + b
            if total > 0:
                blue_ratio = b / total
                if blue_ratio > 0.6:  # Blue is 60% or more of total color
                    return True
            
        except Exception as e:
            print(f"    Error analyzing color {color}: {e}")
        
        return False
    
    def _looks_like_url_text(self, text):
        """Check if text looks like a URL or web address"""
        url_indicators = [
            r'www\.',
            r'https?://',
            r'\.com\b',
            r'\.org\b',
            r'\.net\b',
            r'\.edu\b',
            r'\.gov\b',
            r'@.*\.',  # Email pattern
        ]
        
        text_lower = text.lower()
        for pattern in url_indicators:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_cross_reference(self, text):
        """Detect cross-reference patterns (very loose matching)"""
        cross_ref_patterns = [
            r'\b(see|refer|reference|check|view|go to|visit)\b',
            r'\b(above|below|earlier|later|previous|next)\b',
            r'\b(figure|fig|table|tbl|chart|diagram)\b.*\d',
            r'\b(section|sec|chapter|ch|appendix|app)\b.*\d',
            r'\b(page|pg|p\.)\s*\d',
            r'\d+\.\d+',  # Numbered sections like 3.1, 5.2
            r'\([^)]*\d[^)]*\)',  # Text in parentheses with numbers
        ]
        
        text_lower = text.lower()
        for pattern in cross_ref_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_navigation_text(self, text):
        """Detect navigation-related text"""
        nav_patterns = [
            r'\b(home|index|contents?|toc|menu)\b',
            r'\b(back|forward|next|previous|prev)\b',
            r'\b(top|bottom|up|down)\b',
            r'\b(first|last|begin|end|start|finish)\b',
            r'\b(return|go|navigate|jump)\b',
            r'^\s*(>|>>|<|<<|\|)\s*',  # Arrow-like symbols
        ]
        
        text_lower = text.lower()
        for pattern in nav_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_numbered_item(self, text):
        """Detect numbered items that could be clickable"""
        numbered_patterns = [
            r'^\d+\.',  # "1.", "2.", etc.
            r'^\d+\)',  # "1)", "2)", etc.
            r'^\(\d+\)',  # "(1)", "(2)", etc.
            r'^\d+\s+',  # "1 ", "2 ", etc. (with space)
            r'^\d+[a-z]\.',  # "1a.", "2b.", etc.
            r'^[a-z]\.',  # "a.", "b.", etc.
            r'^[A-Z]\.',  # "A.", "B.", etc.
            r'^\d+\.\d+',  # "1.1", "2.3", etc.
        ]
        
        for pattern in numbered_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _extract_internal_page_jumps(self, page, page_num):
        """Extract internal links that jump to other pages - SPECIFIC FOR PAGE JUMPING LINKS"""
        internal_jumps = []
        try:
            # Method 1: Look for destinations and bookmarks
            destinations = self._get_pdf_destinations()
            bookmarks = self._get_pdf_bookmarks()
            
            # Method 2: Analyze blue text and cross-reference with destinations
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            text = span.get("text", "").strip()
                            bbox = span.get("bbox", [])
                            
                            # Focus on blue text that could be page jumps
                            if color != 0 and text and self._is_blue_color(color):
                                # Check if this text matches any bookmark/destination
                                target_page = self._find_destination_page(text, destinations, bookmarks)
                                
                                if target_page:
                                    internal_jumps.append({
                                        'page': page_num,
                                        'type': 'internal_page_jump',
                                        'uri': f"jump_to_page_{target_page}",
                                        'text': text,
                                        'color': color,
                                        'bbox': bbox,
                                        'target_page': target_page
                                    })
                                    print(f"  PAGE_JUMP: '{text}' -> page {target_page} (color: {color})")
                                
                                # Also check if it's a generic page reference
                                elif self._is_page_reference_text(text):
                                    # Try to extract page number from text
                                    extracted_page = self._extract_page_number_from_text(text)
                                    if extracted_page and 1 <= extracted_page <= self.doc.page_count:
                                        internal_jumps.append({
                                            'page': page_num,
                                            'type': 'text_page_reference',
                                            'uri': f"text_ref_page_{extracted_page}",
                                            'text': text,
                                            'color': color,
                                            'bbox': bbox,
                                            'target_page': extracted_page
                                        })
                                        print(f"  TEXT_PAGE_REF: '{text}' -> page {extracted_page}")
                                    else:
                                        # Generic blue internal text
                                        internal_jumps.append({
                                            'page': page_num,
                                            'type': 'blue_internal_text',
                                            'uri': f"blue_internal:{text}",
                                            'text': text,
                                            'color': color,
                                            'bbox': bbox
                                        })
                                        print(f"  BLUE_INTERNAL: '{text}' (color: {color})")
                                        
        except Exception as e:
            print(f"  Error extracting internal page jumps: {e}")
        
        return internal_jumps
    
    def _get_pdf_destinations(self):
        """Get all named destinations in the PDF"""
        destinations = {}
        try:
            if hasattr(self.doc, 'resolve_names'):
                names = self.doc.resolve_names()
                if names:
                    for name, dest in names.items():
                        if isinstance(dest, list) and len(dest) > 0:
                            # Extract page number from destination
                            page_ref = dest[0]
                            if hasattr(page_ref, 'number'):
                                destinations[name] = page_ref.number + 1  # 0-based to 1-based
                            else:
                                # Try to resolve page reference
                                for i, page in enumerate(self.doc):
                                    if page.get_contents() == page_ref:
                                        destinations[name] = i + 1
                                        break
        except Exception as e:
            print(f"  Error getting destinations: {e}")
        
        return destinations
    
    def _get_pdf_bookmarks(self):
        """Get all bookmarks/outline items in the PDF"""
        bookmarks = {}
        try:
            toc = self.doc.get_toc()  # Table of contents
            for item in toc:
                level, title, page_num = item
                if page_num > 0:
                    bookmarks[title.strip()] = page_num
                    
        except Exception as e:
            print(f"  Error getting bookmarks: {e}")
        
        return bookmarks
    
    def _find_destination_page(self, text, destinations, bookmarks):
        """Find which page a text refers to based on destinations and bookmarks"""
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # Direct match in bookmarks (case insensitive)
        for bookmark_title, page_num in bookmarks.items():
            if bookmark_title.lower() == text_lower:
                return page_num
            # Partial match for longer titles
            if len(text_clean) > 10 and text_lower in bookmark_title.lower():
                return page_num
        
        # Direct match in destinations
        for dest_name, page_num in destinations.items():
            if dest_name.lower() == text_lower:
                return page_num
        
        # Check if text contains section numbers that match bookmarks
        for bookmark_title, page_num in bookmarks.items():
            # Extract numbers from both text and bookmark
            text_numbers = re.findall(r'\d+(?:\.\d+)*', text_clean)
            bookmark_numbers = re.findall(r'\d+(?:\.\d+)*', bookmark_title)
            
            if text_numbers and bookmark_numbers:
                if any(num in bookmark_numbers for num in text_numbers):
                    return page_num
        
        return None
    
    def _is_page_reference_text(self, text):
        """Check if text looks like a page reference"""
        page_ref_patterns = [
            r'\bpage\s+\d+\b',
            r'\bp\.\s*\d+\b',
            r'\bpg\.\s*\d+\b',
            r'^\d+(\.\d+)*\s+[A-Z]',  # "5.2 Something"
            r'\bsection\s+\d+',
            r'\bchapter\s+\d+',
            r'\bfigure\s+\d+',
            r'\btable\s+\d+',
        ]
        
        text_lower = text.lower()
        for pattern in page_ref_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _extract_page_number_from_text(self, text):
        """Extract page number from text like 'page 123' or 'see page 45'"""
        # Look for explicit page references
        page_match = re.search(r'\bpage\s+(\d+)\b', text.lower())
        if page_match:
            return int(page_match.group(1))
        
        # Look for p. or pg. references
        p_match = re.search(r'\bp\.?\s*(\d+)\b', text.lower())
        if p_match:
            return int(p_match.group(1))
        
        # Look for standalone numbers that could be page refs
        numbers = re.findall(r'\b(\d+)\b', text)
        for num_str in numbers:
            num = int(num_str)
            # Reasonable page number range
            if 1 <= num <= 1000:
                return num
        
        return None

    def match_with_markdown_files(self, all_links: Dict[int, List[Dict[str, Any]]], md_directory: str) -> Dict[str, Any]:
        """Match PDF links with corresponding Markdown files (page-wise if MD file names like 1_*.md)."""
        if not os.path.exists(md_directory):
            print(f"Markdown directory not found: {md_directory}")
            return {}

        print(f"\nMatching PDF links with Markdown files in: {md_directory}")

        # Collect markdown files
        md_files: List[str] = []
        for root, _dirs, files in os.walk(md_directory):
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    md_files.append(os.path.join(root, file))

        print(f"Found {len(md_files)} Markdown files")

        # Extract MD links and validate
        md_links = self._extract_markdown_links(md_files)
        md_validation = self._validate_markdown_files(md_files)

        # Page-wise matching
        matching_results = self._match_pdf_with_md_links(all_links, md_links)
        matching_results['markdown_validation'] = md_validation

        # Report
        self._generate_matching_report(matching_results, md_directory)
        return matching_results
    
    def _extract_markdown_links(self, md_files: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all links from Markdown files"""
        md_links = {}
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_links = []
                
                # Extract different types of markdown links
                
                # 1. Standard markdown links [text](url)
                standard_links = re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content)
                for match in standard_links:
                    text = match.group(1)
                    url = match.group(2)
                    file_links.append({
                        'type': 'markdown_standard',
                        'text': text,
                        'url': url,
                        'line': content[:match.start()].count('\n') + 1
                    })
                
                # 2. Reference links [text][ref] and [ref]: url
                ref_links = re.finditer(r'\[([^\]]*)\]\[([^\]]*)\]', content)
                ref_definitions = re.finditer(r'^\s*\[([^\]]+)\]:\s*(.+)$', content, re.MULTILINE)
                
                # Build reference mapping
                refs = {}
                for ref_def in ref_definitions:
                    ref_id = ref_def.group(1)
                    ref_url = ref_def.group(2).strip()
                    refs[ref_id] = ref_url
                
                for ref_link in ref_links:
                    text = ref_link.group(1)
                    ref_id = ref_link.group(2) or text  # If no ref_id, use text
                    if ref_id in refs:
                        file_links.append({
                            'type': 'markdown_reference',
                            'text': text,
                            'url': refs[ref_id],
                            'line': content[:ref_link.start()].count('\n') + 1
                        })
                
                # 3. Autolinks <url>
                autolinks = re.finditer(r'<(https?://[^>]+)>', content)
                for match in autolinks:
                    url = match.group(1)
                    file_links.append({
                        'type': 'markdown_autolink',
                        'text': url,
                        'url': url,
                        'line': content[:match.start()].count('\n') + 1
                    })
                
                # 4. Bare URLs (common in markdown)
                bare_urls = re.finditer(r'(?<![\[\(<])(https?://[^\s\)>\]]+)', content)
                for match in bare_urls:
                    url = match.group(1)
                    file_links.append({
                        'type': 'markdown_bare_url',
                        'text': url,
                        'url': url,
                        'line': content[:match.start()].count('\n') + 1
                    })
                
                # 5. HTML links in markdown
                html_links = re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', content, re.IGNORECASE)
                for match in html_links:
                    url = match.group(1)
                    text = match.group(2)
                    file_links.append({
                        'type': 'markdown_html_link',
                        'text': text,
                        'url': url,
                        'line': content[:match.start()].count('\n') + 1
                    })
                
                md_links[md_file] = file_links
                print(f"  {os.path.basename(md_file)}: {len(file_links)} links")
                
            except Exception as e:
                print(f"  Error reading {md_file}: {e}")
                md_links[md_file] = []
        
        return md_links
    
    def _match_pdf_with_md_links(self, pdf_links: Dict[int, List[Dict[str, Any]]], 
                                md_links: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Match PDF links with Markdown links"""
        # PAGE-WISE MATCHING ENHANCEMENT
        # 1. Flatten PDF links with page attribution already present
        all_pdf_links = []
        for page_num, links in pdf_links.items():
            for link in links:
                link['pdf_page'] = page_num
                all_pdf_links.append(link)

        # 2. Flatten MD links, capturing page number from filename prefix (e.g., 1_intro.md -> page 1)
        page_prefix_pattern = re.compile(r'^(\d+)_')
        all_md_links: List[Dict[str, Any]] = []
        md_indices_by_page: Dict[int, List[int]] = {}
        global_md_indices: List[int] = []  # Files without page prefix considered global/fallback

        for md_file, links in md_links.items():
            filename = os.path.basename(md_file)
            m = page_prefix_pattern.match(filename)
            md_page = int(m.group(1)) if m else None
            for link in links:
                link['md_file'] = md_file
                if md_page:
                    link['md_page'] = md_page
                all_md_links.append(link)
                idx = len(all_md_links) - 1
                if md_page:
                    md_indices_by_page.setdefault(md_page, []).append(idx)
                else:
                    global_md_indices.append(idx)

        print(f"\nMatching (page-wise) {len(all_pdf_links)} PDF links with {len(all_md_links)} MD links...")

        matching_results = {
            'matched_links': [],
            'pdf_only_links': [],
            'md_only_links': [],
            'statistics': {
                'total_pdf_links': len(all_pdf_links),
                'total_md_links': len(all_md_links),
                'matched_count': 0,
                'pdf_only_count': 0,
                'md_only_count': 0,
                'page_wise': {}
            }
        }

        matched_pdf_indices: set[int] = set()
        matched_md_indices: set[int] = set()

        def candidate_indices_for_page(page: int) -> List[int]:
            # Primary: page specific; Secondary fallback handled separately
            return md_indices_by_page.get(page, [])

        # Helper to attempt a strategy
        def attempt_match(strategy_name: str, comparator_func):
            for i, pdf_link in enumerate(all_pdf_links):
                if i in matched_pdf_indices:
                    continue
                pdf_page = pdf_link.get('pdf_page')
                primary_candidates = candidate_indices_for_page(pdf_page)
                found = False

                # Strategy among page-specific candidates first
                for j in primary_candidates:
                    if j in matched_md_indices:
                        continue
                    if comparator_func(pdf_link, all_md_links[j]):
                        matching_results['matched_links'].append({
                            'pdf_link': pdf_link,
                            'md_link': all_md_links[j],
                            'match_type': strategy_name + ('_page' if primary_candidates else ''),
                            'confidence': 'high' if strategy_name == 'exact_url' else 'medium'
                        })
                        matched_pdf_indices.add(i)
                        matched_md_indices.add(j)
                        found = True
                        break

                # Fallback to global (unscoped) MD links if not found and pdf not matched yet
                if not found:
                    for j, md_link in enumerate(all_md_links):
                        if j in matched_md_indices:
                            continue
                        # Skip page-specific links for other pages during fallback to avoid cross-page false positives until last resort
                        if md_link.get('md_page') and md_link.get('md_page') != pdf_page:
                            continue
                        if comparator_func(pdf_link, md_link):
                            matching_results['matched_links'].append({
                                'pdf_link': pdf_link,
                                'md_link': md_link,
                                'match_type': strategy_name + ('_fallback' if md_link.get('md_page') != pdf_page else ''),
                                'confidence': 'high' if strategy_name == 'exact_url' else 'medium'
                            })
                            matched_pdf_indices.add(i)
                            matched_md_indices.add(j)
                            break

        # Strategy 1: Exact URL
        def cmp_exact(pdf_link, md_link):
            pdf_url = self._normalize_url(pdf_link.get('uri', ''))
            md_url = self._normalize_url(md_link.get('url', ''))
            return bool(pdf_url) and pdf_url == md_url
        attempt_match('exact_url', cmp_exact)

        # Strategy 2: Domain match (external only)
        def cmp_domain(pdf_link, md_link):
            pdf_url = pdf_link.get('uri', '')
            if not self._is_external_url(pdf_url):
                return False
            md_url = md_link.get('url', '')
            pdf_domain = self._extract_domain(pdf_url)
            md_domain = self._extract_domain(md_url)
            return bool(pdf_domain) and pdf_domain == md_domain
        attempt_match('domain_match', cmp_domain)

        # Strategy 3: Text similarity
        def cmp_text(pdf_link, md_link):
            pdf_text = (pdf_link.get('text') or '').strip().lower()
            if len(pdf_text) < 3:
                return False
            md_text = (md_link.get('text') or '').strip().lower()
            return self._text_similarity(pdf_text, md_text) > 0.8
        attempt_match('text_similarity', cmp_text)

        # Collect unmatched
        for i, pdf_link in enumerate(all_pdf_links):
            if i not in matched_pdf_indices:
                matching_results['pdf_only_links'].append(pdf_link)
        for j, md_link in enumerate(all_md_links):
            if j not in matched_md_indices:
                matching_results['md_only_links'].append(md_link)

        # Statistics
        matching_results['statistics']['matched_count'] = len(matching_results['matched_links'])
        matching_results['statistics']['pdf_only_count'] = len(matching_results['pdf_only_links'])
        matching_results['statistics']['md_only_count'] = len(matching_results['md_only_links'])

        # Page-wise stats
        for pdf_link in all_pdf_links:
            page = pdf_link['pdf_page']
            stats = matching_results['statistics']['page_wise'].setdefault(page, {'pdf_links': 0, 'matched': 0})
            stats['pdf_links'] += 1
        for match in matching_results['matched_links']:
            page = match['pdf_link']['pdf_page']
            matching_results['statistics']['page_wise'][page]['matched'] += 1

        return matching_results
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        
        # Remove common prefixes/suffixes
        url = url.strip()
        
        # Handle different URL formats
        if url.startswith(('http://', 'https://')):
            return url.lower().rstrip('/')
        elif url.startswith('www.'):
            return f"https://{url.lower()}".rstrip('/')
        elif url.startswith('mailto:'):
            return url.lower()
        
        return url.lower()
    
    def _is_external_url(self, url: str) -> bool:
        """Check if URL is external"""
        return url.startswith(('http://', 'https://', 'www.', 'mailto:'))
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            if url.startswith('mailto:'):
                return url.split('@')[-1].split('?')[0]
            
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                else:
                    return ""
            
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity ratio"""
        if not text1 or not text2:
            return 0.0
        
        # Simple similarity based on common words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    # ------------------ NEW: Markdown Validation & Reporting ------------------
    def _validate_markdown_files(self, md_files: List[str]) -> Dict[str, Any]:
        """Validate markdown links ensuring <a href> and markdown links aren't empty '#' and anchors exist."""
        results: Dict[str, Any] = { 'files': {}, 'summary': { 'total_files': 0, 'total_links_checked': 0, 'invalid_count': 0, 'invalid_empty_anchor': 0, 'invalid_missing_target': 0 } }
        header_slug_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        id_attr_pattern = re.compile(r'id=["\']([^"\']+)["\']', re.IGNORECASE)
        html_link_pattern = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE)
        md_link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

        def slugify(text: str) -> str:
            t = text.strip().lower()
            t = re.sub(r'[\s]+', '-', t)
            t = re.sub(r'[^a-z0-9\-]', '', t)
            return t

        for md_file in md_files:
            file_result = { 'invalid_links': [], 'counts': { 'links_checked': 0, 'invalid': 0 } }
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Collect possible anchor targets
                header_slugs = set()
                for m in header_slug_pattern.finditer(content):
                    header_slugs.add(slugify(m.group(2)))
                id_attrs = set(a.group(1) for a in id_attr_pattern.finditer(content))
                all_targets = header_slugs.union(id_attrs)

                def validate_link(raw_url: str, line_no: int, link_text: str, source_type: str):
                    url = raw_url.strip()
                    file_result['counts']['links_checked'] += 1
                    if url == '#' or url == '' or url.lower() in {'# ', '#\t'}:
                        file_result['invalid_links'].append({ 'line': line_no, 'url': url, 'issue': 'empty_anchor', 'text': link_text, 'type': source_type })
                        file_result['counts']['invalid'] += 1
                        results['summary']['invalid_count'] += 1
                        results['summary']['invalid_empty_anchor'] += 1
                    elif url.startswith('#'):
                        anchor = url[1:].strip()
                        # Some MD generators slugify headers; compare slugified anchor too
                        anchor_slug = slugify(anchor)
                        if anchor not in all_targets and anchor_slug not in all_targets:
                            file_result['invalid_links'].append({ 'line': line_no, 'url': url, 'issue': 'missing_target', 'text': link_text, 'type': source_type })
                            file_result['counts']['invalid'] += 1
                            results['summary']['invalid_count'] += 1
                            results['summary']['invalid_missing_target'] += 1

                # Validate HTML links
                for m in html_link_pattern.finditer(content):
                    href = m.group(1)
                    text = m.group(2)
                    line_no = content[:m.start()].count('\n') + 1
                    validate_link(href, line_no, text, 'html_a')

                # Validate markdown standard links
                for m in md_link_pattern.finditer(content):
                    text = m.group(1)
                    href = m.group(2)
                    line_no = content[:m.start()].count('\n') + 1
                    validate_link(href, line_no, text, 'md_standard')

            except Exception as e:
                file_result['error'] = str(e)

            results['files'][md_file] = file_result
            results['summary']['total_files'] += 1
            results['summary']['total_links_checked'] += file_result['counts'].get('links_checked', 0)

        return results

    def _generate_matching_report(self, matching_results: Dict[str, Any], md_directory: str):
        """Generate HTML report for PDF<->MD matching and markdown validation."""
        try:
            report_path = os.path.join(md_directory, 'pdf_md_matching_report.html')
            stats = matching_results.get('statistics', {})
            md_validation = matching_results.get('markdown_validation', {})

            def esc(text: str) -> str:
                return (str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

            html = [
                '<!DOCTYPE html>',
                '<html><head><meta charset="utf-8"><title>PDF ↔ MD Matching Report</title>',
                '<style>body{font-family:Arial,Helvetica,sans-serif;margin:20px;}table{border-collapse:collapse;width:100%;margin-bottom:30px;}th,td{border:1px solid #ccc;padding:6px;font-size:12px;}th{background:#f0f0f0;}h2{margin-top:40px;} .ok{color:#2e7d32;} .warn{color:#d84315;} .bad{color:#c62828;font-weight:bold;} .mono{font-family:monospace;} .small{font-size:11px;color:#555;} </style>',
                '</head><body>',
                '<h1>PDF ↔ Markdown Matching Report</h1>',
                f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p><h2>Overall Statistics</h2>",
                '<table><tr><th>Metric</th><th>Value</th></tr>',
                f"<tr><td>Total PDF Links</td><td>{stats.get('total_pdf_links','')}</td></tr>",
                f"<tr><td>Total MD Links</td><td>{stats.get('total_md_links','')}</td></tr>",
                f"<tr><td>Matched</td><td>{stats.get('matched_count','')}</td></tr>",
                f"<tr><td>PDF Only</td><td>{stats.get('pdf_only_count','')}</td></tr>",
                f"<tr><td>MD Only</td><td>{stats.get('md_only_count','')}</td></tr>",
                '</table>'
            ]

            # Page-wise breakdown
            pw = stats.get('page_wise', {})
            if pw:
                html.append('<h2>Page-wise Matching</h2><table><tr><th>Page</th><th>PDF Links</th><th>Matched</th><th>Match %</th></tr>')
                for page in sorted(pw.keys()):
                    pdfc = pw[page]['pdf_links']
                    mc = pw[page]['matched']
                    pct = f"{(mc/pdfc*100):.1f}%" if pdfc else '0%'
                    html.append(f"<tr><td>{page}</td><td>{pdfc}</td><td>{mc}</td><td>{pct}</td></tr>")
                html.append('</table>')

            # Matched links table (limited)
            html.append('<h2>Sample Matched Links (first 200)</h2><table><tr><th>PDF Page</th><th>Match Type</th><th>PDF URI/Text</th><th>MD File</th><th>MD URL/Text</th></tr>')
            for m in matching_results.get('matched_links', [])[:200]:
                pdf_link = m['pdf_link']
                md_link = m['md_link']
                html.append('<tr>'
                            f"<td>{pdf_link.get('pdf_page')}</td>"
                            f"<td>{m.get('match_type')}</td>"
                            f"<td class='mono'>{esc(pdf_link.get('uri'))}<div class='small'>{esc(pdf_link.get('text'))}</div></td>"
                            f"<td>{esc(os.path.basename(md_link.get('md_file','')))}</td>"
                            f"<td class='mono'>{esc(md_link.get('url'))}<div class='small'>{esc(md_link.get('text'))}</div></td>"
                            '</tr>')
            html.append('</table>')

            # Markdown validation section
            val_summary = md_validation.get('summary', {})
            html.append('<h2>Markdown Link Validation</h2>')
            html.append('<table><tr><th>Total Files</th><th>Total Links Checked</th><th>Invalid Total</th><th>Empty #</th><th>Missing Target</th></tr>')
            html.append(f"<tr><td>{val_summary.get('total_files','')}</td><td>{val_summary.get('total_links_checked','')}</td><td>{val_summary.get('invalid_count','')}</td><td>{val_summary.get('invalid_empty_anchor','')}</td><td>{val_summary.get('invalid_missing_target','')}</td></tr></table>")

            # List invalid links (cap at 200)
            html.append('<h3>Invalid Links (max 200)</h3><table><tr><th>File</th><th>Line</th><th>Issue</th><th>Type</th><th>URL</th><th>Text</th></tr>')
            invalid_rows = 0
            for fpath, fdata in md_validation.get('files', {}).items():
                for inv in fdata.get('invalid_links', []):
                    if invalid_rows >= 200:
                        break
                    html.append('<tr>'
                                f"<td>{esc(os.path.basename(fpath))}</td>"
                                f"<td>{inv.get('line','')}</td>"
                                f"<td class='bad'>{esc(inv.get('issue'))}</td>"
                                f"<td>{esc(inv.get('type'))}</td>"
                                f"<td class='mono'>{esc(inv.get('url'))}</td>"
                                f"<td>{esc(inv.get('text'))}</td>"
                                '</tr>')
                    invalid_rows += 1
            html.append('</table>')

            html.append('</body></html>')

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(html))
            print(f"Matching report generated: {report_path}")
        except Exception as e:
            print(f"Failed to generate matching report: {e}")
def main():
    # Update these paths for your files
    PDF_PATH = r"path/to/your/document.pdf"
    
    if not os.path.exists(PDF_PATH):
        print(f"PDF file not found: {PDF_PATH}")
        return
    
    extractor = PDFLinkExtractor(PDF_PATH)
    
    if not extractor.open_pdf():
        return
    
    try:
        print("TESTING PAGE 1 FOR HYPERLINKS...")
        links = extractor.extract_page_links(1)
        
        if links:
            print(f"\nSUCCESS! Found {len(links)} links on page 1:")
            for link in links:
                print(f"  {link['type']}: {link['uri']}")
        else:
            print("No links found on page 1")
        
        # Also generate full report
        print("\nGenerating full report...")
        all_links = extractor.extract_all_links()
        extractor.generate_html_report(all_links)
            
    finally:
        extractor.close_pdf()

def main_with_markdown_matching():
    """Main function that includes Markdown matching functionality"""
    # Update these paths for your files
    PDF_PATH = r"path/to/your/document.pdf"
    MD_DIRECTORY = r"path/to/your/markdown/directory"  # Directory containing Markdown files
    
    if not os.path.exists(PDF_PATH):
        print(f"PDF file not found: {PDF_PATH}")
        return
    
    extractor = PDFLinkExtractor(PDF_PATH)
    
    if not extractor.open_pdf():
        return
    
    try:
        # Step 1: Extract all PDF links
        print("="*60)
        print("STEP 1: EXTRACTING PDF HYPERLINKS")
        print("="*60)
        all_links = extractor.extract_all_links()
        extractor.generate_html_report(all_links)
        
        # Step 2: Match with Markdown files
        if os.path.exists(MD_DIRECTORY):
            print(f"\n" + "="*60)
            print("STEP 2: MATCHING PDF LINKS WITH MARKDOWN FILES")
            print("="*60)
            
            matching_results = extractor.match_with_markdown_files(all_links, MD_DIRECTORY)
            
            # Show detailed matching summary
            stats = matching_results.get('statistics', {})
            print(f"\nMATCHING COMPLETE")
            print(f"   PDF Links: {stats.get('total_pdf_links', 0)}")
            print(f"   MD Links: {stats.get('total_md_links', 0)}")
            print(f"   Matched: {stats.get('matched_count', 0)} ({(stats.get('matched_count', 0) / max(stats.get('total_pdf_links', 1), 1)) * 100:.1f}%)")
            print(f"   PDF-Only: {stats.get('pdf_only_count', 0)}")
            print(f"   MD-Only: {stats.get('md_only_count', 0)}")
                
        else:
            print(f"\nMarkdown directory not found: {MD_DIRECTORY}")
            print("Skipping Markdown matching...")
            
    finally:
        extractor.close_pdf()

if __name__ == "__main__":
    # Use the enhanced version with Markdown matching
    main_with_markdown_matching()
