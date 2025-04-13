import os
import markdown
import pdfplumber
import docx
from datetime import datetime
from bs4 import BeautifulSoup
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Constants
JOURNAL_DIR = "journal"
PUBLIC_DIR = "public"
OUTPUT_DIR = os.path.join(PUBLIC_DIR, "journal")
SITE_TITLE = "Political Memoranda"
PRIMARY_COLOR = "#00274D"
ACCENT_COLOR = "#8B0000"

# Professional HTML Template
HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        :root {{
            --primary: {PRIMARY_COLOR};
            --accent: {ACCENT_COLOR};
        }}
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 680px;
            margin: 2rem auto;
            padding: 0 1rem;
            color: #333;
        }}
        h1 {{
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
            padding-bottom: 0.5rem;
            margin-bottom: 2rem;
            font-size: 2.2rem;
        }}
        .content {{
            margin: 2rem 0;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            color: #666;
            border-top: 1px solid #ddd;
            text-align: center;
        }}
        @media (max-width: 480px) {{
            body {{ margin: 1rem auto; }}
            h1 {{ font-size: 1.8rem; }}
        }}
    </style>
</head>
<body>
    <h1>{{title}}</h1>
    <div class="content">{{content}}</div>
    <footer>
        {SITE_TITLE} - {{date}}<br>
        Official digital repository - All rights reserved
    </footer>
</body>
</html>
"""

def process_entry(filename):
    """Process individual journal entry"""
    try:
        base_name = os.path.splitext(filename)[0]
        title = ' '.join(base_name.split('-')).title()
        input_path = os.path.join(JOURNAL_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.html")

        # Process different file types
        if filename.endswith(".md"):
            with open(input_path, "r", encoding="utf-8") as f:
                content = markdown.markdown(f.read(), extensions=['extra'])
        elif filename.endswith(".docx"):
            doc = docx.Document(input_path)
            content = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith(".pdf"):
            content = ""
            with pdfplumber.open(input_path) as pdf:
                for page in pdf.pages:
                    content += page.extract_text() or ""
        else:
            return None

        # Generate HTML with consistent styling
        formatted_html = HTML_TEMPLATE.format(
            title=title,
            content=content,
            date=datetime.now().strftime("%B %d, %Y")
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_html)

        logging.info(f"Processed: {filename}")
        return base_name

    except Exception as e:
        logging.error(f"Failed to process {filename}: {str(e)}")
        return None

def generate_index(entries):
    """Generate professional index page"""
    index_html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{SITE_TITLE}</title>
        <style>
            body {{ 
                font-family: 'Georgia', serif;
                line-height: 1.8;
                max-width: 680px;
                margin: 2rem auto;
                padding: 0 1rem;
                color: #333;
            }}
            h1 {{ 
                color: var(--primary);
                border-bottom: 2px solid var(--primary);
                padding-bottom: 0.5rem;
                margin-bottom: 2rem;
                font-size: 2.2rem;
            }}
            .entry-list {{
                list-style: none;
                padding: 0;
            }}
            .entry-item {{
                margin: 1.2rem 0;
                padding-left: 1rem;
                border-left: 3px solid var(--accent);
                transition: transform 0.2s;
            }}
            .entry-item:hover {{
                transform: translateX(5px);
            }}
            .entry-link {{
                color: var(--primary);
                text-decoration: none;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <h1>{SITE_TITLE}</h1>
        <ul class="entry-list">
            {"".join(
                f'<li class="entry-item"><a class="entry-link" href="journal/{e}.html">{e.replace("-", " ").title()}</a></li>'
                for e in entries if e
            )}
        </ul>
    </body>
    </html>
    """

    with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    logging.info("Index generated successfully")

def main():
    """Main processing function"""
    # Clean existing files
    shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Process all entries
    entries = []
    for filename in sorted(os.listdir(JOURNAL_DIR), reverse=True):
        if filename.startswith('.'):
            continue
        result = process_entry(filename)
        if result:
            entries.append(result)

    # Generate index
    generate_index(entries)
    logging.info("Site generation completed successfully")

if __name__ == "__main__":
    main()