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
JOURNAL_DIR = Path("journal")  # Changed to lowercase
LEGISLATIVE_DIR = Path("legislative")
PUBLIC_DIR = Path("public")
ALLOWED_EXT = {'.md', '.docx', '.pdf', '.txt'}
SITE_TITLE = "Political Memoranda"

SECTION_CONFIG = {
    'legislative': {
        'source': LEGISLATIVE_DIR,
        'public': PUBLIC_DIR / 'my-legislative-agenda',
        'title': 'My Legislative Agenda'
    },
    'journal': {
        'source': JOURNAL_DIR,
        'public': PUBLIC_DIR / 'journal',  # Changed to lowercase
        'title': 'Journal Archive',
        'subsections': {
            'personal': 'Personal Journal',
            'political': 'Political Memoranda',
            'law': 'Law Journal'
        }
    }
}

# ===== KEEP SHARED_CSS AND THEME_SCRIPT UNCHANGED =====
# ... [Previous CSS and JS content remains exactly the same] ...

def process_entry(file_path: Path, section: str, subsection: str = None):
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        config = SECTION_CONFIG[section]
        
        # Determine output path
        output_path = config['public']
        nav_links = f'<a href="../">Home</a> | <a href="./">{config["title"]}</a>'

        if subsection:
            output_path = output_path / subsection
            nav_links = f'''
                <a href="../../">Home</a> | 
                <a href="../">{config['title']}</a> | 
                <a href="./">{config['subsections'][subsection]}</a>
            '''

        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{base_name}.html"

        # Content extraction logic remains the same
        # ...

        # HTML generation
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_name.replace('-', ' ').title()} | {SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="government-header">
        <nav class="official-nav">
            <div class="site-title">{SITE_TITLE}</div>
            <div class="nav-links">
                <a href="legislative/">My Legislative Agenda</a>
                <a href="journal/">Journal Archive</a>  <!-- Lowercase link -->
            </div>
        </nav>
    </header>

    <div class="document-container">
        <article class="content">
            {content}
        </article>
    </div>

    {THEME_SCRIPT}
</body>
</html>"""
        output_file.write_text(html)
        return base_name
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return None

def generate_indexes():
    try:
        # Main Index (updated links)
        (PUBLIC_DIR / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="government-header">
        <nav class="official-nav">
            <div class="site-title">{SITE_TITLE}</div>
            <div class="nav-links">
                <a href="legislative/">My Legislative Agenda</a>
                <a href="journal/">Journal Archive</a>  <!-- Lowercase -->
            </div>
        </nav>
    </header>
    <!-- ... rest of index ... -->
</body>
</html>""")

        # Journal Index (lowercase paths)
        journal_index = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Journal Archive</title>
    {SHARED_CSS}
</head>
<body>
    <header class="government-header">
        <nav class="official-nav">
            <div class="site-title">{SITE_TITLE}</div>
            <div class="nav-links">
                <a href="../legislative/">My Legislative Agenda</a>
                <a href="../journal/">Journal Archive</a>  <!-- Lowercase -->
            </div>
        </nav>
    </header>
    <!-- ... rest of journal index ... -->
</body>
</html>"""
        (PUBLIC_DIR / 'journal' / 'index.html').write_text(journal_index)

    except Exception as e:
        logging.critical(f"Index error: {str(e)}")
        sys.exit(1)

def main():
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

        # Ensure source directories exist
        JOURNAL_DIR.mkdir(exist_ok=True)
        LEGISLATIVE_DIR.mkdir(exist_ok=True)

        # Process entries
        # ... (rest of main function remains the same)

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