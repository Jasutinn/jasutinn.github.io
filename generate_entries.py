import os
import string  # ← REQUIRED IMPORT ADDED HERE
import sys
import markdown
import pdfplumber
import docx
import logging
import shutil
from datetime import datetime
from pathlib import Path

# ===== CONSTANTS =====
JOURNAL_DIR = Path("journal")
PUBLIC_DIR = Path("public")
OUTPUT_DIR = PUBLIC_DIR / "journal"
ALLOWED_EXT = {'.md', '.docx', '.pdf', '.txt'}
SITE_TITLE = "Political Memoranda"

# ===== SAFE CHARACTER SET =====
SAFE_CHARS = set(f" -_.(){string.ascii_letters}{string.digits}")  # ← FIXED LINE

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler()
    ]
)

def sanitize_filename(name: str) -> str:
    """Convert to web-safe filename"""
    return "".join(c if c in SAFE_CHARS else '_' for c in name).strip('_')

def process_entry(file_path: Path) -> bool:
    """Process individual entry file"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return False

        clean_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{clean_name}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Content processing
        if file_path.suffix == '.md':
            content = markdown.markdown(file_path.read_text())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "\n".join(p.text for p in doc.paragraphs)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "\n".join(page.extract_text() for page in pdf.pages)
        else:
            content = file_path.read_text()

# In generate_entries.py - Professional Design Section

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Roboto:wght@300;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #00274D;
            --secondary: #8B0000;
            --accent: #5F5F5F;
            --background: #F8F9FA;
        }}

        body {{
            font-family: 'Libre Baskerville', serif;
            line-height: 1.8;
            max-width: 820px;
            margin: 2rem auto;
            padding: 0 20px;
            color: #222;
            background-color: var(--background);
        }}

        .letterhead {{
            border-bottom: 3px solid var(--primary);
            padding-bottom: 1rem;
            margin-bottom: 2.5rem;
            text-align: center;
        }}

        .letterhead h1 {{
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            font-size: 2.4rem;
            color: var(--primary);
            letter-spacing: -0.5px;
            margin: 0 0 0.5rem 0;
            text-transform: uppercase;
        }}

        .document-content {{
            font-size: 1.1rem;
            margin: 2rem 0;
        }}

        .document-content p {{
            margin: 1.2rem 0;
            text-align: justify;
        }}

        .document-footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--accent);
            color: var(--accent);
            font-size: 0.9rem;
            text-align: center;
        }}

        .legal-notice {{
            font-family: 'Roboto', sans-serif;
            font-size: 0.8rem;
            color: #666;
            margin-top: 2rem;
        }}

        @media print {{
            body {{ 
                max-width: none;
                font-size: 12pt;
                background: white;
            }}
            .document-footer {{ display: none; }}
        }}

        @media (max-width: 768px) {{
            body {{ margin: 1rem auto; }}
            .letterhead h1 {{ font-size: 1.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="letterhead">
        <h1>POLITICAL MEMORANDA</h1>
        <div class="legal-notice">
            CLASSIFIED LEVEL IV: PUBLIC DISSEMINATION AUTHORIZED
        </div>
    </div>

    <div class="document-content">
        <h2>{{title}}</h2>
        {{content}}
    </div>

    <div class="document-footer">
        <div>Issued: {{date}}</div>
        <div style="margin-top: 0.5rem;">Justine de La Torre | All Rights Reserved</div>
    </div>
</body>
</html>
"""

    INDEX_TEMPLATE = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Political Memoranda Archive</title>
        <style>
            :root {{
                --primary: #00274D;
                --secondary: #8B0000;
                --accent: #5F5F5F;
            }}
    
            body {{
                font-family: 'Libre Baskerville', serif;
                line-height: 1.8;
                max-width: 820px;
                margin: 3rem auto;
                padding: 0 20px;
                color: #222;
            }}
    
            .archive-header {{
                border-bottom: 3px solid var(--primary);
                padding-bottom: 1.5rem;
                margin-bottom: 2rem;
            }}
    
            .archive-title {{
                font-family: 'Roboto', sans-serif;
                font-size: 2.2rem;
                color: var(--primary);
                margin: 0;
                text-transform: uppercase;
                letter-spacing: -0.5px;
            }}
    
            .entry-list {{
                list-style: none;
                padding: 0;
                margin: 2rem 0;
            }}
    
            .entry-item {{
                margin: 1.5rem 0;
                padding: 1rem;
                background: white;
                border-left: 4px solid var(--secondary);
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: transform 0.2s;
            }}
    
            .entry-item:hover {{
                transform: translateX(5px);
            }}
    
            .entry-date {{
                font-family: 'Roboto', sans-serif;
                color: var(--accent);
                font-size: 0.9rem;
                font-weight: 500;
            }}
    
            .entry-title {{
                color: var(--primary);
                text-decoration: none;
                font-size: 1.1rem;
                display: block;
                margin-top: 0.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="archive-header">
            <h1 class="archive-title">ARCHIVES OF POLITICAL MEMORANDA</h1>
            <div class="legal-notice">Last Updated: {{date}}</div>
        </div>
    
        <ul class="entry-list">
            {"".join('''
            <li class="entry-item">
                <div class="entry-date">{entry_date}</div>
                <a href="journal/{filename}.html" class="entry-title">{title}</a>
            </li>
            ''' for entry in entries)}
        </ul>
    </body>
    </html>
    """
        
        output_path.write_text(html)
        return True

    except Exception as e:
        logging.error(f"Failed {file_path.name}: {str(e)}")
        return False

def generate_index():
    """Generate main index page"""
    try:
        entries = sorted(
            [f.stem for f in OUTPUT_DIR.glob('*.html')],
            key=lambda x: x.lower(),
            reverse=True
        )
        
        index_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{SITE_TITLE}</title>
            <style>
                body {{ 
                    font-family: 'Times New Roman', serif;
                    line-height: 1.8;
                    max-width: 680px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }}
                h1 {{ color: #00274D; border-bottom: 2px solid #00274D; }}
                .entry-list {{ list-style: none; padding: 0; }}
                .entry-item {{ margin: 1.2rem 0; padding-left: 1rem; }}
                .entry-link {{ color: #00274D; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>{SITE_TITLE}</h1>
            <ul class="entry-list">
                {"".join(f'<li class="entry-item"><a class="entry-link" href="journal/{e}.html">{e.replace("_", " ").title()}</a></li>' for e in entries)}
            </ul>
        </body>
        </html>
        """
        
        (PUBLIC_DIR / 'index.html').write_text(index_html)
        logging.info(f"Index generated with {len(entries)} entries")

    except Exception as e:
        logging.critical(f"Index generation failed: {str(e)}")
        sys.exit(1)

def main():
    """Main execution flow"""
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file() and process_entry(entry):
                success_count += 1

        if success_count == 0:
            logging.error("No valid entries processed!")
            sys.exit(1)

        generate_index()
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Deployment package ready")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()