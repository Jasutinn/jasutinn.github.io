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

# ===== SIMPLE PROFESSIONAL STYLE =====
BASE_CSS = """
<style>
    :root {
        --primary: #00274D;
        --accent: #8B0000;
    }
    body {
        font-family: 'Times New Roman', serif;
        line-height: 1.8;
        max-width: 800px;
        margin: 2rem auto;
        padding: 0 20px;
        color: #333;
    }
    header {
        border-bottom: 2px solid var(--primary);
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        text-align: center;
    }
    h1 {
        color: var(--primary);
        font-size: 2rem;
        margin: 0 0 0.5rem 0;
    }
    .content {
        margin: 2rem 0;
        text-align: justify;
    }
    footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
        color: #666;
        text-align: center;
    }
    ul.entries {
        list-style: none;
        padding: 0;
    }
    li.entry {
        margin: 1rem 0;
        padding-left: 1rem;
        border-left: 3px solid var(--accent);
    }
    a {
        color: var(--primary);
        text-decoration: none;
    }
    @media (max-width: 768px) {
        body {
            margin: 1rem auto;
        }
    }
</style>
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
    <header>
        <h1>{SITE_TITLE} Archive</h1>
    </header>

    <ul class="entries">
        {"".join(f'''
        <li class="entry">
            <a href="journal/{e}.html">
                {e.replace('-', ' ').title()}
            </a>
        </li>
        ''' for e in entries)}
    </ul>

    <footer>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d')}</p>
    </footer>
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