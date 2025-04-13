import os
import markdown
import pdfplumber
import docx
import json
from datetime import datetime
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Paths
journal_dir = "journal"
output_dir = "public/journal"
os.makedirs(output_dir, exist_ok=True)

# HTML Template (unchanged from your original)
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

def convert_md_to_html(md_text):
    return markdown.markdown(md_text)

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join(para.text for para in doc.paragraphs)

def format_text_as_html(text):
    return "<p>" + text.replace("\n", "</p><p>") + "</p>"

def process_journal_entries():
    entries = []
    
    for filename in os.listdir(journal_dir):
        try:
            if not filename.lower().endswith(('.md', '.txt', '.pdf', '.docx')):
                continue

            base_name = os.path.splitext(filename)[0]
            title_parts = base_name.split('-')[3:]  # Skip date parts (YYYY-MM-DD-)
            title = ' '.join(title_parts).title() if title_parts else "Untitled Entry"
            
            file_path = os.path.join(journal_dir, filename)
            output_file = os.path.join(output_dir, f"{base_name}.html")

            # File processing (unchanged from your original)
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

            soup = BeautifulSoup(formatted_text, "html.parser")
            cleaned_text = soup.prettify()

            formatted_html = html_template.format(
                title=title,
                header="Political Memoranda",
                content=cleaned_text,
                footer_date=datetime.now().strftime("%B %d, %Y")
            )

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted_html)

            entries.append({
                "title": title,
                "path": f"journal/{base_name}.html"
            })
            logging.info(f"Processed: {filename}")

        except Exception as e:
            logging.error(f"Failed to process {filename}: {str(e)}")
            continue

    # Generate index.html
    index_html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Political Memoranda</title>
        <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Merriweather', serif;
                margin: 40px;
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.8;
            }}
            #search {{
                width: 100%;
                padding: 12px;
                margin: 20px 0;
                border: 1px solid #00274D;
                border-radius: 4px;
                font-size: 16px;
            }}
            @media (max-width: 768px) {{
                body {{ margin: 10px; }}
                article {{ padding: 10px; }}
            }}
            /* Your original CSS remains below */
            header {{ background-color: #00274D; color: white; padding: 20px; text-align: center; }}
            article {{ background: white; padding: 20px; margin: 20px auto; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 800px; }}
        </style>
    </head>
    <body>
        <header>Political Memoranda</header>
        <article>
            <h2>Official Compendium of Political and Legal Memoranda</h2>
            <p>This is a collection of my political thoughts, legal insights, and journal entries related to governance, law, and human rights.</p>
            <p>Browse the latest entries below:</p>
            <input type="text" id="search" placeholder="Search entries...">
            <ul id="entries-list">
                {"".join(f'<li><a href="{e["path"]}">{e["title"]}</a></li>' for e in entries)}
            </ul>
        </article>
        <footer>&copy; 2025 Justine de La Torre | All Rights Reserved</footer>
        <script>
            const entries = {json.dumps(entries)};
            document.getElementById('search').addEventListener('input', (e) => {{
                const term = e.target.value.toLowerCase();
                const filtered = entries.filter(entry => 
                    entry.title.toLowerCase().includes(term)
                );
                document.getElementById('entries-list').innerHTML = 
                    filtered.map(entry => `<li><a href="${{entry.path}}">${{entry.title}}</a></li>`).join('');
            }});
        </script>
    </body>
    </html>
    """

    with open(os.path.join("public", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    process_journal_entries()