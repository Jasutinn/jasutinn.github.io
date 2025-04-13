import os
import string
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
PRIMARY_COLOR = "#00274D"  # Official navy blue
ACCENT_COLOR = "#8B0000"   # Authority crimson

# ===== DESIGN SYSTEM =====
SAFE_CHARS = set(f" -_.(){string.ascii_letters}{string.digits}")

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler()
    ]
)

def sanitize_filename(name: str) -> str:
    """Create web-safe filenames"""
    return "".join(c if c in SAFE_CHARS else '_' for c in name).strip('_')

def process_entry(file_path: Path) -> dict:
    """Convert files to formatted entries"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        # Extract metadata
        base_name = sanitize_filename(file_path.stem)
        created_date = datetime.fromtimestamp(
            file_path.stat().st_ctime
        ).strftime("%Y-%m-%d")
        
        # Process content
        if file_path.suffix == '.md':
            content = markdown.markdown(file_path.read_text())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "\n".join(p.text for p in doc.paragraphs)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "\n".join(p.extract_text() for p in pdf.pages)
        else:
            content = file_path.read_text()

        # Generate entry HTML
        entry_html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{base_name.replace('_', ' ').title()}</title>
            <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@450;600&family=Libre+Baskerville:wght@700&display=swap" rel="stylesheet>
            <style>
                :root {{
                    --primary: {PRIMARY_COLOR};
                    --accent: {ACCENT_COLOR};
                }}
                body {{
                    font-family: 'Crimson Pro', serif;
                    line-height: 1.78;
                    max-width: 820px;
                    margin: 3rem auto;
                    padding: 0 2rem;
                    color: #222;
                }}
                .letterhead {{
                    border-bottom: 3px solid var(--primary);
                    margin-bottom: 2.5rem;
                    padding-bottom: 1rem;
                }}
                h1 {{
                    font-family: 'Libre Baskerville', serif;
                    font-size: 2.4rem;
                    color: var(--primary);
                    margin: 0 0 0.5rem 0;
                }}
                .document-content {{
                    font-size: 1.1rem;
                    text-align: justify;
                }}
                .document-footer {{
                    margin-top: 3rem;
                    padding-top: 1rem;
                    border-top: 1px solid #ddd;
                    color: #666;
                    text-align: center;
                }}
                @media (max-width: 768px) {{
                    body {{ padding: 0 1rem; }}
                    h1 {{ font-size: 2rem; }}
                }}
            </style>
        </head>
        <body>
            <div class="letterhead">
                <h1>{SITE_TITLE}</h1>
                <div class="document-meta">
                    <span>Classification: UNCLASSIFIED</span> | 
                    <span>Effective: {created_date}</span>
                </div>
            </div>
            
            <div class="document-content">
                {content}
            </div>
            
            <div class="document-footer">
                {SITE_TITLE} Digital Archive | Valid as of {datetime.now().strftime('%Y-%m-%d')}
            </div>
        </body>
        </html>
        """

        output_path = OUTPUT_DIR / f"{base_name}.html"
        output_path.write_text(entry_html)
        
        return {
            "title": base_name.replace('_', ' ').title(),
            "date": created_date,
            "filename": base_name
        }

    except Exception as e:
        logging.error(f"Processing failed: {file_path.name} - {str(e)}")
        return None

def generate_index(entries: list):
    """Create professional archive index"""
    try:
        index_html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{SITE_TITLE} Archive</title>
            <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@450;600&family=Libre+Baskerville:wght@700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary: {PRIMARY_COLOR};
                    --accent: {ACCENT_COLOR};
                }}
                body {{
                    font-family: 'Crimson Pro', serif;
                    line-height: 1.78;
                    max-width: 820px;
                    margin: 3rem auto;
                    padding: 0 2rem;
                    color: #222;
                }}
                .archive-header {{
                    border-bottom: 3px solid var(--primary);
                    margin-bottom: 2.5rem;
                    padding-bottom: 1rem;
                }}
                h1 {{
                    font-family: 'Libre Baskerville', serif;
                    font-size: 2.4rem;
                    color: var(--primary);
                    margin: 0 0 0.5rem 0;
                }}
                .entry-list {{
                    list-style: none;
                    padding: 0;
                }}
                .entry-item {{
                    margin: 1.5rem 0;
                    padding: 1.2rem;
                    border-left: 4px solid var(--accent);
                    background: #fff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    transition: transform 0.2s;
                }}
                .entry-item:hover {{
                    transform: translateX(5px);
                }}
                .entry-date {{
                    color: #666;
                    font-size: 0.9rem;
                }}
                .entry-title {{
                    color: var(--primary);
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="archive-header">
                <h1>{SITE_TITLE} Archive</h1>
                <div class="document-meta">
                    Last Updated: {datetime.now().strftime('%Y-%m-%d')}
                </div>
            </div>
            
            <ul class="entry-list">
                {"".join(f'''
                <li class="entry-item">
                    <div class="entry-date">{e["date"]}</div>
                    <a href="journal/{e["filename"]}.html" class="entry-title">
                        {e["title"]}
                    </a>
                </li>
                ''' for e in entries)}
            </ul>
        </body>
        </html>
        """
        
        (PUBLIC_DIR / 'index.html').write_text(index_html)
        logging.info("Professional index generated")

    except Exception as e:
        logging.critical(f"Index generation failed: {str(e)}")
        sys.exit(1)

def main():
    """Main execution flow"""
    try:
        # Clean environment
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Process entries
        entries = []
        for entry in sorted(JOURNAL_DIR.iterdir(), key=lambda x: x.stat().st_ctime, reverse=True):
            if entry.is_file():
                result = process_entry(entry)
                if result:
                    entries.append(result)

        if not entries:
            logging.error("No valid entries processed!")
            sys.exit(1)

        # Generate index
        generate_index(entries)
        
        # Add GitHub Pages requirements
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Deployment package ready")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()