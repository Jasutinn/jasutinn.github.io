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
PRIMARY_COLOR = "#00274D"  # WCAG AA compliant
ACCENT_COLOR = "#8B0000"   # WCAG AA compliant

# ===== UNIVERSAL DESIGN SYSTEM =====
SHARED_CSS = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600&family=IBM+Plex+Sans:wght@300;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {PRIMARY_COLOR};
            --accent: {ACCENT_COLOR};
            --text: #333333;
            --background: #FFFFFF;
            --breakpoint-mobile: 480px;
            --breakpoint-tablet: 768px;
            --breakpoint-desktop: 1024px;
        }}

        /* Base Reset */
        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Source Serif Pro', serif;
            line-height: 1.6;
            color: var(--text);
            background-color: var(--background);
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            display: grid;
            grid-template-rows: auto 1fr auto;
        }}

        /* Universal Content Styles */
        .container {{
            width: 100%;
            max-width: var(--breakpoint-desktop);
            margin: 0 auto;
            padding: 1rem;
        }}

        /* Header */
        .document-header {{
            background: var(--primary);
            color: white;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
        }}

        .header-content {{
            max-width: var(--breakpoint-desktop);
            margin: 0 auto;
            padding: 0 1rem;
        }}

        /* Main Content */
        .document-content {{
            font-size: 1.1rem;
            hyphens: auto;
        }}

        .document-content img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5rem auto;
        }}

        /* Footer */
        .document-footer {{
            background: var(--primary);
            color: white;
            padding: 1.5rem 0;
            margin-top: 3rem;
        }}

        /* Entry List */
        .entry-list {{
            list-style: none;
            display: grid;
            gap: 1.5rem;
            padding: 1rem 0;
        }}

        .entry-item {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.2s;
        }}

        .entry-link {{
            display: block;
            padding: 1.5rem;
            color: var(--text);
            text-decoration: none;
        }}

        /* Responsive Breakpoints */
        @media (min-width: 480px) {{
            .container {{
                padding: 2rem;
            }}
            .entry-list {{
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }}
        }}

        @media (min-width: 768px) {{
            .document-content {{
                font-size: 1.15rem;
                line-height: 1.7;
            }}
        }}

        @media (min-width: 1024px) {{
            .container {{
                padding: 2rem 3rem;
            }}
        }}

        /* Accessibility */
        a:focus {{
            outline: 3px solid var(--accent);
            outline-offset: 2px;
        }}

        @media (prefers-reduced-motion: reduce) {{
            html {{
                scroll-behavior: auto;
            }}
            .entry-item {{
                transition: none;
            }}
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --text: #EEEEEE;
                --background: #121212;
            }}
            .entry-item {{
                background: #1E1E1E;
            }}
        }}
    </style>
"""

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler()
    ]
)

def sanitize_filename(name: str) -> str:
    """Create web-safe filenames"""
    safe_chars = set(f" -_.(){string.ascii_letters}{string.digits}")
    return "".join(c if c in safe_chars else '_' for c in name).strip('_')

def process_entry(file_path: Path) -> dict:
    """Process individual journal entry"""
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT:
            return None

        base_name = sanitize_filename(file_path.stem)
        output_path = OUTPUT_DIR / f"{base_name}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Process content
        content = ""
        if file_path.suffix == '.md':
            content = markdown.markdown(file_path.read_text())
        elif file_path.suffix == '.docx':
            doc = docx.Document(file_path)
            content = "\n".join(f"<p>{p.text}</p>" for p in doc.paragraphs if p.text)
        elif file_path.suffix == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                content = "".join(f"<p>{page.extract_text()}</p>" for page in pdf.pages)
        else:
            content = file_path.read_text()

        # Generate entry HTML
        entry_html = f"""{SHARED_CSS}
</head>
<body>
    <header class="document-header">
        <div class="header-content">
            <h1>{SITE_TITLE}</h1>
        </div>
    </header>
    
    <main class="container">
        <article class="document-content">
            <h2>{base_name.replace('_', ' ').title()}</h2>
            <div class="entry-meta">
                Last Updated: {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')}
            </div>
            {content}
        </article>
    </main>
    
    <footer class="document-footer">
        <div class="container">
            <p>{SITE_TITLE} Archive - Accessible Across All Platforms</p>
            <p>Automatically generated on {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </footer>
</body>
</html>
        """

        output_path.write_text(entry_html)
        return {
            "title": base_name.replace('_', ' ').title(),
            "filename": base_name,
            "date": datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d')
        }

    except Exception as e:
        logging.error(f"Failed {file_path.name}: {str(e)}")
        return None

def generate_index(entries: list):
    """Generate universal index page"""
    try:
        index_html = f"""{SHARED_CSS}
</head>
<body>
    <header class="document-header">
        <div class="header-content">
            <h1>{SITE_TITLE} Archive</h1>
        </div>
    </header>
    
    <main class="container">
        <ul class="entry-list">
            {"".join(f'''
            <li class="entry-item">
                <a href="journal/{e['filename']}.html" class="entry-link">
                    <h3>{e['title']}</h3>
                    <div class="entry-meta">{e['date']}</div>
                </a>
            </li>
            ''' for e in entries)}
        </ul>
    </main>
    
    <footer class="document-footer">
        <div class="container">
            <p>Universal Access Version {datetime.now().strftime('%Y.%m')}</p>
            <p>Optimized for all devices and platforms</p>
        </div>
    </footer>
</body>
</html>
        """

        (PUBLIC_DIR / 'index.html').write_text(index_html)
        logging.info("Universal index generated")

    except Exception as e:
        logging.critical(f"Index generation failed: {str(e)}")
        sys.exit(1)

def main():
    """Main execution flow"""
    try:
        shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        entries = []
        for entry in JOURNAL_DIR.iterdir():
            if entry.is_file() and entry.suffix.lower() in ALLOWED_EXT:
                result = process_entry(entry)
                if result:
                    entries.append(result)

        if not entries:
            logging.error("No valid entries processed!")
            sys.exit(1)

        generate_index(sorted(entries, key=lambda x: x["date"], reverse=True))
        (PUBLIC_DIR / '.nojekyll').touch()
        (PUBLIC_DIR / 'CNAME').write_text('yourdomain.com')  # Set if using custom domain
        logging.info("Universal build completed")

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()