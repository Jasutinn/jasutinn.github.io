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

# ===== UNIVERSAL DESIGN SYSTEM =====
SHARED_CSS = """
<style>
    :root {
        --primary: #1A2B4D;
        --accent: #7A1F1F;
        --text: #333333;
        --background: #F8F9FA;
        --border: #E0E0E0;
        --max-width: 1200px;
        --line-length: 70ch;
        font-size: clamp(100%, 1rem + 0.5vw, 110%);
    }

    [data-theme="dark"] {
        --text: #E8E8E8;
        --background: #121212;
        --border: #2D2D2D;
        --primary: #2B3A5A;
        --accent: #8B5D5D;
    }

    /* ... (keep all previous CSS rules unchanged) ... */
</style>
"""

THEME_SCRIPT = """
<script>
    // ... (keep previous theme script unchanged) ...
</script>
"""

def sanitize_filename(name: str) -> str:
    """Generate web-safe filenames with proper spacing"""
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned = ''.join(c for c in name if c in valid_chars).strip()
    return cleaned.replace(' ', '-')

def process_entry(file_path: Path):
    """Process document files into HTML pages"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            logging.warning(f"Skipped unsupported file: {file_path.name}")
            return None

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"

        # Content extraction logic
        if file_path.suffix == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = markdown.markdown(f.read())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "".join(f"<p>{paragraph.text}</p>" for paragraph in doc.paragraphs if paragraph.text)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "".join(f"<p>{page.extract_text()}</p>" for page in pdf.pages if page.extract_text())
        else:  # .txt files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f"<pre>{f.read()}</pre>"

        # HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
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
    """Generate archive index page"""
    try:
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
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
                <ul>
                    {"".join(f'''
                    <li style="margin: 1.5rem 0; padding-left: 2rem; border-left: 2px solid var(--primary)">
                        <a href="journal/{e}.html">
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
    """Main execution workflow"""
    try:
        # Clean previous build
        if PUBLIC_DIR.exists():
            shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        
        # Create directories with proper permissions
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
        JOURNAL_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)

        # Process journal entries
        entries = []
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file() and entry.suffix.lower() in ALLOWED_EXT:
                result = process_entry(entry)
                if result:
                    entries.append(result)
                    logging.info(f"Processed: {entry.name}")

        # Handle empty journal case
        if not entries:
            logging.warning("No valid entries found - generating empty index")
            entries = ["welcome"]  # Default entry for empty journal

        generate_index(sorted(entries, key=lambda x: x.lower()))
        (PUBLIC_DIR / '.nojekyll').touch(mode=0o644)
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