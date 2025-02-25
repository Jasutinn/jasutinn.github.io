import os
import json
import markdown
import pdfplumber
from bs4 import BeautifulSoup
from docx import Document

# Directory containing journal entries
journal_dir = "journal"
output_file = os.path.join(journal_dir, "entries.json")

# Function to read .txt files
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Function to read .md files and convert to HTML
def read_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())

# Function to read .html files
def read_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()  # No need to convert, already HTML

# Function to read .pdf files
def read_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# Function to read .docx (Word) files
def read_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Process files
entries = []
if not os.path.exists(journal_dir):
    os.makedirs(journal_dir)

for filename in os.listdir(journal_dir):
    if filename == "entries.json":
        continue  # Skip the JSON file itself

    file_path = os.path.join(journal_dir, filename)
    entry = {"title": filename, "content": ""}

    if filename.endswith(".txt"):
        entry["content"] = read_txt(file_path)
    elif filename.endswith(".md"):
        entry["content"] = read_md(file_path)
    elif filename.endswith(".html"):
        entry["content"] = read_html(file_path)
    elif filename.endswith(".pdf"):
        entry["content"] = read_pdf(file_path)
    elif filename.endswith(".docx"):
        entry["content"] = read_docx(file_path)

    entries.append(entry)

# Save to JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=4, ensure_ascii=False)

print("✅ Entries JSON generated successfully!")