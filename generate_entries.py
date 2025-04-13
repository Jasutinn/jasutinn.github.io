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

# ===== PROFESSIONAL DESIGN SYSTEM =====
SHARED_CSS = """
<style>
    :root {
        --primary: #1A2B4D;
        --accent: #7A1F1F;
        --text: #333333;
        --background: #FFFFFF;
        --border: #E0E0E0;
        --max-width: min(92vw, 1200px);
        --line-length: 70ch;
    }

    [data-theme="dark"] {
        --text: #E8E8E8;
        --background: #0A0A0A;
        --border: #404040;
        --primary: #2B4D7A;
        --accent: #9B3D3D;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Times New Roman', serif;
        line-height: 1.7;
        color: var(--text);
        background: var(--background);
        padding: 3rem 0;
        min-height: 100vh;
        transition: background 0.3s ease, color 0.3s ease;
    }

    .container {
        width: var(--max-width);
        margin: 0 auto;
        padding: 0 2rem;
    }

    header {
        border-bottom: 2px solid var(--primary);
        padding-bottom: 1.5rem;
        margin-bottom: 3rem;
        text-align: center;
    }

    h1 {
        font-size: 2.5rem;
        color: var(--primary);
        margin: 0 0 1rem 0;
        font-weight: normal;
    }

    .content {
        font-size: 1.1rem;
        max-width: var(--line-length);
        margin: 0 auto;
        text-align: left; /* Changed from justify */
    }

    .content p {
        margin: 1.5rem 0;
        line-height: 1.8;
        text-indent: 0; /* Removed paragraph indentation */
    }

    footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-size: 0.9rem;
        color: var(--text);
        opacity: 0.8;
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
        opacity: 0.9;
        transition: opacity 0.3s ease;
    }

    .theme-toggle:hover {
        opacity: 1;
    }

    @media (max-width: 768px) {
        .container {
            padding: 0 1.5rem;
        }
        h1 {
            font-size: 2rem;
        }
        .content {
            font-size: 1rem;
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
    """Generate web-safe filenames with proper spacing"""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned = ''.join(c for c in name if c in valid_chars).strip()
    return cleaned.replace(' ', '-')

def process_entry(file_path: Path):
    """Process all file types with formal structure"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            logging.warning(f"Skipped unsupported file: {file_path.name}")
            return None

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"

        # Extract content based on file type
        if file_path.suffix == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = markdown.markdown(f.read())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "".join(f"<p>{paragraph.text}</p>" for paragraph in doc.paragraphs if paragraph.text)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "".join(f"<p>{page.extract_text()}</p>" for page in pdf.pages if page.extract_text())
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f"<pre>{f.read()}</pre>"

        # Generate formal document structure
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
            <h1>{SITE_TITLE}</h1>
            <nav>
                <a href="/">← Return to Archive</a>
            </nav>
        </header>

        <main class="content">
            <article>
                {content}
            </article>
        </main>

        <footer>
            <p>Document generated: {datetime.now().strftime('%Y-%m-%d')}</p>
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
    """Generate formal archive index"""
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
    <button class="theme-toggle" onclick="toggleTheme()">🌓</button>
    
    <div class="container">
        <header>
            <h1>{SITE_TITLE}</h1>
            <nav>
                <p>Official Document Repository</p>
            </nav>
        </header>

        <main class="content">
            <article>
                <h2>Archival Index</h2>
                <ul style="list-style: none; padding-left: 0;">
                    {"".join(f'''
                    <li style="margin: 1.5rem 0; padding-left: 0; border-left: none;">
                        <a href="journal/{e}.html" style="text-decoration: none; color: var(--text)">
                            {e.replace('-', ' ').title()}
                        </a>
                    </li>
                    ''' for e in entries)}
                </ul>
            </article>
        </main>

        <footer>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
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
    """Main execution workflow"""
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        entries = []
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file() and entry.suffix.lower() in ALLOWED_EXT:
                result = process_entry(entry)
                if result:
                    entries.append(result)
                    logging.info(f"Processed: {entry.name}")

        if not entries:
            logging.error("No valid entries processed")
            sys.exit(1)

        generate_index(sorted(entries, key=lambda x: x.lower()))
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