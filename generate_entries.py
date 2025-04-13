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
PUBLIC_DIR = Path("public")
OUTPUT_DIR = PUBLIC_DIR / "journal"
ALLOWED_EXT = {'.md', '.docx', '.pdf', '.txt'}
SITE_TITLE = "Political Memoranda"

# ===== UNIVERSAL STYLES WITH DARK MODE =====
BASE_CSS = """
<style>
    :root {
        --primary: #00274D;
        --accent: #8B0000;
        --text: #333333;
        --background: #FFFFFF;
        --border: #DDDDDD;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text: #EEEEEE;
            --background: #121212;
            --border: #333333;
        }
    }

    [data-theme="dark"] {
        --text: #EEEEEE;
        --background: #121212;
        --border: #333333;
    }

    [data-theme="light"] {
        --text: #333333;
        --background: #FFFFFF;
        --border: #DDDDDD;
    }

    body {
        font-family: 'Times New Roman', serif;
        line-height: 1.6;
        max-width: 90rem;
        margin: 2rem auto;
        padding: 0 5vw;
        color: var(--text);
        background-color: var(--background);
        font-size: clamp(1rem, 2vw, 1.25rem);
        transition: background-color 0.3s, color 0.3s;
    }

    header {
        border-bottom: 2px solid var(--primary);
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        text-align: center;
    }

    h1 {
        color: var(--primary);
        font-size: clamp(2rem, 5vw, 3rem);
        margin: 0 0 1rem 0;
    }

    h2 {
        font-size: clamp(1.5rem, 3vw, 2rem);
        margin: 2rem 0 1rem;
    }

    .content {
        margin: 2rem 0;
        text-align: justify;
        max-width: 65ch;
    }

    footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
        color: var(--text);
        text-align: center;
        opacity: 0.8;
    }

    .theme-toggle {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        padding: 0.5rem;
        border-radius: 50%;
        background: var(--primary);
        color: white;
        cursor: pointer;
        border: none;
        width: 40px;
        height: 40px;
    }

    @media (min-width: 768px) {
        body {
            padding: 0 10vw;
        }
    }
</style>
"""

THEME_SCRIPT = """
<script>
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    function toggleTheme() {
        const current = localStorage.getItem('theme') || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        setTheme(current === 'dark' ? 'light' : 'dark');
    }

    // Initialize theme
    const savedTheme = localStorage.getItem('theme');
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');
    setTheme(initialTheme);
</script>
"""

def sanitize_filename(name: str) -> str:
    """Create web-safe filenames"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path):
    """Process individual journal entry"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"

        # Process content
        if file_path.suffix == '.md':
            with open(file_path, 'r') as f:
                content = markdown.markdown(f.read())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "\n".join(f"<p>{p.text}</p>" for p in doc.paragraphs if p.text)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "".join(f"<p>{page.extract_text()}</p>" for page in pdf.pages)
        else:
            with open(file_path, 'r') as f:
                content = f.read()

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_name.replace('-', ' ').title()}</title>
    {BASE_CSS}
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
        🌓
    </button>
    
    <header>
        <h1>{SITE_TITLE}</h1>
        <nav>
            <a href="/">← Back to Archive</a>
        </nav>
    </header>

    <div class="content">
        <h2>{base_name.replace('-', ' ').title()}</h2>
        {content}
    </div>

    <footer>
        <p>Document generated: {datetime.now().strftime('%Y-%m-%d')}</p>
        <p>Official archive - All rights reserved</p>
    </footer>
    
    {THEME_SCRIPT}
</body>
</html>
        """

        output_path.write_text(html)
        return base_name

    except Exception as e:
        logging.error(f"Error processing {file_path.name}: {str(e)}")
        return None

def generate_index(entries: list):
    """Generate archive index"""
    try:
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_TITLE} Archive</title>
    {BASE_CSS}
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
        🌓
    </button>
    
    <header>
        <h1>{SITE_TITLE} Archive</h1>
    </header>

    <div class="content">
        <ul class="entries">
            {"".join(f'''
            <li>
                <a href="journal/{e}.html">
                    {e.replace('-', ' ').title()}
                </a>
            </li>
            ''' for e in entries)}
        </ul>
    </div>

    <footer>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d')}</p>
    </footer>
    
    {THEME_SCRIPT}
</body>
</html>
        """

        (PUBLIC_DIR / 'index.html').write_text(index_html)
        logging.info("Index generated successfully")

    except Exception as e:
        logging.critical(f"Index generation failed: {str(e)}")
        sys.exit(1)

def main():
    """Main workflow"""
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        entries = []
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file():
                result = process_entry(entry)
                if result:
                    entries.append(result)

        if not entries:
            logging.error("No entries processed!")
            sys.exit(1)

        generate_index(entries)
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Build completed successfully")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()