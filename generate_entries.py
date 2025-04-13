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

# ===== SHARED DESIGN SYSTEM =====
SHARED_CSS = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@450;600&family=Libre+Baskerville:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {PRIMARY_COLOR};
            --accent: {ACCENT_COLOR};
            --background: #F8F9FA;
        }}
        body {{
            font-family: 'Crimson Pro', serif;
            line-height: 1.78;
            max-width: 820px;
            margin: 3rem auto;
            padding: 0 2rem;
            color: #222;
            background-color: var(--background);
        }}
        .document-header {{
            border-bottom: 3px solid var(--primary);
            margin-bottom: 2.5rem;
            padding-bottom: 1rem;
        }}
        h1, h2 {{
            font-family: 'Libre Baskerville', serif;
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
            font-size: 0.9rem;
        }}
        .entry-meta {{
            font-family: 'Crimson Pro', sans-serif;
            color: #666;
            font-size: 0.9rem;
        }}
        @media (max-width: 768px) {{
            body {{ padding: 0 1rem; }}
            h1 {{ font-size: 2rem; }}
        }}
    </style>
"""

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
    safe_chars = set(f" -_.(){string.ascii_letters}{string.digits}")
    return "".join(c if c in safe_chars else '_' for c in name).strip('_')

def process_entry(file_path: Path) -> dict:
    """Process individual journal entry"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Process content
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

        # Generate entry HTML
        entry_html = f"""{SHARED_CSS}
</head>
<body>
    <div class="document-header">
        <h1>{SITE_TITLE}</h1>
        <div class="entry-meta">
            Document: {base_name.replace('_', ' ').title()} | 
            Effective: {datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d')}
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

        output_path.write_text(entry_html)
        return {
            "title": base_name.replace('_', ' ').title(),
            "filename": base_name,
            "date": datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d')
        }

    except Exception as e:
        logging.error(f"Failed {file_path.name}: {str(e)}")
        return None

def generate_index(entries: list):
    """Generate professional index page"""
    try:
        index_html = f"""{SHARED_CSS}
    <style>
        .entry-list {{
            list-style: none;
            padding: 0;
        }}
        .entry-item {{
            margin: 1.5rem 0;
            padding: 1.2rem;
            border-left: 4px solid var(--accent);
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }}
        .entry-item:hover {{
            transform: translateX(5px);
        }}
    </style>
</head>
<body>
    <div class="document-header">
        <h1>{SITE_TITLE} Archive</h1>
        <div class="entry-meta">
            Last Updated: {datetime.now().strftime('%Y-%m-%d')}
        </div>
    </div>
    
    <ul class="entry-list">
        {"".join(f'''
        <li class="entry-item">
            <div class="entry-meta">{{e["date"]}}</div>
            <h2><a href="journal/{{e["filename"]}}.html">{{e["title"]}}</a></h2>
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
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        entries = []
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file() and entry.suffix.lower() in ALLOWED_EXT:
                result = process_entry(entry)
                if result:
                    entries.append(result)

        if not entries:
            logging.error("No valid entries processed!")
            sys.exit(1)

        generate_index(sorted(entries, key=lambda x: x["date"], reverse=True))
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Deployment package ready")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()