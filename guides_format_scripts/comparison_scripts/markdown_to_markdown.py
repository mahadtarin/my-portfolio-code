import os
import re
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_md_content(md_directory_path, is_old_variant=False):
    """Extract and clean content of all markdown files in a directory."""
    md_content_dict = {}
    for md_file in os.listdir(md_directory_path):
        if md_file.endswith('.md'):
            file_path = os.path.join(md_directory_path, md_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read().strip()
                cleaned_content = clean_md_content(md_content, is_old_variant=is_old_variant)
                md_content_dict[md_file] = cleaned_content
    return md_content_dict

def clean_md_content(md_content, is_old_variant=False):
    """
    Remove author info, image links, and internal/document links from markdown content.
    Keep the original language and text content intact.
    """
    lines = md_content.splitlines()
    cleaned_lines = []
    for idx, line in enumerate(lines):
        # Remove authorinformation line at the start for old variant
        if is_old_variant and idx == 0 and line.strip().lower().startswith("--- authorinformation:"):
            continue
        
        # Skip lines that are only image links
        if re.match(r'^\s*!\[.*?\]\(.*?\)\s*$', line):
            continue
        
        # Skip lines that are only document/internal links
        if re.match(r'^\s*\[.*?\]\(.*?\)\s*$', line):
            continue
        
        # Remove inline image links but keep surrounding text
        line = re.sub(r'!\[.*?\]\(.*?\)', '', line)
        
        # Remove inline links but keep the visible text (preserve the actual content)
        line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        
        # Only add non-empty lines after cleaning
        if line.strip():
            cleaned_lines.append(line)
    
    # Join lines and preserve original spacing/formatting
    cleaned = "\n".join(cleaned_lines)
    return cleaned

def extract_text_similarity(text1, text2):
    """Calculate cosine similarity between two texts."""
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    cos_sim = cosine_similarity(vectors)
    return cos_sim[0][1]

def find_matching_new_version_file(old_version_file_content, new_version_content_dict, strict_threshold=0.9, low_confidence_threshold=0.85):
    best_match = None
    highest_similarity = 0

    for new_version_file, new_version_content in new_version_content_dict.items():
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit_transform([old_version_file_content, new_version_content])
        similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = new_version_file

    # Determine confidence level
    if highest_similarity >= strict_threshold:
        return best_match, highest_similarity, "strict"
    elif highest_similarity >= low_confidence_threshold:
        return best_match, highest_similarity, "low"
    else:
        return None, highest_similarity, "unmatched"

def generate_grouped_diff(text1, text2):
    # Remove full stops at the end of sentences for comparison
    text1 = re.sub(r"\.\s*$", "", text1, flags=re.MULTILINE)
    text2 = re.sub(r"\.\s*$", "", text2, flags=re.MULTILINE)

    # Generate line-by-line differences
    diff = difflib.ndiff(text1.splitlines(), text2.splitlines())

    # Separate differences into old and new variants
    old_variant = []
    new_variant = []

    for line in diff:
        if line.startswith("- "):  # Old text
            old_variant.append(line[2:].strip())
        elif line.startswith("+ "):  # New text
            new_variant.append(line[2:].strip())

    return old_variant, new_variant

def generate_grouped_diff_html(text1, text2):
    # Split the texts into words
    words1 = text1.split()
    words2 = text2.split()

    # Use SequenceMatcher to compare words
    diff = difflib.SequenceMatcher(None, words1, words2).get_opcodes()
    old_html = ""
    new_html = ""

    for tag, i1, i2, j1, j2 in diff:
        if tag == "replace":
            old_html += f'<span class="old">{" ".join(words1[i1:i2])}</span> '
            new_html += f'<span class="new">{" ".join(words2[j1:j2])}</span> '
        elif tag == "delete":
            old_html += f'<span class="old">{" ".join(words1[i1:i2])}</span> '
        elif tag == "insert":
            new_html += f'<span class="new">{" ".join(words2[j1:j2])}</span> '
        elif tag == "equal":
            old_html += f'<span class="unchanged">{" ".join(words1[i1:i2])}</span> '
            new_html += f'<span class="unchanged">{" ".join(words2[j1:j2])}</span> '

    return old_html.strip(), new_html.strip()

def compare_markdown_files_html(old_version_dir, new_version_dir, log_dir, threshold=0.97):
    """
    Compare markdown files in new_version (older version) and old_version (new version) directories and generate an HTML report.
    Preserves original language content while keeping interface in English.
    """
    log_filename = os.path.join(log_dir, "markdown_comparison.html")

    num_matched = 0
    num_changed = 0
    changed_files = []
    skipped_in_old_version = []
    skipped_in_new_version = []

    # Use the improved extract_md_content with cleaning
    new_version_content_dict = extract_md_content(new_version_dir, is_old_variant=False)
    old_version_content_dict = extract_md_content(old_version_dir, is_old_variant=True)

    all_files_match = True

    # Use utf-8 encoding for the HTML file to preserve original languages
    with open(log_filename, 'w', encoding='utf-8') as html_file:
        html_file.write("""
        <html>
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Markdown Comparison Report</title>
        <style>
            body { 
                font-family: Arial, sans-serif, "Segoe UI", "Noto Sans", sans-serif; 
                margin: 20px; 
                line-height: 1.6;
            }
            .file-section { margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
            .diff { display: flex; gap: 40px; }
            .diff > div { width: 48%; }
            .old { background: #faa; color: #900; text-decoration: line-through; padding: 2px 4px; border-radius: 3px; }
            .new { background: #cfc; color: #060; padding: 2px 4px; border-radius: 3px; }
            .unchanged { color: #333; }
            .summary { border-top: 2px solid #333; margin-top: 40px; padding-top: 20px; }
            .content-box { 
                border: 1px solid #ddd; 
                padding: 15px; 
                border-radius: 5px; 
                background: #f9f9f9; 
                white-space: pre-wrap; 
                word-wrap: break-word;
                font-family: "Courier New", monospace;
            }
            .similarity-high { color: #27ae60; font-weight: bold; }
            .similarity-medium { color: #f39c12; font-weight: bold; }
            .similarity-low { color: #e74c3c; font-weight: bold; }
        </style>
        </head>
        <body>
        <h1>Markdown Comparison Report - Original Language Content Preserved</h1>
        """)

        new_version_files = set(new_version_content_dict.keys())
        old_version_files = set(old_version_content_dict.keys())

        # Check for matches from new_version to old_version
        for file_name, new_version_content in new_version_content_dict.items():
            # Find the best matching old_version file based on content similarity
            old_version_file_name, similarity_score, confidence_level = find_matching_new_version_file(
                new_version_content, old_version_content_dict
            )

            if confidence_level == "unmatched":
                skipped_in_new_version.append(file_name)
                all_files_match = False
                continue

            if confidence_level == "low":
                print(f"Low-confidence match: {file_name} -> {old_version_file_name} (Similarity: {similarity_score:.2f})")

            old_version_content = old_version_content_dict[old_version_file_name]
            old_html, new_html = generate_grouped_diff_html(old_version_content, new_version_content)

            # Increment the counter for matched files
            num_matched += 1

            # Check if the file has changes
            if similarity_score <= threshold:
                num_changed += 1
                changed_files.append(file_name)

            # Determine similarity class for styling
            similarity_class = "similarity-high" if similarity_score >= 0.95 else "similarity-medium" if similarity_score >= 0.85 else "similarity-low"

            # Write the file comparison section with preserved original language content
            html_file.write(f"""
            <div class="file-section">
                <h2>File: {file_name}</h2>
                <p><strong>Matched with:</strong> {old_version_file_name}</p>
                <p><strong>Similarity Score:</strong> <span class="{similarity_class}">{similarity_score:.4f}</span></p>
                <p><strong>Confidence:</strong> {confidence_level}</p>
                
                <div class="diff">
                    <div>
                        <h3>Old Version Content:</h3>
                        <div class="content-box">{old_html}</div>
                    </div>
                    <div>
                        <h3>New Version Content:</h3>
                        <div class="content-box">{new_html}</div>
                    </div>
                </div>
            </div>
            """)

        # Write the summary section in English
        html_file.write(f"""
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total matched files:</strong> {num_matched}</p>
            <p><strong>Total .md files with changes:</strong> {num_changed}</p>
            <p><strong>Skipped files in new version directory:</strong> {len(skipped_in_new_version)}</p>
            <p><strong>Skipped files in old version directory:</strong> {len(skipped_in_old_version)}</p>
        """)

        if changed_files:
            html_file.write("<h3>Files with content changes:</h3><ul>")
            for changed_file in changed_files:
                html_file.write(f"<li>{changed_file}</li>")
            html_file.write("</ul>")

        if skipped_in_new_version:
            html_file.write("<h3>Skipped files (Not present in old version directory):</h3><ul>")
            for skipped_file in skipped_in_new_version:
                html_file.write(f"<li>{skipped_file}</li>")
            html_file.write("</ul>")

        if skipped_in_old_version:
            html_file.write("<h3>Skipped files (Not present in new version directory):</h3><ul>")
            for skipped_file in skipped_in_old_version:
                html_file.write(f"<li>{skipped_file}</li>")
            html_file.write("</ul>")

        html_file.write("</div></body></html>")

    # Print summary in English
    print(f"\nTotal matched files: {num_matched}")
    print(f"Total .md files with changes: {num_changed}")
    print(f"Skipped files in new version directory: {len(skipped_in_new_version)}")
    print(f"Skipped files in old version directory: {len(skipped_in_old_version)}")
    print(f"\nComparison results have been saved to {log_filename}.")

    # Print only the files with real content edits in English
    print("\nFiles with real content edits:")
    for fname in changed_files:
        print(fname)

    return all_files_match


# Example usage
if __name__ == "__main__":
    # Update these paths for your files
    new_version_dir = 'path/to/your/new/markdown/folder'
    old_version_dir = 'path/to/your/old/markdown/folder'
    log_dir = 'path/to/output/reports'

    result = compare_markdown_files_html(old_version_dir, new_version_dir, log_dir)
    if result:
        print('Markdown files comparison is valid!')
    else:
        print('Markdown files comparison has errors!')
 