import os
import re
import hashlib
from collections import defaultdict
from bs4 import BeautifulSoup

# Configuration - Update these paths for your files
MD_FOLDER = r"path/to/your/markdown/folder"
XML_FOLDER = r"path/to/your/xml/folder"

def find_tables(md_text):
    # Detect Markdown tables more accurately
    lines = md_text.splitlines()
    tables = []
    i = 0
    while i < len(lines):
        if '|' in lines[i]:
            # Found potential table start
            table_lines = []
            # Collect consecutive lines with pipes
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            
            # A valid table needs at least 2 lines (header + separator)
            if len(table_lines) >= 2:
                table_text = '\n'.join(table_lines)
                tables.append(table_text)
        else:
            i += 1
    return tables

def verify_table_format(table_text):
    """
    Check for actual table formatting issues, not just presence of tables.
    Returns True if table is properly formatted, False if there are issues.
    """
    lines = table_text.strip().split('\n')
    if len(lines) < 2:
        return False
    
    # Check header row
    header = lines[0].strip()
    if not header.startswith('|') or not header.endswith('|'):
        return False
    
    # Check separator row (should contain dashes and colons only)
    separator = lines[1].strip()
    if not separator.startswith('|') or not separator.endswith('|'):
        return False
    
    # Separator should contain only |, -, :, and spaces
    separator_content = separator[1:-1]  # Remove outer pipes
    separator_parts = separator_content.split('|')
    
    for part in separator_parts:
        part = part.strip()
        if not re.match(r'^[-: ]+$', part):
            return False
        # Must contain at least one dash
        if '-' not in part:
            return False
    
    # Check that header and separator have same number of columns
    header_cols = len(header.split('|')) - 2  # Subtract 2 for outer pipes
    separator_cols = len(separator.split('|')) - 2
    
    if header_cols != separator_cols:
        return False
    
    # Check data rows (if any) have consistent column count
    for i in range(2, len(lines)):
        data_row = lines[i].strip()
        if data_row:  # Skip empty lines
            if not data_row.startswith('|') or not data_row.endswith('|'):
                return False
            data_cols = len(data_row.split('|')) - 2
            if data_cols != header_cols:
                return False
    
    return True

def get_parent_topic_reference(md_text):
    # Assume parent topic reference is a Markdown link at the end
    match = re.search(r'\[.+\]\(.+\.md\)\s*$', md_text.strip())
    return match.group(0) if match else None

def hash_content(md_text):
    # Hash content for uniqueness check (ignore whitespace)
    return hashlib.md5(md_text.strip().encode('utf-8')).hexdigest()

def verify_xml_metadata(xml_path, md_files):
    messages = []
    with open(xml_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')
    meta = soup.find('meta', {'name': 'tableContents'})
    if not meta:
        messages.append(f"Missing &lt;meta name='tableContents'&gt; in {os.path.basename(xml_path)}")
        return {'status': 'fail', 'messages': messages}
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', meta.text)
    missing = [md for _, md in md_links if md not in md_files]
    if missing:
        messages.append(f"Metadata references missing md files: {missing}")
        return {'status': 'fail', 'messages': messages}
    all_matched = True
    for heading, md_file in md_links:
        md_path = os.path.join(MD_FOLDER, md_file)
        if not os.path.exists(md_path):
            all_matched = False
            messages.append(f"Referenced file not found: {md_file}")
            continue
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        md_heading = None
        for line in md_content.splitlines():
            if line.strip().startswith('#'):
                md_heading = line.strip('#').strip()
                break
        if md_heading and md_heading != heading:
            messages.append(f"Heading mismatch in {md_file}: XML='{heading}' vs MD='{md_heading}'")
            all_matched = False
    if all_matched and not missing:
        return {'status': 'ok', 'messages': []}
    return {'status': 'fail', 'messages': messages}

def write_html_report(table_errors, repeated_refs, duplicate_files, xml_results, localized_results, output_path="verification_report.html"):
    html = """
    <html>
    <head>
        <title>Markdown & XML Verification Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
            h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 5px; }
            ul { background: #fff; padding: 15px 30px; border-radius: 8px; box-shadow: 0 2px 8px #eee; }
            li { margin-bottom: 8px; }
            .ok { color: #27ae60; }
            .fail { color: #c0392b; }
            .section { margin-bottom: 40px; }
        </style>
    </head>
    <body>
        <h1>Markdown & XML Verification Report</h1>
    """

    # XML Metadata Results
    html += '<div class="section"><h2>XML Metadata Verification</h2>'
    for xml_file, result in xml_results.items():
        if result['status'] == 'ok':
            html += f'<p class="ok"><b>{xml_file}:</b> All XML headings and referenced md files are present and match.</p>'
        else:
            html += f'<p class="fail"><b>{xml_file}:</b></p><ul>'
            for msg in result['messages']:
                html += f"<li>{msg}</li>"
            html += "</ul>"
    html += "</div>"

    # Localized Metadata Results
    html += '<div class="section"><h2>Localized Metadata Verification</h2>'
    for xml_file, result in localized_results.items():
        if result['status'] == 'ok':
            html += f'<p class="ok"><b>{xml_file}:</b> All localized metadata is present and valid.</p>'
        else:
            html += f'<p class="fail"><b>{xml_file}:</b></p><ul>'
            for msg in result['messages']:
                html += f"<li>{msg}</li>"
            html += "</ul>"
    html += "</div>"

    # Duplicate Content
    html += '<div class="section"><h2>Duplicate Content</h2>'
    if duplicate_files:
        html += "<ul>"
        for fname in duplicate_files:
            html += f"<li>{fname}</li>"
        html += "</ul>"
    else:
        html += '<p class="ok">No duplicate content detected.</p>'
    html += "</div>"

    # Table Errors
    html += '<div class="section"><h2>Table Format Errors</h2>'
    if table_errors:
        html += "<ul>"
        for fname, indices in table_errors.items():
            html += f"<li><b>{fname}</b>:  {len(indices)}</li>"
        html += "</ul>"
    else:
        html += '<p class="ok">No table format errors found.</p>'
    html += "</div>"

    # Repeated Parent Topic References
    html += '<div class="section"><h2>Repeated Parent Topic References</h2>'
    if repeated_refs:
        html += "<ul>"
        for ref in repeated_refs:
            html += f"<li>{ref}</li>"
        html += "</ul>"
    else:
        html += '<p class="ok">No repeated parent topic references found.</p>'
    html += "</div>"

    html += "</body></html>"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nHTML report written to {output_path}\n")

def verify_localized_metadata(xml_path, required_langs=None):
    messages = []
    found_langs = set()
    found_urls = set()
    if required_langs is None:
        required_langs = ["jp", "ko", "de", "es"]

    with open(xml_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')
    loc_meta = soup.find('localized_metadata')
    if not loc_meta:
        messages.append("Missing <localized_metadata> section.")
        return {'status': 'fail', 'messages': messages}

    for lang in loc_meta.find_all('language'):
        code = lang.get('code')
        if not code:
            messages.append("A <language> tag is missing the 'code' attribute.")
            continue
        if code in found_langs:
            messages.append(f"Duplicate language code: {code}")
        found_langs.add(code)

        alt = lang.find('meta', {'name': 'DC.alternative'})
        if not alt or not alt.text.strip():
            messages.append(f"Missing or empty DC.alternative for language '{code}'.")

        ref = lang.find('meta', {'name': 'DC.reference'})
        if not ref:
            messages.append(f"Missing DC.reference for language '{code}'.")
            continue
        url = ref.get('content', '').strip()
        if not url:
            messages.append(f"DC.reference for '{code}' missing 'content' attribute.")
        if url != ref.text.strip():
            messages.append(f"DC.reference content/text mismatch for '{code}'.")
        if not url.startswith("http"):
            messages.append(f"DC.reference for '{code}' is not a valid URL: {url}")
        if f"/{code}/" not in url:
            messages.append(f"DC.reference URL for '{code}' does not contain '/{code}/': {url}")
        if url in found_urls:
            messages.append(f"Duplicate DC.reference URL: {url}")
        found_urls.add(url)

    for req in required_langs:
        if req not in found_langs:
            messages.append(f"Missing required language: {req}")

    if not messages:
        return {'status': 'ok', 'messages': []}
    return {'status': 'fail', 'messages': messages}

def main():
    md_files = [f for f in os.listdir(MD_FOLDER) if f.endswith('.md')]
    content_hashes = set()
    parent_refs = set()
    repeated_refs = set()
    table_errors = {}
    duplicate_files = set()
    xml_results = {}
    localized_results = {}

    for md_file in md_files:
        path = os.path.join(MD_FOLDER, md_file)
        with open(path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Table detection and format verification
        tables = find_tables(md_text)
        invalid_tables = []
        for idx, table in enumerate(tables, 1):
            if not verify_table_format(table):
                invalid_tables.append(idx)
        
        # Only add to table_errors if there are actual formatting issues
        if invalid_tables:
            table_errors[md_file] = invalid_tables
        
        # Parent topic reference check
        ref = get_parent_topic_reference(md_text)
        if ref:
            if ref in parent_refs:
                repeated_refs.add(ref)
            parent_refs.add(ref)
        
        # Content uniqueness
        h = hash_content(md_text)
        if h in content_hashes:
            duplicate_files.add(md_file)
        content_hashes.add(h)

    # XML metadata verification
    xml_files = [f for f in os.listdir(XML_FOLDER) if f.endswith('.xml')]
    for xml_file in xml_files:
        xml_path = os.path.join(XML_FOLDER, xml_file)
        xml_results[xml_file] = verify_xml_metadata(xml_path, md_files)
        localized_results[xml_file] = verify_localized_metadata(xml_path)

    # Print results for table errors only
    if table_errors:
        print("\nFiles with table formatting ISSUES:\n")
        for fname, invalid_indices in table_errors.items():
            print(f"  {fname}: {len(invalid_indices)} table(s) with formatting issues")
    else:
        print("\nNo table formatting issues found.\n")

    # Write HTML report
    write_html_report(table_errors, repeated_refs, duplicate_files, xml_results, localized_results)

if __name__ == "__main__":
    main()