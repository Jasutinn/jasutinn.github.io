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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, minimum-scale=1.0">
<style>
  :root {
    --primary: #1A2B4D;
    --accent: #DC143C;
    --background: #F5F5DC;
    --text: #333333;
    --border: #D4AF37;
    --base-font: 1rem;
  }
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Merriweather', serif;
  }

  html {
    font-size: 16px;
  }

  body {
    background: var(--background);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
    font-size: var(--base-font);
  }

  .container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  .header {
    background: var(--primary);
    color: white;
    padding: 1rem 0;
    position: relative;
  }

  .nav {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    padding: 0 1rem;
  }

  .nav a {
    color: white;
    text-decoration: none;
    padding: 0.75rem 1.25rem;
    transition: all 0.3s ease;
    font-size: calc(var(--base-font) * 0.9);
    white-space: nowrap;
  }

  .nav a.active {
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
  }

  .nav a:hover {
    transform: translateY(-2px);
  }

  .content-card {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 2px 15px rgba(0,0,0,0.1);
  }

  @media (max-width: 480px) {
    :root { --base-font: 0.875rem; }
    .container { width: 95%; padding: 10px; }
    .nav { flex-direction: column; gap: 0.75rem; }
    .content-card { padding: 1.25rem; margin: 1rem 0; }
    .nav a { padding: 0.5rem; font-size: 1rem; }
  }

  @media (min-width: 481px) and (max-width: 768px) {
    :root { --base-font: 0.925rem; }
    .container { width: 90%; }
    .nav a { padding: 0.5rem 1rem; }
  }

  @media (min-width: 769px) and (max-width: 1024px) {
    :root { --base-font: 1rem; }
    .container { width: 85%; }
  }

  @media (prefers-reduced-motion: no-preference) {
    .nav a { transition: transform 0.2s ease, opacity 0.3s ease; }
  }
</style>
"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT or file_path.name.startswith('.'):
            return None

        base_name = sanitize_filename(file_path.stem)
        config = SECTION_CONFIG[section]
        
        output_path = config['public']
        nav_links = []
        current_page = ''

        if subsection:
            output_path = output_path / subsection
            subsection_config = config['subsections'][subsection]
            nav_links = [
                ('../../', 'Home'),
                ('../', config['title']),
                ('./', subsection_config['title'])
            ]
            current_page = subsection_config['title']
        else:
            nav_links = [
                ('../', 'Home'),
                ('./', config['title'])
            ]
            current_page = config['title']

        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{base_name}.html"

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

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, minimum-scale=1.0">
    <title>{base_name.replace('-', ' ').title()} | {current_page}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            {"".join(f'<a href="{link}"{" class=active" if title == current_page else ""}>{title}</a>' for link, title in nav_links)}
        </nav>
    </header>
    <div class="container">
        <div class="content-card">
            <h1>{base_name.replace('-', ' ').title()}</h1>
            <article class="content">
                {content}
            </article>
            <footer style="margin-top: 2rem; color: #666;">
                Document generated: {datetime.now().strftime('%Y-%m-%d')}
            </footer>
        </div>
    </div>
</body>
</html>"""
        output_file.write_text(html)
        return base_name
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return None

def generate_indexes():
    try:
        # Force create directories first
        (PUBLIC_DIR / 'journal').mkdir(parents=True, exist_ok=True)
        (PUBLIC_DIR / 'legislative').mkdir(parents=True, exist_ok=True)

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
            <a href="journal/">Journal Archive</a>
            <a href="legislative/">My Legislative Agenda</a>
        </nav>
    </header>
    <div class="container">
        <div class="content-card">
            <h1 style="margin-bottom: 1.5rem;">{SITE_TITLE}</h1>
            <div style="display: grid; gap: 2rem;">
                <section>
                    <h2 style="color: {SECTION_CONFIG['journal']['subsections']['political']['color']};">
                        <a href="journal/" style="text-decoration: none; color: inherit;">
                            Journal Archive
                        </a>
                    </h2>
                    <p>Strategic analyses and policy evaluations</p>
                </section>
                <section>
                    <h2 style="color: {SECTION_CONFIG['legislative']['color']};">
                        <a href="legislative/" style="text-decoration: none; color: inherit;">
                            My Legislative Agenda
                        </a>
                    </h2>
                    <p>Personal policy proposals and legislative tracking</p>
                </section>
            </div>
        </div>
    </div>
</body>
</html>""")

        # ... [Keep rest of generate_indexes() unchanged from previous version]

def main():
    # ... [Keep main() unchanged from previous version]

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