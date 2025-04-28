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
    font-weight: 400;
  }
  .container {
    max-width: 1000px;
    margin: 0 auto;
    background: white;
    padding: 45px;
    box-shadow: 0 3px 18px rgba(0,0,0,0.06);
    border-radius: 6px;
  }
  h1 {
    color: var(--navy);
    font-weight: 700;
    font-size: 2.6rem;
    margin: 0 0 45px 0;
    letter-spacing: -0.03em;
    border-bottom: 3px solid var(--gold);
    padding-bottom: 18px;
  }
  .section-header {
    padding: 28px;
    border-radius: 6px;
    margin-bottom: 35px;
    transition: transform 0.25s ease;
    background: linear-gradient(15deg, rgba(0,0,0,0.08), transparent);
  }
  .section-header:hover {
    transform: translateX(8px);
  }
  .section-header h2 {
    margin: 0;
    font-weight: 600;
    font-size: 1.5rem;
    letter-spacing: -0.01em;
    color: white !important;
    text-shadow: 0 2px 3px rgba(0,0,0,0.15);
  }
  .entry-list {
    list-style-type: none;
    padding: 0;
    margin-top: 35px;
  }
  .entry-item {
    margin-bottom: 25px;
    padding: 22px;
    background: #fff;
    border-left: 5px solid var(--gold);
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    border-radius: 4px;
  }
  pre {
    font-size: 1.1rem;
    line-height: 1.9;
    background: #FCFCFC;
    padding: 28px;
    border-radius: 5px;
    border: 1px solid rgba(0,0,0,0.08);
  }
  .back-link {
    font-size: 1.1rem;
    padding: 12px 28px;
    margin-top: 45px;
    letter-spacing: 0.03em;
  }
  @media (max-width: 768px) {
    body {
      padding: 25px;
      font-size: 1.05rem;
    }
    .container {
      padding: 30px;
    }
    h1 {
      font-size: 2.2rem;
    }
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

# Rest of the code remains identical to previous version
# [Include all other functions (generate_indexes, main) without changes]
# ... (refer to previous generate_entries.py for complete code)