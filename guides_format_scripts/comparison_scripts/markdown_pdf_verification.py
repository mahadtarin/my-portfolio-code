import os
import re
import fitz  # PyMuPDF
from markdown import markdown
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_md_content(md_folder):
    """
    Extracts text content from Markdown files, ignoring specific unwanted text and image references.
    Args:
        md_folder (str): Path to the folder containing Markdown files.
    Returns:
        dict: A dictionary where keys are file names and values are extracted text content.
    """
    md_content = {}

    for file_name in os.listdir(md_folder):
        if file_name.endswith(".md"):
            file_path = os.path.join(md_folder, file_name)
            with open(file_path, "r", encoding="utf-8") as md_file:
                raw_content = md_file.read()

                # Remove specific unwanted text (customize for your document format)
                raw_content = re.sub(r"authorinformation: .* audience:", "", raw_content, flags=re.IGNORECASE)

                # Remove image references (e.g., ![alt text](url))
                raw_content = re.sub(r"!\[.*?\]\(.*?\)", "", raw_content)

                # Convert Markdown to plain text using BeautifulSoup
                html_content = markdown(raw_content)
                soup = BeautifulSoup(html_content, "html.parser")
                text_content = soup.get_text(separator=" ").strip()

                # Preprocess the content to remove unwanted characters
                text_content = preprocess_content(text_content)

                # Store the extracted and cleaned text content
                md_content[file_name] = text_content

    return md_content

def preprocess_content(content):
    """
    Preprocesses the content by removing unwanted characters like '|' and '--'.
    Args:
        content (str): The raw content to preprocess.
    Returns:
        str: The cleaned content.
    """
    # Remove '|' and '--' and replace multiple spaces with a single space
    cleaned_content = re.sub(r"[|]", "", content)  # Remove '|'
    cleaned_content = re.sub(r"--+", "", cleaned_content)  # Remove '--'
    cleaned_content = re.sub(r"\s+", " ", cleaned_content).strip()  # Normalize spaces
    return cleaned_content

def extract_pdf_content(pdf_path):
    """
    Extracts text content from a PDF file and preprocesses it.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: A dictionary where keys are page numbers and values are extracted text content.
    """
    pdf_content = {}

    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]

            # Extract text content from the page
            text_content = page.get_text("text").strip()

            # Preprocess the content to remove unwanted characters
            text_content = preprocess_content(text_content)

            # Store the extracted and cleaned text content
            pdf_content[page_num + 1] = text_content

    return pdf_content


def find_best_pdf_match(md_text, pdf_content_dict, threshold=0.85):
    """
    Find the best matching PDF page for a given Markdown file based on content similarity.
    Args:
        md_text (str): Content of the Markdown file.
        pdf_content_dict (dict): Dictionary of PDF page numbers and their content.
        threshold (float): Minimum similarity score for a confident match.
    Returns:
        tuple: (best_match_page, similarity_score, confidence_level)
               - best_match_page: The page number of the best matching PDF page, or None if no match is found.
               - similarity_score: The similarity score of the best match.
               - confidence_level: "strict", "low", or "unmatched".
    """
    best_match_page = None
    highest_similarity = 0

    for page_num, pdf_text in pdf_content_dict.items():
        # Calculate cosine similarity between the Markdown text and the PDF page text
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit_transform([md_text, pdf_text])
        similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match_page = page_num

    # Determine confidence level
    if highest_similarity >= threshold:
        return best_match_page, highest_similarity, "strict"
    elif highest_similarity >= 0.75:  # Adjust for low-confidence matches
        return best_match_page, highest_similarity, "low"
    else:
        return None, highest_similarity, "unmatched"


def generate_diff_html(md_text, pdf_text):
    """
    Generates HTML highlighting differences between Markdown and PDF content.
    Args:
        md_text (str): Text content from the Markdown file.
        pdf_text (str): Text content from the PDF file.
    Returns:
        tuple: Two HTML strings with differences highlighted.
    """
    diff = SequenceMatcher(None, md_text, pdf_text).get_opcodes()
    old_html = ""
    new_html = ""

    for tag, i1, i2, j1, j2 in diff:
        if tag == "replace":
            old_html += f'<span class="old">{md_text[i1:i2]}</span>'
            new_html += f'<span class="new">{pdf_text[j1:j2]}</span>'
        elif tag == "delete":
            old_html += f'<span class="old">{md_text[i1:i2]}</span>'
        elif tag == "insert":
            new_html += f'<span class="new">{pdf_text[j1:j2]}</span>'
        elif tag == "equal":
            old_html += f'<span class="unchanged">{md_text[i1:i2]}</span>'
            new_html += f'<span class="unchanged">{pdf_text[j1:j2]}</span>'

    return old_html, new_html


def compare_md_and_pdf(md_content, pdf_content, html_file="comparison_report.html"):
    """
    Compares text content extracted from Markdown files and PDF files and generates an HTML report.
    Args:
        md_content (dict): Extracted text content from Markdown files.
        pdf_content (dict): Extracted text content from PDF files.
        html_file (str): Path to the HTML report file.
    """
    with open(html_file, "w", encoding="utf-8") as html:
        # Write the HTML header
        html.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Markdown to PDF Comparison Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #555; }
                .old { color: red; font-weight: bold; }
                .new { color: green; font-weight: bold; }
                .unchanged { color: black; }
                .file-section { margin-bottom: 20px; }
                .diff { margin: 10px 0; padding: 10px; border: 1px solid #ddd; background: #f4f4f4; }
            </style>
        </head>
        <body>
            <h1>Markdown to PDF Comparison Report</h1>
        """)

        for md_file, md_text in md_content.items():
            # Find the best matching PDF page
            best_match_page, similarity_score, confidence_level = find_best_pdf_match(md_text, pdf_content)

            # Get the corresponding PDF page content
            pdf_text = pdf_content.get(best_match_page, "")

            # Highlight differences
            old_html, new_html = generate_diff_html(md_text, pdf_text)

            # Write the file comparison section
            html.write(f"""
            <div class="file-section">
                <h2>File: {md_file} (Matched with: Page {best_match_page}, Similarity Score: {similarity_score:.2f}, Confidence: {confidence_level})</h2>
                <div class="diff">
                    <h3>Markdown Content:</h3>
                    <div>{old_html}</div>
                    <h3>PDF Content:</h3>
                    <div>{new_html}</div>
                </div>
            </div>
            """)

        # Write the HTML footer
        html.write("""
        </body>
        </html>
        """)

    print(f"Comparison complete. HTML report saved to {html_file}.")


# Example Usage
if __name__ == "__main__":
    # Update these paths for your files
    md_folder = "path/to/your/markdown/folder"
    pdf_path = "path/to/your/document.pdf"
    html_file = "comparison_report.html"

    # Extract content
    md_content = extract_md_content(md_folder)
    pdf_content = extract_pdf_content(pdf_path)

    # Compare and generate HTML report
    compare_md_and_pdf(md_content, pdf_content, html_file)