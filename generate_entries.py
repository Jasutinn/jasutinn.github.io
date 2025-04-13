import os
import markdown
import pdfplumber
import docx
import json
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

# ========== CONFIGURATION ==========
JOURNAL_DIR = "journal"
OUTPUT_DIR = "public/journal"
ACCENT_COLOR = "#8B0000"  # Dark crimson for legal gravitas
PRIMARY_COLOR = "#00274D"  # Authoritative dark blue

# ========== FORMAL HTML TEMPLATE ==========
HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <meta name="description" content="Official political and legal memorandum">
    <meta name="author" content="Justine de La Torre">
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600&family=Martel:wght@700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Crimson Pro', serif;
            margin: 40px auto;
            max-width: 820px;
            background: #f9f9f9;
            color: #222;
            line-height: 1.8;
            font-size: 1.1em;
        }}
        
        header {{
            border-bottom: 3px solid {ACCENT_COLOR};
            padding: 2rem 0;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .document-title {{
            font-family: 'Martel', serif;
            font-size: 2.2rem;
            color: {PRIMARY_COLOR};
            letter-spacing: -0.5px;
            margin: 0;
            text-transform: uppercase;
        }}
        
        .section {{
            margin: 2.5rem 0;
            counter-increment: section;
        }}
        
        .section-title {{
            font-family: 'Martel', serif;
            color: {ACCENT_COLOR};
            border-bottom: 2px solid #ddd;
            padding-bottom: 0.5rem;
            font-size: 1.4rem;
            font-variant: small-caps;
            letter-spacing: 0.5px;
        }}
        
        footer {{
            margin-top: 3rem;
            padding: 1.5rem 0;
            border-top: 3px solid {ACCENT_COLOR};
            font-size: 0.9em;
            color: #666;
            text-align: center;
        }}
        
        .citation {{
            font-style: italic;
            color: #444;
            margin-left: 2em;
            border-left: 3px solid #ddd;
            padding-left: 1em;
        }}
        
        @media print {{
            body {{ max-width: none; }}
            header {{ page-break-after: avoid; }}
        }}
        
        @media (max-width: 768px) {{
            body {{ margin: 20px; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1 class="document-title">Political Memoranda</h1>
    </header>
    
    <article>
        {{content}}
    </article>
    
    <footer>
        <div>Issued: {{footer_date}}</div>
        <div style="margin-top: 0.5em;">© 2025 Justine de La Torre. All rights reserved.<br>
        This document constitutes privileged political analysis under Article IV of...</div>
    </footer>
</body>
</html>
"""

# ========== PROCESSING FUNCTIONS ==========
def convert_md_to_html(md_text):
    return markdown.markdown(md_text, extensions=['extra', 'smarty'])

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def enhance_legal_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Format section headings
    for h in soup.find_all(['h1', 'h2', 'h3']):
        h['class'] = 'section-title'
        wrapper = soup.new_tag('div', **{'class': 'section'})
        h.wrap(wrapper)
        
    # Format blockquotes as citations
    for bq in soup.find_all('blockquote'):
        bq['class'] = 'citation'
        
    return str(soup)

def process_journal_entries():
    try:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        entries = []
        
        for filename in sorted(os.listdir(JOURNAL_DIR), reverse=True):  # Newest first
            if not filename.lower().endswith(('.md', '.txt', '.pdf', '.docx')):
                continue

            try:
                base_name, ext = os.path.splitext(filename)
                file_path = os.path.join(JOURNAL_DIR, filename)
                
                # Extract title from filename (YYYY-MM-DD-Title)
                title_components = base_name.split('-')
                if len(title_components) > 3 and title_components[0].isdigit():
                    title = ' '.join(title_components[3:]).title()
                    doc_date = '-'.join(title_components[:3])
                else:
                    title = base_name.replace('_', ' ').title()
                    doc_date = datetime.now().strftime("%Y-%m-%d")

                # Process content
                if ext.lower() == '.md':
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = convert_md_to_html(f.read())
                elif ext.lower() == '.pdf':
                    content = extract_text_from_pdf(file_path)
                elif ext.lower() == '.docx':
                    doc = docx.Document(file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                else:  # .txt
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                formatted_html = HTML_TEMPLATE.format(
                    title=title,
                    content=enhance_legal_content(content),
                    footer_date=datetime.strptime(doc_date, "%Y-%m-%d").strftime("%B %d, %Y")
                )

                output_file = os.path.join(OUTPUT_DIR, f"{base_name}.html")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(formatted_html)

                entries.append({
                    "title": title,
                    "date": doc_date,
                    "path": f"journal/{base_name}.html"
                })
                logging.info(f"Processed: {filename}")

            except Exception as e:
                logging.error(f"Error processing {filename}: {str(e)}")
                continue

        # Generate professional index
        generate_index(entries)
        
    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        raise

def generate_index(entries):
    index_html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Political Memoranda Archive</title>
        <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600&family=Martel:wght@700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Crimson Pro', serif; max-width: 820px; margin: 2rem auto; }}
            .archives-header {{ 
                border-bottom: 3px solid {ACCENT_COLOR};
                padding-bottom: 1rem;
                margin-bottom: 2rem;
            }}
            .entry-list li {{ 
                margin: 1.2rem 0;
                padding-left: 1rem;
                border-left: 3px solid {PRIMARY_COLOR};
            }}
            .entry-date {{ 
                color: #666;
                font-size: 0.95em;
                display: block;
                margin-bottom: 0.3rem;
            }}
        </style>
    </head>
    <body>
        <div class="archives-header">
            <h1 style="font-family: 'Martel'; color: {PRIMARY_COLOR}; margin: 0;">
                ARCHIVES OF POLITICAL MEMORANDA
            </h1>
            <p style="margin-top: 0.5rem; color: #666;">Classified Level IV: Public Dissemination Authorized</p>
        </div>
        
        <ul class="entry-list">
            {"".join(f'''
            <li>
                <span class="entry-date">{e["date"]}</span>
                <a href="{e["path"]}" style="color: {ACCENT_COLOR}; text-decoration: none; font-weight: 600;">
                    {e["title"]}
                </a>
            </li>
            ''' for e in entries)}
        </ul>
    </body>
    </html>
    """
    
    with open(os.path.join("public", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    process_journal_entries()