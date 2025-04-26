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
  /* ... [keep CSS unchanged from previous version] ... */
</style>
"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    # ... [keep process_entry() unchanged from previous version] ...

def generate_indexes():
    try:
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        
        # Main Index
        (PUBLIC_DIR / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="./">Home</a>
            <a href="journal/">Journal</a>
            <a href="legislative/">Legislative</a>
        </nav>
    </header>
    <div class="container">
        <h1>Welcome to {SITE_TITLE}</h1>
        <div class="grid">
            <a href="journal/" class="card">
                <h2>Journal Archive</h2>
            </a>
            <a href="legislative/" class="card">
                <h2>Legislative Agenda</h2>
            </a>
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
    <title>Journal Archive</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="../../">Home</a>
            <a href="./" class="active">Journal Archive</a>
        </nav>
    </header>
    <div class="container">
        <div class="content-card">
            <h1>Journal Entries</h1>
            <div class="grid">
                <a href="personal/" class="card">Personal</a>
                <a href="political/" class="card">Political</a>
                <a href="legal/" class="card">Legal</a>
            </div>
        </div>
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
    <title>My Legislative Agenda</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="../../">Home</a>
            <a href="./" class="active">Legislative Agenda</a>
        </nav>
    </header>
    <div class="container">
        <div class="content-card">
            <h1>Legislative Proposals</h1>
            <ul>
                <li><a href="sample.html">Sample Proposal</a></li>
            </ul>
        </div>
    </div>
</body>
</html>""")

        # Journal Subsections
        for subsection in SECTION_CONFIG['journal']['subsections']:
            subsection_public = journal_public / subsection
            subsection_public.mkdir(parents=True, exist_ok=True)
            
            subsection_config = SECTION_CONFIG['journal']['subsections'][subsection]
            (subsection_public / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{subsection_config['title']}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            <a href="../../">Home</a>
            <a href="../">Journal Archive</a>
            <a href="./" class="active">{subsection_config['title']}</a>
        </nav>
    </header>
    <div class="container">
        <div class="content-card">
            <h1>{subsection_config['title']}</h1>
            <ul>
                <li><a href="sample.html">Sample Entry</a></li>
            </ul>
        </div>
    </div>
</body>
</html>""")

    except Exception as e:
        logging.critical(f"Index error: {str(e)}")
        sys.exit(1)

def main():
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

        # Process all content
        for section in SECTION_CONFIG:
            section_dir = SECTION_CONFIG[section]['source']
            section_dir.mkdir(exist_ok=True)
            
            if 'subsections' in SECTION_CONFIG[section]:
                for subsection in SECTION_CONFIG[section]['subsections']:
                    subsection_dir = section_dir / subsection
                    subsection_dir.mkdir(exist_ok=True)
                    for file in subsection_dir.iterdir():
                        if file.is_file() and file.suffix in ALLOWED_EXT:
                            process_entry(file, section, subsection)
            else:
                for file in section_dir.iterdir():
                    if file.is_file() and file.suffix in ALLOWED_EXT:
                        process_entry(file, section)

        generate_indexes()
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Build completed successfully")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

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