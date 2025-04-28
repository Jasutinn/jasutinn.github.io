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

SHARED_CSS = """<link href="https://fonts.googleapis.com/css2?family=Merriweather&display=swap" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<style>
  :root {
    --gold: #C5A47E;
    --navy: #1A2B4D;
    --cream: #F5F3EF;
  }
  body { 
    font-family: 'Merriweather', serif; 
    margin: 0; 
    padding: 30px; 
    background: var(--cream);
    line-height: 1.6;
    color: #333;
  }
  .container { 
    max-width: 1000px; 
    margin: 0 auto;
    background: white;
    padding: 30px;
    box-shadow: 0 2px 15px rgba(0,0,0,0.1);
    border-radius: 4px;
  }
  .section-header {
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 30px;
    transition: transform 0.2s;
    border: 1px solid rgba(0,0,0,0.1);
  }
  .section-header:hover {
    transform: translateX(5px);
  }
  .section-header h2 {
    margin: 0;
    font-weight: 600;
    letter-spacing: -0.03em;
    color: white !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  }
  .entry-list {
    list-style-type: none;
    padding: 0;
    margin-top: 25px;
  }
  .entry-item {
    margin-bottom: 15px;
    padding: 15px;
    background: #fff;
    border-left: 4px solid var(--gold);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  a { 
    text-decoration: none; 
    color: var(--navy);
    border-bottom: 1px dotted transparent;
  }
  a:hover {
    border-bottom-color: var(--gold);
  }
  .back-link {
    display: inline-block;
    margin-top: 30px;
    padding: 8px 20px;
    background: var(--navy);
    color: white !important;
    border-radius: 3px;
    font-weight: 500;
  }
  .back-link:hover {
    background: var(--gold);
  }
  h1 {
    color: var(--navy);
    border-bottom: 2px solid var(--gold);
    padding-bottom: 10px;
    margin-bottom: 30px;
    font-size: 2.2em;
  }
  pre {
    white-space: pre-wrap;
    font-family: 'Merriweather', serif;
    background: #f8f8f8;
    padding: 20px;
    border-radius: 3px;
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

        # Journal Index
        journal_public = PUBLIC_DIR / 'journal'
        journal_public.mkdir(exist_ok=True)
        (journal_public / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{SECTION_CONFIG['journal']['title']}</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>{SECTION_CONFIG['journal']['title']}</h1>
        {"".join(f'''
        <div class="section-header" style="background: {sub['color']}">
            <h2><a href="{name}/index.html">{sub['title']}</a></h2>
        </div>
        ''' for name, sub in SECTION_CONFIG['journal']['subsections'].items())}
        <a class="back-link" href="../index.html">← Back</a>
    </div>
</body>
</html>""")

        # Legislative Index
        legislative_public = PUBLIC_DIR / 'legislative'
        legislative_public.mkdir(exist_ok=True)
        (legislative_public / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{SECTION_CONFIG['legislative']['title']}</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>{SECTION_CONFIG['legislative']['title']}</h1>
        <ul class="entry-list">
            <!-- Entries will be auto-populated -->
        </ul>
        <a class="back-link" href="../index.html">← Back</a>
    </div>
</body>
</html>""")

        # Journal Subsections
        for subsection in SECTION_CONFIG['journal']['subsections']:
            subsection_public = journal_public / subsection
            subsection_public.mkdir(parents=True, exist_ok=True)
            sub_config = SECTION_CONFIG['journal']['subsections'][subsection]
            (subsection_public / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{sub_config['title']}</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>{sub_config['title']}</h1>
        <ul class="entry-list">
            <!-- Entries will be auto-populated -->
        </ul>
        <a class="back-link" href="../index.html">← Back</a>
    </div>
</body>
</html>""")

    except Exception as e:
        logging.critical(f"Index error: {str(e)}")
        sys.exit(1)

def main():
    logging.info("Starting content generation")
    generate_indexes()

    for section in SECTION_CONFIG:
        source_dir = SECTION_CONFIG[section]['source']
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in ALLOWED_EXT:
                if section == 'journal':
                    subsection = file_path.relative_to(JOURNAL_DIR).parts[0]
                    process_entry(file_path, section, subsection)
                else:
                    process_entry(file_path, section)

    logging.info("Content generation complete")

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