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
LEGISLATIVE_DIR = Path("legislative")
PUBLIC_DIR = Path("public")
ALLOWED_EXT = {'.md', '.docx', '.pdf', '.txt'}
SITE_TITLE = "Political Memoranda"

SECTION_CONFIG = {
    'legislative': {
        'source': LEGISLATIVE_DIR,
        'public': PUBLIC_DIR / 'legislative',
        'title': 'My Legislative Agenda',
        'color': '#1A2B4D'
    },
    'journal': {
        'source': JOURNAL_DIR,
        'public': PUBLIC_DIR / 'journal',
        'title': 'Journal Archive',
        'color': '#333333',
        'subsections': {
            'personal': {'title': 'Personal Journal', 'color': '#4A4A4A'},
            'political': {'title': 'Political Journal', 'color': '#DC143C'},
            'legal': {'title': 'Legal Journal', 'color': '#2B4D7A'}
        }
    }
}

SHARED_CSS = """<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;600;700&display=swap" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<style>
  :root {
    --gold: #C5A47E;
    --navy: #1A2B4D;
    --cream: #F8F6F2;
    --text-primary: #2A2A2A;
  }
  body {
    font-family: 'Merriweather', serif;
    margin: 0;
    padding: 35px;
    background: var(--cream);
    line-height: 1.8;
    color: var(--text-primary);
  }
  .container {
    max-width: 1000px;
    margin: 0 auto;
    background: white;
    padding: 45px;
    box-shadow: 0 3px 18px rgba(0,0,0,0.06);
  }
  h1 {
    color: var(--navy);
    font-weight: 700;
    font-size: 2.4rem;
    margin-bottom: 40px;
    border-bottom: 3px solid var(--gold);
  }
  .section-header {
    padding: 25px;
    border-radius: 6px;
    margin-bottom: 30px;
    background: linear-gradient(15deg, rgba(0,0,0,0.08), transparent);
  }
  .section-header h2 {
    color: white !important;
    text-shadow: 0 2px 3px rgba(0,0,0,0.15);
    margin: 0;
    font-size: 1.4rem;
  }
  .entry-item {
    border-left: 4px solid var(--gold);
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
  }
  pre {
    background: #fafafa;
    padding: 25px;
    line-height: 1.7;
  }
</style>
"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    try:
        if file_path.suffix == '.html':
            return

        public_path = PUBLIC_DIR / section
        if subsection:
            public_path = public_path / subsection

        sanitized_name = sanitize_filename(file_path.stem) + '.html'
        output_path = public_path / sanitized_name

        content = ""
        if file_path.suffix == '.md':
            content = markdown.markdown(file_path.read_text())
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = '\n'.join([para.text for para in doc.paragraphs])
        elif file_path.suffix == '.txt':
            content = file_path.read_text()
        else:
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{sanitized_name}</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>{file_path.stem}</h1>
        <pre>{content}</pre>
        <a class="back-link" href="../index.html">← Back</a>
    </div>
</body>
</html>""")
        
    except Exception as e:
        logging.error(f"Failed to process {file_path}: {str(e)}")

def generate_indexes():
    try:
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

        # Main Index (Journal first)
        (PUBLIC_DIR / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>{SITE_TITLE}</h1>
        <div class="section-header" style="background: {SECTION_CONFIG['journal']['color']}">
            <h2><a href="journal/index.html">{SECTION_CONFIG['journal']['title']}</a></h2>
        </div>
        <div class="section-header" style="background: {SECTION_CONFIG['legislative']['color']}">
            <h2><a href="legislative/index.html">{SECTION_CONFIG['legislative']['title']}</a></h2>
        </div>
    </div>
</body>
</html>""")

        # Rest of original index generation code
        # ... (identical to your working version)

    except Exception as e:
        logging.critical(f"Index error: {str(e)}")
        sys.exit(1)

def main():
    logging.info("Starting content generation")
    generate_indexes()

    # Original processing logic
    # ... (identical to your working version)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('build.log'),
            logging.StreamHandler()
        ]
    )
    main()