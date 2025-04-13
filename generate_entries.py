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

# ===== SOPHISTICATED DESIGN SYSTEM =====
SHARED_CSS = """
<style>
    :root {
        --primary: #2B547E;    /* Authority Navy */
        --accent: #9B3D3D;     /* Crimson Accent */
        --text: #333333;       /* Base Text */
        --background: #FFFFFF; /* Light Background */
        --border: #E0E0E0;     /* Subtle Borders */
        --max-width: min(92vw, 1200px); /* Responsive Containers */
        --line-length: 70ch;   /* Optimal Readability */
    }

    [data-theme="dark"] {
        --text: #E8E8E8;       /* Soft White */
        --background: #1A1A1A; /* Deep Charcoal */
        --border: #404040;     /* Dark Mode Borders */
        --primary: #4A7BA6;    /* Softer Navy */
        --accent: #B85C5C;     /* Warm Accent */
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html {
        scroll-behavior: smooth;
    }

    body {
        font-family: 'Georgia', serif;
        line-height: 1.7;
        color: var(--text);
        background: var(--background);
        padding: 2rem 0;
        min-height: 100vh;
        transition: all 0.3s ease;
    }

    .container {
        width: var(--max-width);
        margin: 0 auto;
        padding: 0 2rem;
    }

    header {
        border-bottom: 2px solid var(--primary);
        padding-bottom: 1.5rem;
        margin-bottom: 2.5rem;
    }

    h1 {
        font-size: clamp(2rem, 5vw, 3rem);
        color: var(--primary);
        margin-bottom: 1rem;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    h2 {
        font-size: clamp(1.5rem, 3vw, 2rem);
        color: var(--primary);
        margin: 2rem 0 1rem;
    }

    .content {
        font-size: clamp(1rem, 1.8vw, 1.2rem);
        max-width: var(--line-length);
        margin: 0 auto;
        text-align: justify;
        hyphens: auto;
    }

    footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-size: 0.9rem;
        color: var(--text);
        opacity: 0.9;
    }

    .theme-toggle {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 50%;
        width: 3rem;
        height: 3rem;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    .theme-toggle:hover {
        transform: scale(1.1);
    }

    @media (max-width: 768px) {
        .container {
            padding: 0 1.5rem;
            width: 100%;
        }
        .theme-toggle {
            bottom: 1rem;
            right: 1rem;
        }
    }
</style>
"""

THEME_SCRIPT = """
<script>
    const theme = {
        init() {
            this.loadTheme()
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', e => this.loadTheme())
        },
        
        loadTheme() {
            const saved = localStorage.getItem('theme')
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
            document.documentElement.setAttribute('data-theme', 
                saved || (systemDark ? 'dark' : 'light'))
        },
        
        toggle() {
            const current = document.documentElement.getAttribute('data-theme')
            const newTheme = current === 'dark' ? 'light' : 'dark'
            localStorage.setItem('theme', newTheme)
            document.documentElement.setAttribute('data-theme', newTheme)
        }
    }
    
    document.addEventListener('DOMContentLoaded', () => theme.init())
</script>
"""

def sanitize_filename(name: str) -> str:
    """Generate web-safe filenames"""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path):
    """Process journal entries with unified design"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"

        # Content processing
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

        # Generate entry HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{base_name.replace('-', ' ').title()} | {SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <button class="theme-toggle" onclick="theme.toggle()">🌓</button>
    
    <div class="container">
        <header>
            <h1>{SITE_TITLE}</h1>
            <nav>
                <a href="/">← Return to Archive</a>
            </nav>
        </header>

        <main class="content">
            <h2>{base_name.replace('-', ' ').title()}</h2>
            {content}
        </main>

        <footer>
            <p>Document generated: {datetime.now().strftime('%Y-%m-%d')}</p>
            <p>Official Archive - Restricted Access</p>
        </footer>
    </div>
    
    <script>{THEME_SCRIPT}</script>
</body>
</html>
        """

        output_path.write_text(html)
        return base_name

    except Exception as e:
        logging.error(f"Error processing {file_path.name}: {str(e)}")
        return None

def generate_index(entries: list):
    """Generate professional index page"""
    try:
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_TITLE} Archive</title>
    {SHARED_CSS}
</head>
<body>
    <button class="theme-toggle" onclick="theme.toggle()">🌓</button>
    
    <div class="container">
        <header>
            <h1>{SITE_TITLE} Archive</h1>
        </header>

        <main class="content">
            <h2>Recent Memoranda</h2>
            <ul>
                {"".join(f'''
                <li style="margin: 1.5rem 0; padding-left: 1rem; border-left: 3px solid var(--accent)">
                    <a href="journal/{e}.html" style="text-decoration: none; color: var(--text)">
                        {e.replace('-', ' ').title()}
                    </a>
                </li>
                ''' for e in entries)}
            </ul>
        </main>

        <footer>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Classified Level IV - Public Access Authorized</p>
        </footer>
    </div>
    
    <script>{THEME_SCRIPT}</script>
</body>
</html>
        """

        (PUBLIC_DIR / 'index.html').write_text(index_html)
        logging.info("Index generated successfully")

    except Exception as e:
        logging.critical(f"Index generation failed: {str(e)}")
        sys.exit(1)

def main():
    """Main execution flow"""
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        entries = []
        for entry in sorted(JOURNAL_DIR.iterdir(), 
                          key=lambda x: x.stat().st_ctime, 
                          reverse=True):
            if entry.is_file() and entry.suffix.lower() in ALLOWED_EXT:
                result = process_entry(entry)
                if result:
                    entries.append(result)

        if not entries:
            logging.error("No valid entries processed")
            sys.exit(1)

        generate_index(entries)
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Build completed successfully")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()