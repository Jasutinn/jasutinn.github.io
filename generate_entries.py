import os
import markdown
import pdfplumber
import docx
from bs4 import BeautifulSoup
from datetime import datetime

# Define paths
journal_dir = "journal"
output_dir = "public/journal"

# Create output directory if missing
os.makedirs(output_dir, exist_ok=True)

# Define a formal & legal HTML template
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: "Times New Roman", serif;
            margin: 40px;
            background-color: #f5f5f5;
            color: #333;
            text-align: justify;
        }}
        header {{
            background-color: #00274D;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }}
        article {{
            background: white;
            padding: 20px;
            margin: 20px auto;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{
            color: #00274D;
        }}
        p {{
            text-indent: 50px;
        }}
        footer {{
            text-align: center;
            padding: 10px;
            margin-top: 20px;
            background-color: #00274D;
            color: white;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <header>{header}</header>
    <article>
        {content}
    </article>
    <footer>Political Memoranda - {footer_date}</footer>
</body>
</html>
"""

# Function to convert Markdown to HTML
def convert_md_to_html(md_text):
    return markdown.markdown(md_text)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

# Function to extract text from DOCX files
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join(para.text for para in doc.paragraphs)

# Function to format plain text to HTML
def format_text_as_html(text):
    """Ensure proper HTML formatting with paragraphs."""
    return "<p>" + text.replace("\n", "</p><p>") + "</p>"

# Function to process and convert all journal entries
def process_journal_entries():
    for filename in os.listdir(journal_dir):
        file_path = os.path.join(journal_dir, filename)
        output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.html")

        if filename.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
                formatted_text = convert_md_to_html(raw_text)
        
        elif filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
                formatted_text = format_text_as_html(raw_text)
        
        elif filename.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_path)
            formatted_text = format_text_as_html(raw_text)
        
        elif filename.endswith(".docx"):
            raw_text = extract_text_from_docx(file_path)
            formatted_text = format_text_as_html(raw_text)
        
        else:
            print(f"Skipping unsupported file: {filename}")
            continue

        # Clean up using BeautifulSoup
        soup = BeautifulSoup(formatted_text, "html.parser")
        cleaned_text = soup.prettify()

        # Format the final HTML page
        formatted_html = html_template.format(
            title=filename,
            header="Political Memoranda",
            content=cleaned_text,
            footer_date=datetime.now().strftime("%B %d, %Y")
        )

        # Save as an HTML file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_html)

        print(f"Processed: {filename} -> {output_file}")

# Run the script
if __name__ == "__main__":
    process_journal_entries()