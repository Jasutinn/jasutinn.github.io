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
        'public': PUBLIC_DIR / 'my-legislative-agenda',
        'title': 'My Legislative Agenda'
    },
    'journal': {
        'source': JOURNAL_DIR,
        'public': PUBLIC_DIR / 'journal',
        'title': 'Journal Archive',
        'subsections': {
            'personal': 'Personal Journal',
            'political': 'Political Memoranda', 
            'law': 'Law Journal'
        }
    }
}

SHARED_CSS = """
<style>
    :root {
        --primary: #1A2B4D;
        --accent: #7A1F1F;
        --text: #333;
        --background: #F9F9F9;
        --border: #DEE2E6;
        --header-height: 80px;
    }

    [data-theme="dark"] {
        --primary: #2B4D7A;
        --accent: #9B3D3D;
        --text: #E8E8E8;
        --background: #0A0A0A;
        --border: #404040;
    }

    body {
        font-family: 'Georgia', serif;
        background: var(--background);
        color: var(--text);
        line-height: 1.8;
        margin: 0;
        padding-top: var(--header-height);
    }

    .government-header {
        position: fixed;
        top: 0;
        width: 100%;
        background: var(--primary);
        color: white;
        padding: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
    }

    .official-nav {
        width: min(1200px, 90%);
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .site-title {
        font-size: 1.8rem;
        letter-spacing: -0.5px;
        font-weight: 700;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
    }

    .nav-links a {
        color: white;
        text-decoration: none;
        font-size: 1.1rem;
        transition: opacity 0.3s;
    }

    .nav-links a:hover {
        opacity: 0.8;
    }

    .document-container {
        width: min(800px, 90%);
        margin: 3rem auto;
        padding: 2rem;
        background: var(--background);
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .section-list {
        list-style: none;
        padding: 0;
        margin: 2rem 0;
    }

    .section-list li {
        margin: 1.5rem 0;
        padding: 1.5rem;
        background: rgba(26, 43, 77, 0.05);
        border-left: 4px solid var(--primary);
        transition: transform 0.2s;
    }

    .section-list li:hover {
        transform: translateX(10px);
    }

    @media (max-width: 768px) {
        .government-header {
            padding: 0.5rem 0;
        }
        
        .official-nav {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .nav-links {
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
        }
    }
</style>
"""

THEME_SCRIPT = """
<script>
    (function() {
        const storedTheme = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = storedTheme || (systemDark ? 'dark' : 'light');
        
        document.documentElement.setAttribute('data-theme', initialTheme);

        window.toggleTheme = function() {
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            document.documentElement.setAttribute('data-theme', newTheme);
        }
    })();
</script>
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
                <a href="journal/">Journal Archive</a>
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
        # Main Index
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
                <a href="journal/">Journal Archive</a>
            </div>
        </nav>
    </header>

    <div class="document-container">
        <h1 style="margin-top: 0">Official Repository</h1>
        <ul class="section-list">
            <li>
                <h2><a href="legislative/">My Legislative Agenda</a></h2>
                <p>Policy proposals and legislative initiatives</p>
            </li>
            <li>
                <h2><a href="journal/">Journal Archive</a></h2>
                <p>Personal, political, and legal memoranda</p>
            </li>
        </ul>
    </div>

    {THEME_SCRIPT}
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
    <header class="government-header">
        <nav class="official-nav">
            <div class="site-title">{SITE_TITLE}</div>
            <div class="nav-links">
                <a href="../legislative/">My Legislative Agenda</a>
                <a href="../journal/">Journal Archive</a>
            </div>
        </nav>
    </header>

    <div class="document-container">
        <h1>Legislative Documents</h1>
    </div>
</body>
</html>""")

        # Journal Index
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
                <a href="../journal/">Journal Archive</a>
            </div>
        </nav>
    </header>

    <div class="document-container">
        <h1>Journal Sections</h1>
        <ul class="section-list">
            <li><a href="personal/">Personal Journal</a></li>
            <li><a href="political/">Political Memoranda</a></li>
            <li><a href="law/">Law Journal</a></li>
        </ul>
    </div>
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

        # Process Legislative Agenda
        for file in SECTION_CONFIG['legislative']['source'].iterdir():
            if file.is_file() and file.suffix in ALLOWED_EXT:
                process_entry(file, 'legislative')

        # Process Journal Subsections
        for subsection in SECTION_CONFIG['journal']['subsections']:
            subsection_path = SECTION_CONFIG['journal']['source'] / subsection
            subsection_path.mkdir(exist_ok=True)
            for file in subsection_path.iterdir():
                if file.is_file() and file.suffix in ALLOWED_EXT:
                    process_entry(file, 'journal', subsection)

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