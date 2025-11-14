#!/usr/bin/env python3
"""Extract PDF files to markdown format."""

import os
import sys
from pathlib import Path

try:
    import pypdf
except ImportError:
    print("Installing pypdf...")
    os.system(f"{sys.executable} -m pip install pypdf")
    import pypdf

def extract_pdf_to_markdown(pdf_path, output_path):
    """Extract text from PDF and save as markdown."""
    try:
        reader = pypdf.PdfReader(pdf_path)

        # Get PDF metadata
        metadata = reader.metadata
        title = metadata.get('/Title', '') if metadata else ''

        # Extract text from all pages
        text_content = []
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text.strip():
                text_content.append(f"## Page {page_num}\n\n{text}\n")

        # Create markdown content
        pdf_name = Path(pdf_path).stem
        markdown_content = f"# {pdf_name}\n\n"
        if title:
            markdown_content += f"**Title:** {title}\n\n"
        markdown_content += f"**Total Pages:** {len(reader.pages)}\n\n"
        markdown_content += "---\n\n"
        markdown_content += "\n".join(text_content)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return True, f"Extracted {len(reader.pages)} pages"
    except Exception as e:
        return False, str(e)

def main():
    source_dir = Path("Jane_Boyle_Expert_Witness_Orders_19")
    output_dir = Path("md_data")

    # Get all PDF files
    pdf_files = sorted(source_dir.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files to extract")
    print("-" * 60)

    success_count = 0
    failed_count = 0

    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.md"
        print(f"Processing: {pdf_file.name}...", end=" ")

        success, message = extract_pdf_to_markdown(pdf_file, output_file)

        if success:
            print(f"✓ {message}")
            success_count += 1
        else:
            print(f"✗ Failed: {message}")
            failed_count += 1

    print("-" * 60)
    print(f"Completed: {success_count} succeeded, {failed_count} failed")

if __name__ == "__main__":
    main()
