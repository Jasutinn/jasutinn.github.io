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
SITE_TITLE = "Political Memoranda"  # Unified title

# ===== ENHANCED DESIGN SYSTEM =====
SHARED_CSS = """
<style>
    :root {
        --primary: #2B547E;    /* Professional Navy */
        --accent: #9B3D3D;     /* Warm Accent */
        --text: #333333;
        --background: #FFFFFF;
        --border: #E0E0E0;
        --max-width: min(92vw, 1200px);
        --line-length: 70ch;
    }

    [data-theme="dark"] {
        --text: #F0F0F0;
        --background: #1A1A1A;
        --border: #404040;
        --primary: #4A7BA6;
        --accent: #B85C5C;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
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
        text-align: center;
    }

    h1 {
        font-size: clamp(2rem, 5vw, 3rem);
        color: var(--primary);
        margin-bottom: 1rem;
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
    }

    .content p {
        margin: 1.5rem 0;
        line-height: 1.8;
        text-align: justify;
    }

    .key-findings {
        background: rgba(var(--primary), 0.05);
        border-left: 4px solid var(--accent);
        padding: 1.5rem;
        margin: 2rem 0;
    }

    footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-size: 0.9rem;
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
    """Generate web-safe filenames with proper spacing"""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned = ''.join(c for c in name if c in valid_chars).strip()
    return cleaned.replace(' ', '-')

def extract_title(content: str) -> str:
    """Extract title from first meaningful line"""
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 10:  # Skip short lines/empty
            return stripped.replace('#', '').strip()
    return "Untitled Entry"

def process_entry(file_path: Path):
    """Process journal entries with proper structure"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"
        title = extract_title(raw_content)
        
        # Process content with proper spacing
        if file_path.suffix == '.md':
            content = markdown.markdown(raw_content)
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "".join(f"<p>{p.text}</p>" for p in doc.paragraphs if p.text)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "".join(f"<p>{page.extract_text()}</p>" for page in pdf.pages)
        else:
            content = f"<pre>{raw_content}</pre>"

        # Generate structured HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {SITE_TITLE}</title>
    {SHARED_CSS}
</head>
<body>
    <button class="theme-toggle" onclick="theme.toggle()">🌓</button>
    
    <div class="container">
        <header>
            <h1>{SITE_TITLE}</h1>
            <nav>
                <a href="/">← Back to Archive</a>
            </nav>
        </header>

        <main class="content">
            <article>
                <h2>{title}</h2>
                
                <div class="metadata">
                    <p>Published: {datetime.now().strftime('%B %d, %Y')}</p>
                </div>

                <div class="key-findings">
                    <h3>Key Findings</h3>
                    <!-- Add your key findings content here -->
                </div>

                <div class="main-content">
                    {content}
                </div>
            </article>
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
    """Generate main index page with consistent naming"""
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
            <h1>{SITE_TITLE}</h1>
            <nav>
                <p>Comprehensive Policy Archive</p>
            </nav>
        </header>

        <main class="content">
            <h2>Recent Entries</h2>
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
    """Main workflow execution"""
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