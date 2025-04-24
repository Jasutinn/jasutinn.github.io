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
JOURNAL_DIR = Path("Journal")
LEGISLATIVE_DIR = Path("Legislative")
PUBLIC_DIR = Path("public")
ALLOWED_EXT = {'.md', '.docx', '.pdf', '.txt'}
SITE_TITLE = "Political Memoranda"

SECTION_CONFIG = {
    'legislative': {
        'source': LEGISLATIVE_DIR,
        'public': PUBLIC_DIR / 'My-Legislative-Agenda',
        'title': 'My Legislative Agenda'
    },
    'journal': {
        'source': JOURNAL_DIR,
        'public': PUBLIC_DIR / 'Journal',
        'subsections': {
            'personal': 'Personal Journal',
            'political': 'Political Memoranda',
            'law': 'Law Journal'
        }
    }
}

# ===== KEEP ORIGINAL CSS AND JS =====
SHARED_CSS = """<style>/* Your original CSS here */</style>"""
THEME_SCRIPT = """<script>/* Your original theme script here */</script>"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        config = SECTION_CONFIG[section]
        
        # Determine output path
        if subsection:
            output_path = config['public'] / subsection
            nav_links = f'''
                <a href="../../">Home</a> | 
                <a href="../">{config['title']}</a> | 
                <a href="./">{config['subsections'][subsection]}</a>
            '''
        else:
            output_path = config['public']
            nav_links = f'<a href="../">Home</a> | <a href="./">{config["title"]}</a>'

        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{base_name}.html"

        # Content extraction
        if file_path.suffix == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = markdown.markdown(f.read())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "".join(f"<p>{p.text}</p>" for p in doc.paragraphs if p.text)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "".join(f"<p>{p.extract_text()}</p>" for p in pdf.pages if p.extract_text())
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f"<pre>{f.read()}</pre>"

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_name.replace('-', ' ').title()} | {SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()">🌓</button>
    <div class="container">
        <header>
            <h1>{SECTION_CONFIG[section]['subsections'][subsection] if subsection else SECTION_CONFIG[section]['title']}</h1>
            <nav>{nav_links}</nav>
        </header>
        <main class="content">{content}</main>
        <footer>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d')}</p>
        </footer>
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
        # Main Index
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
        <nav>
            <a href="My-Legislative-Agenda/">My Legislative Agenda</a><br>
            <a href="Journal/">Journal Archive</a>
        </nav>
    </div>
</body>
</html>""")

        # Legislative Index
        (SECTION_CONFIG['legislative']['public'] / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Legislative Agenda</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>My Legislative Agenda</h1>
        <nav><a href="../">← Home</a></nav>
    </div>
</body>
</html>""")

        # Journal Index
        (SECTION_CONFIG['journal']['public'] / 'index.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Journal Archive</title>
    {SHARED_CSS}
</head>
<body>
    <div class="container">
        <h1>Journal Sections</h1>
        <nav>
            <a href="../">← Home</a> | 
            <a href="personal/">Personal</a> | 
            <a href="political/">Political</a> | 
            <a href="law/">Law</a>
        </nav>
    </div>
</body>
</html>""")

    except Exception as e:
        logging.critical(f"Index error: {str(e)}")
        sys.exit(1)

def main():
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        PUBLIC_DIR.mkdir()

        # Process Legislative
        legislative_public = SECTION_CONFIG['legislative']['public']
        legislative_public.mkdir()
        for file in SECTION_CONFIG['legislative']['source'].iterdir():
            if file.is_file() and file.suffix in ALLOWED_EXT:
                process_entry(file, 'legislative')

        # Process Journal Subsections
        journal_public = SECTION_CONFIG['journal']['public']
        journal_public.mkdir()
        for subsection in SECTION_CONFIG['journal']['subsections']:
            subsection_path = SECTION_CONFIG['journal']['source'] / subsection
            (journal_public / subsection).mkdir()
            for file in subsection_path.iterdir():
                if file.is_file() and file.suffix in ALLOWED_EXT:
                    process_entry(file, 'journal', subsection)

        generate_indexes()
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Build successful")

    except Exception as e:
        logging.critical(f"Fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    main()