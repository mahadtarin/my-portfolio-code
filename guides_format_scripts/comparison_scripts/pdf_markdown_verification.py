from difflib import SequenceMatcher
import pdfplumber
import fitz  # PyMuPDF
import sys
import os
import re
import glob

def is_heading(span, threshold_size=12):
    return span["size"] >= threshold_size and "bold" in span["font"].lower()

def is_bullet_point(text):
    bullet_chars = ["•", "-", "–", "*", "·"]
    return text.strip().startswith(tuple(bullet_chars))

def is_purple(color):
    """
    Checks if the given color is purple.
    Args:
        color (tuple or int): RGB color tuple (R, G, B) or an integer.
    Returns:
        bool: True if the color is purple, False otherwise.
    """
    if not color:
        return False

    # Convert color to RGB tuple if it's an integer
    if isinstance(color, int):
        # Extract RGB values from the integer color
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        color = (r, g, b)

    r, g, b = color
    # Define thresholds for purple
    return r > 100 and b > 100 and g < 100  # High red and blue, low green
def remove_headers_and_footers(pdf_content):
    """
    Removes headers and footers from the extracted PDF content.
    Args:
        pdf_content (dict): A dictionary where keys are page numbers and values are the raw content of each page.
    Returns:
        dict: A dictionary with headers and footers removed from each page.
    """
    cleaned_content = {}

    for page_num, content in pdf_content.items():
        # Split the content into lines
        lines = content.split("\n")

        # Remove the first and last lines (common for headers and footers)
        if len(lines) > 2:
            lines = lines[1:-1]  # Remove the first and last lines

        # Rejoin the remaining lines
        cleaned_content[page_num] = "\n".join(lines).strip()

    return cleaned_content

def extract_pdf_content(pdf_path):
    """
    Extracts raw content from a PDF file and preprocesses it.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: A dictionary where keys are page numbers and values are the raw content of each page.
    """
    pdf_content = {}

    # Open the PDF file
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            # Extract text from the page
            page_text = page.get_text("text")  # Extract text in reading order
            # Preprocess the content to remove unwanted characters
            pdf_content[page_num + 1] = preprocess_content(page_text.strip())  # Store text by page number (1-based index)

    # Remove headers and footers
    pdf_content = remove_headers_and_footers(pdf_content)

    return pdf_content

def extract_markdown_content(md_folder):
    """
    Extracts and preprocesses content from Markdown files.
    Args:
        md_folder (str): Path to the folder containing Markdown files.
    Returns:
        dict: A dictionary where keys are page numbers and values are the preprocessed content of each file.
    """
    md_content_by_page = {}

    # Find all Markdown files in the folder
    md_files = glob.glob(os.path.join(md_folder, "*.md"))

    for md_file in md_files:
        # Extract the page number from the file name (e.g., "1_filename.md" -> page 1)
        base_name = os.path.basename(md_file)
        page_num = base_name.split("_")[0]  # Extract the part before the first "_"
        if page_num.isdigit():
            page_num = int(page_num)
            with open(md_file, "r", encoding="utf-8") as file:
                # Preprocess the content to remove unwanted characters
                md_content_by_page[page_num] = preprocess_content(file.read().strip())

    return md_content_by_page

def preprocess_content(content):
    """
    Preprocesses the content by removing unwanted characters like '|' and '---'.
    Args:
        content (str): The raw content to preprocess.
    Returns:
        str: The cleaned content.
    """
    # Remove '|' and '---' and replace multiple spaces with a single space
    cleaned_content = re.sub(r"[|]", "", content)  # Remove '|'
    cleaned_content = re.sub(r"-{2,}", "", cleaned_content)  # Remove '---' or longer dashes
    cleaned_content = re.sub(r"\s+", " ", cleaned_content).strip()  # Normalize spaces
    return cleaned_content

def normalize_pdf_content(pdf_content):
    """
    Processes the extracted PDF content, detects headings based on font size and color,
    and formats it with paragraphs.
    Args:
        pdf_content (dict): Dictionary where keys are page numbers and values are raw text strings.
    Returns:
        dict: A dictionary where keys are page numbers and values are the formatted content of each page.
    """
    formatted_content = {}

    for page_num, raw_text in pdf_content.items():
        # Split the raw text into lines
        lines = raw_text.split("\n")
        page_text = []

        for line in lines:
            line = line.strip()
            if line:  # Ignore empty lines
                page_text.append(line)

        # Combine the text into paragraphs
        content = "\n".join(page_text)

        # Normalize line breaks and extra spaces
        content = re.sub(r"\s+", " ", content)

        # Standardize bullet points (e.g., replace "•" with "-")
        content = re.sub(r"•", "-", content)

        # Split content into paragraphs
        paragraphs = re.split(r"\n{2,}", content)  # Split on double newlines or more
        formatted_paragraphs = "\n\n".join(paragraphs)

        # Store the formatted content for the page
        formatted_content[page_num] = formatted_paragraphs.strip()

    return formatted_content

def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio() * 100

def generate_diff_html(pdf_text, md_text):
    """
    Generates HTML highlighting differences between PDF and Markdown content at the word level.
    Args:
        pdf_text (str): Text content from the PDF file.
        md_text (str): Text content from the Markdown file.
    Returns:
        tuple: Two HTML strings with differences highlighted.
    """
    # Split the content into words for word-level comparison
    pdf_words = pdf_text.split()
    md_words = md_text.split()

    # Use SequenceMatcher to compare word lists
    diff = SequenceMatcher(None, pdf_words, md_words).get_opcodes()
    pdf_html = ""
    md_html = ""

    for tag, i1, i2, j1, j2 in diff:
        if tag == "replace":
            pdf_html += f'<span class="removed">{" ".join(pdf_words[i1:i2])}</span> '
            md_html += f'<span class="added">{" ".join(md_words[j1:j2])}</span> '
        elif tag == "delete":
            pdf_html += f'<span class="removed">{" ".join(pdf_words[i1:i2])}</span> '
        elif tag == "insert":
            md_html += f'<span class="added">{" ".join(md_words[j1:j2])}</span> '
        elif tag == "equal":
            pdf_html += f'<span class="unchanged">{" ".join(pdf_words[i1:i2])}</span> '
            md_html += f'<span class="unchanged">{" ".join(md_words[j1:j2])}</span> '

    return pdf_html.strip(), md_html.strip()

def compare_pdf_and_markdown_html(pdf_pages, md_content_by_page, threshold=90, report_threshold=70, html_file="comparison_report.html"):
    """
    Compares PDF and Markdown content and generates an HTML report.
    Args:
        pdf_pages (dict): Extracted PDF content by page.
        md_content_by_page (dict): Extracted Markdown content by page.
        threshold (int): Minimum similarity percentage for a confident match.
        report_threshold (int): Minimum similarity percentage to avoid being flagged.
        html_file (str): Path to the HTML report file.
    """
    low_similarity_pages = []  # To store pages with similarity below the report threshold

    with open(html_file, "w", encoding="utf-8") as html:
        # Write the HTML header
        html.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PDF to Markdown Comparison Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #555; }
                .low-similarity { color: red; font-weight: bold; }
                .high-similarity { color: green; font-weight: bold; }
                .content-section { margin-bottom: 20px; }
                .diff { margin: 10px 0; padding: 10px; border: 1px solid #ddd; background: #f4f4f4; }
                .removed { color: red; font-weight: bold; }
                .added { color: green; font-weight: bold; }
                .unchanged { color: black; }
                .pdf-content { color: blue; }
                .md-content { color: purple; }
            </style>
        </head>
        <body>
            <h1>PDF to Markdown Comparison Report</h1>
        """)

        for page_num, pdf_page_content in pdf_pages.items():
            html.write(f"<div class='content-section'><h2>Page {page_num}</h2>")

            # Get the corresponding Markdown content for this page
            md_page_content = md_content_by_page.get(page_num, None)

            if md_page_content is None:
                html.write("<p class='low-similarity'>No Markdown file found for this page.</p>")
                low_similarity_pages.append((page_num, 0))  # No match if Markdown file is missing
                html.write("</div>")
                continue

            # Calculate similarity percentage
            similarity = calculate_similarity(pdf_page_content, md_page_content)

            # Highlight similarity score
            if similarity < report_threshold:
                html.write(f"<p class='low-similarity'>Similarity: {similarity:.2f}%</p>")
                low_similarity_pages.append((page_num, similarity))
            else:
                html.write(f"<p class='high-similarity'>Similarity: {similarity:.2f}%</p>")

            # Highlight differences
            pdf_html, md_html = generate_diff_html(pdf_page_content, md_page_content)

            # Write PDF and Markdown content with differences highlighted
            html.write("<div class='diff'>")
            html.write("<h3>PDF Content:</h3>")
            html.write(f"<div class='pdf-content'>{pdf_html}</div>")
            html.write("<h3>Markdown Content:</h3>")
            html.write(f"<div class='md-content'>{md_html}</div>")
            html.write("</div></div>")

        # Write the summary section
        html.write("<h2>Summary</h2>")
        if low_similarity_pages:
            html.write("<p>Pages with similarity below the threshold:</p><ul>")
            for page_num, similarity in low_similarity_pages:
                html.write(f"<li>Page {page_num}: {similarity:.2f}% similarity</li>")
            html.write("</ul>")
        else:
            html.write("<p>All pages have similarity above the threshold.</p>")

        # Write the HTML footer
        html.write("</body></html>")

    print(f"Comparison results have been written to {html_file}")

# Ensure proper encoding for printing
sys.stdout.reconfigure(encoding='utf-8')
 
# Example usage
if __name__ == "__main__":
    # Update these paths for your files
    pdf_path = "path/to/your/document.pdf"
    md_folder = "path/to/your/markdown/folder"

    # Extract PDF content using the original function
    pdf_content = extract_pdf_content(pdf_path)

    pdf_content = normalize_pdf_content(pdf_content)

    # Extract Markdown content
    md_content_by_page = extract_markdown_content(md_folder)

    # Compare PDF and Markdown content
    compare_pdf_and_markdown_html(pdf_content, md_content_by_page)