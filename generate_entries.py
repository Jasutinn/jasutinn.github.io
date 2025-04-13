import os
import string  # ← REQUIRED IMPORT ADDED HERE
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

# ===== SAFE CHARACTER SET =====
SAFE_CHARS = set(f" -_.(){string.ascii_letters}{string.digits}")  # ← FIXED LINE

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler()
    ]
)

def sanitize_filename(name: str) -> str:
    """Convert to web-safe filename"""
    return "".join(c if c in SAFE_CHARS else '_' for c in name).strip('_')

def process_entry(file_path: Path) -> bool:
    """Process individual entry file"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return False

        clean_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{clean_name}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Content processing
        if file_path.suffix == '.md':
            content = markdown.markdown(file_path.read_text())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "\n".join(p.text for p in doc.paragraphs)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "\n".join(page.extract_text() for page in pdf.pages)
        else:
            content = file_path.read_text()

        # HTML template
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{clean_name.replace('_', ' ').title()}</title>
            <style>
                body {{ 
                    font-family: 'Times New Roman', serif;
                    line-height: 1.8;
                    max-width: 680px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }}
                h1 {{ color: #00274D; border-bottom: 2px solid #00274D; }}
                .content {{ margin: 2rem 0; }}
                footer {{ color: #666; margin-top: 3rem; }}
            </style>
        </head>
        <body>
            <h1>{clean_name.replace('_', ' ').title()}</h1>
            <div class="content">{content}</div>
            <footer>{SITE_TITLE} - {datetime.now().strftime('%Y-%m-%d')}</footer>
        </body>
        </html>
        """
        
        output_path.write_text(html)
        return True

    except Exception as e:
        logging.error(f"Failed {file_path.name}: {str(e)}")
        return False

def generate_index():
    """Generate main index page"""
    try:
        entries = sorted(
            [f.stem for f in OUTPUT_DIR.glob('*.html')],
            key=lambda x: x.lower(),
            reverse=True
        )
        
        index_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{SITE_TITLE}</title>
            <style>
                body {{ 
                    font-family: 'Times New Roman', serif;
                    line-height: 1.8;
                    max-width: 680px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }}
                h1 {{ color: #00274D; border-bottom: 2px solid #00274D; }}
                .entry-list {{ list-style: none; padding: 0; }}
                .entry-item {{ margin: 1.2rem 0; padding-left: 1rem; }}
                .entry-link {{ color: #00274D; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>{SITE_TITLE}</h1>
            <ul class="entry-list">
                {"".join(f'<li class="entry-item"><a class="entry-link" href="journal/{e}.html">{e.replace("_", " ").title()}</a></li>' for e in entries)}
            </ul>
        </body>
        </html>
        """
        
        (PUBLIC_DIR / 'index.html').write_text(index_html)
        logging.info(f"Index generated with {len(entries)} entries")

    except Exception as e:
        logging.critical(f"Index generation failed: {str(e)}")
        sys.exit(1)

def main():
    """Main execution flow"""
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file() and process_entry(entry):
                success_count += 1

        if success_count == 0:
            logging.error("No valid entries processed!")
            sys.exit(1)

        generate_index()
        (PUBLIC_DIR / '.nojekyll').touch()
        logging.info("Deployment package ready")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()