import os
import markdown
import pdfplumber
import docx
from bs4 import BeautifulSoup
from datetime import datetime

journal_dir = "journal"
output_dir = "public/journal"
os.makedirs(output_dir, exist_ok=True)

html_template = """<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{title}</title>
<style>
body {{ font-family: 'Times New Roman', serif; margin: 40px; background-color: #f5f5f5; color: #333; }}
article {{ background: white; padding: 20px; max-width: 800px; margin: auto; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
h1 {{ color: #00274D; }}
p {{ text-indent: 50px; }}
footer {{ text-align: center; margin-top: 40px; font-size: 14px; color: gray; }}
</style>
</head>
<body>
<article>
<h1>{header}</h1>
{content}
<footer>{footer_date}</footer>
</article>
</body>
</html>
"""

def extract_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_docx(path):
    return "\n".join([para.text for para in docx.Document(path).paragraphs])

def process_entries():
    entries = []
    for file in os.listdir(journal_dir):
        name, ext = os.path.splitext(file)
        file_path = os.path.join(journal_dir, file)
        output_file = os.path.join(output_dir, f"{name}.html")

        if ext == ".md":
            with open(file_path, encoding="utf-8") as f:
                html = markdown.markdown(f.read())
        elif ext == ".txt":
            with open(file_path, encoding="utf-8") as f:
                html = "<p>" + f.read().replace("\n", "</p><p>") + "</p>"
        elif ext == ".pdf":
            html = "<p>" + extract_pdf(file_path).replace("\n", "</p><p>") + "</p>"
        elif ext == ".docx":
            html = "<p>" + extract_docx(file_path).replace("\n", "</p><p>") + "</p>"
        else:
            continue

        soup = BeautifulSoup(html, "html.parser")
        cleaned = soup.prettify()
        final_html = html_template.format(
            title=name,
            header="Memorandum Entry",
            content=cleaned,
            footer_date=datetime.now().strftime("%B %d, %Y")
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
        entries.append(f"{name}.html")

    with open("public/journal/entries.json", "w", encoding="utf-8") as f:
        f.write(str([entry for entry in entries]))

if __name__ == "__main__":
    process_entries()
