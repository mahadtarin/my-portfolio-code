import os
import re
import difflib
import sys
sys.stdout.reconfigure(encoding='utf-8')

def extract_text_from_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract code blocks first (to prevent conflicts with inline code)
    block_matches = re.findall(r'```(?:\w+\n)?([\s\S]*?)```', content)

    # Extract inline code ensuring it does not span multiple lines
    inline_matches = re.findall(r'`([^`\n]+)`', content)

    # Filter out empty or purely whitespace matches
    filtered_inline = [text.strip() for text in inline_matches if text.strip()]
    filtered_block = [text.strip() for text in block_matches if text.strip()]

    return filtered_inline + filtered_block


def get_matching_files(source_folder, translated_folder):
    source_files = {f: os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith(".md")}
    translated_files = {f: os.path.join(translated_folder, f) for f in os.listdir(translated_folder) if f.endswith(".md")}
    
    matched_pairs = []
    for src_file in source_files:
        prefix = src_file.split("_")[0]  # Extract prefix
        for trans_file in translated_files:
            if trans_file.startswith(prefix + "_"):
                matched_pairs.append((source_files[src_file], translated_files[trans_file]))
                break
    
    return matched_pairs

def compute_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def generate_comparison_report(source_folder, translated_folder, output_file):
    matched_pairs = get_matching_files(source_folder, translated_folder)
    
    with open(output_file, "w", encoding="utf-8") as report:
        for source_path, translated_path in matched_pairs:
            source_text = "\n".join(extract_text_from_markdown(source_path))
            translated_text = "\n".join(extract_text_from_markdown(translated_path))
            similarity = compute_similarity(source_text, translated_text) * 100
            
            if similarity < 100:
                report.write(f"Slide {os.path.basename(source_path)} ({similarity:.2f}% similarity):\n")
                report.write("Source content:\n------------------------\n")
                report.write(source_text + "\n")
                report.write("------------------------\nTranslated content:\n------------------------\n")
                report.write(translated_text + "\n")
                report.write("------------------------\n\n")

if __name__ == "__main__":
    # Update these paths for your files
    source_folder = "path/to/your/source/markdown/folder"
    translated_folder = "path/to/your/translated/markdown/folder"
    output_file = "codeblocks_comparison_report.txt"
    
    if os.path.isdir(source_folder) and os.path.isdir(translated_folder):
        generate_comparison_report(source_folder, translated_folder, output_file)
        print(f"Report generated: {output_file}")
    else:
        print("Invalid folder path(s). Make sure both source and translated folders exist.")
