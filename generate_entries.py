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
        'color': '#1A2B4D'  # Dark blue
    },
    'journal': {
        'source': JOURNAL_DIR,
        'public': PUBLIC_DIR / 'journal',
        'title': 'Journal Archive',
        'subsections': {
            'personal': {'title': 'Personal Journal', 'color': '#4A4A4A'},
            'political': {'title': 'Political Memoranda', 'color': '#DC143C'},  # Crimson
            'law': {'title': 'Law Journal', 'color': '#2B4D7A'}
        }
    }
}

SHARED_CSS = """
<style>
    :root {
        --primary: #1A2B4D;       /* Dark blue */
        --accent: #DC143C;        /* Crimson */
        --background: #F5F5DC;    /* Beige */
        --text: #333333;
        --border: #D4AF37;        /* Gold accent */
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Merriweather', serif;
        background: var(--background);
        color: var(--text);
        line-height: 1.6;
        min-height: 100vh;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }

    .header {
        background: var(--primary);
        color: white;
        padding: 1rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .nav {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: center;
    }

    .nav a {
        color: white;
        text-decoration: none;
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
        transition: opacity 0.3s;
    }

    .nav a:hover {
        opacity: 0.9;
    }

    .content-card {
        background: white;
        border-radius: 8px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .section-list {
        list-style: none;
        padding: 0;
    }

    .section-item {
        margin: 1.5rem 0;
        padding: 1.5rem;
        border-left: 4px solid var(--primary);
        transition: transform 0.2s;
    }

    .section-item:hover {
        transform: translateX(10px);
    }

    /* Political section specific */
    .political .section-item {
        border-left-color: var(--accent);
    }

    /* Mobile First Design */
    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        
        .nav {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
        }
        
        .content-card {
            padding: 1rem;
        }
    }

    @media (min-width: 992px) {
        .container {
            padding: 40px;
        }
    }
</style>
"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        config = SECTION_CONFIG[section]
        
        output_path = config['public']
        nav_links = []
        section_class = ''

        if subsection:
            output_path = output_path / subsection
            subsection_config = config['subsections'][subsection]
            nav_links = [
                ('../../', 'Home'),
                ('../', config['title']),
                ('./', subsection_config['title'])
            ]
            if subsection == 'political':
                section_class = 'class="political"'
        else:
            nav_links = [
                ('../', 'Home'),
                ('./', config['title'])
            ]

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

        # HTML generation
        html = f"""<!DOCTYPE html>
<html lang="en" {section_class}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_name.replace('-', ' ').title()} | {SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            {"".join(f'<a href="{link}">{title}</a>' for link, title in nav_links)}
        </nav>
    </header>

    <div class="container">
        <div class="content-card">
            <article class="content">
                {content}
            </article>
        </div>
    </div>
</body>
</html>"""
        output_file.write_text(html)
        return base_name
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return None

# Rest of the functions (generate_indexes, main) remain similar with updated styling
# ... [Previous main and supporting functions with styling updates] ...

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