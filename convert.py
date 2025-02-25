import os
import json
from docx import Document

JOURNAL_FOLDER = "journal"
ENTRIES_FILE = "entries.json"

def convert_to_html(filename, content):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
</head>
<body>
    <h1>{filename}</h1>
    <p>{content.replace('\n', '<br>')}</p>
</body>
</html>"""
    
    with open(f"{JOURNAL_FOLDER}/{filename}.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def process_files():
    entries = []
    for file in os.listdir(JOURNAL_FOLDER):
        filepath = os.path.join(JOURNAL_FOLDER, file)
        filename, ext = os.path.splitext(file)
        
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            convert_to_html(filename, content)

        elif ext == ".docx":
            doc = Document(filepath)
            content = "\n".join([para.text for para in doc.paragraphs])
            convert_to_html(filename, content)
        
        if ext in [".txt", ".docx"]:
            entries.append(filename)

    with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f)

if __name__ == "__main__":
    process_files()