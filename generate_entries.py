import os
import markdown
import pdfplumber
import docx
from datetime import datetime
from bs4 import BeautifulSoup
import shutil

# ===== CONFIG =====
JOURNAL_DIR = "journal"
PUBLIC_DIR = "public"
OUTPUT_DIR = os.path.join(PUBLIC_DIR, "journal")
ENTRY_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #00274D; border-bottom: 2px solid #00274D; }}
        .content {{ margin: 20px 0; }}
        footer {{ color: #666; margin-top: 40px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="content">{content}</div>
    <footer>Generated on {date}</footer>
</body>
</html>
"""

def safe_convert(func, path):
    try:
        return func(path)
    except Exception as e:
        print(f"Error processing {path}: {str(e)}")
        return ""

def process_entries():
    # Clear existing output
    shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    entries = []
    
    for filename in os.listdir(JOURNAL_DIR):
        entry_path = os.path.join(JOURNAL_DIR, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.html")
        
        # Process content
        if filename.endswith(".md"):
            with open(entry_path, "r") as f:
                content = markdown.markdown(f.read())
        elif filename.endswith(".docx"):
            doc = docx.Document(entry_path)
            content = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith(".pdf"):
            content = ""
            with pdfplumber.open(entry_path) as pdf:
                for page in pdf.pages:
                    content += page.extract_text()
        else:
            continue
        
        # Save entry
        with open(output_path, "w") as f:
            f.write(ENTRY_TEMPLATE.format(
                title=base_name.replace("-", " ").title(),
                content=content,
                date=datetime.now().strftime("%Y-%m-%d")
            ))
        
        entries.append({
            "title": base_name.replace("-", " ").title(),
            "url": f"journal/{base_name}.html"
        })
    
    # Generate index
    with open(os.path.join(PUBLIC_DIR, "index.html"), "w") as f:
        f.write(f"""<!DOCTYPE html>
        <html>
        <head>
            <title>Political Memoranda</title>
            <style>
                body {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #00274D; }}
                ul {{ list-style: none; padding: 0; }}
                li {{ margin: 10px 0; }}
                a {{ color: #00274D; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>Political Memoranda</h1>
            <ul>
                {"".join(f'<li><a href="{e["url"]}">{e["title"]}</a></li>' for e in entries)}
            </ul>
        </body>
        </html>
        """)

if __name__ == "__main__":
    process_entries()