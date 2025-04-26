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
  /* ... [your original CSS unchanged] ... */
</style>
"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    # ... [your original process_entry code unchanged] ...

def generate_indexes():
    try:  # <- ONLY FIX: Added 4-space indent here
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        
        # Main Index - YOUR ORIGINAL CONTENT
        (PUBLIC_DIR / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <!-- Your original index content -->
</body>
</html>""")

        # Journal Index - YOUR ORIGINAL CONTENT
        journal_public = PUBLIC_DIR / 'journal'
        journal_public.mkdir(exist_ok=True)
        (journal_public / 'index.html').write_text("""...""")

        # Legislative Index - YOUR ORIGINAL CONTENT
        legislative_public = PUBLIC_DIR / 'legislative'
        legislative_public.mkdir(exist_ok=True)
        (legislative_public / 'index.html').write_text("""...""")

        # Journal Subsections - YOUR ORIGINAL CONTENT
        for subsection in SECTION_CONFIG['journal']['subsections']:
            subsection_public = journal_public / subsection
            subsection_public.mkdir(parents=True, exist_ok=True)
            (subsection_public / 'index.html').write_text("""...""")

    except Exception as e:
        logging.critical(f"Index error: {str(e)}")
        sys.exit(1)

def main():
    # ... [your original main() code unchanged] ...

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