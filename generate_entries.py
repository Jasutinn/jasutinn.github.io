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
        'color': '#1A2B4D'
    },
    'journal': {
        'source': JOURNAL_DIR,
        'public': PUBLIC_DIR / 'journal',
        'title': 'Journal Archive',
        'subsections': {
            'personal': {'title': 'Personal Journal', 'color': '#4A4A4A'},
            'political': {'title': 'Political Journal', 'color': '#DC143C'},
            'legal': {'title': 'Legal Journal', 'color': '#2B4D7A'}
        }
    }
}

SHARED_CSS = """<link href="https://fonts.googleapis.com/css2?family=Merriweather&display=swap" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<style>
  :root {
    --primary: #1A2B4D;
    --accent: #DC143C;
    --background: #F5F5DC;
    --text: #333333;
    --border: #D4AF37;
    --base-font: 1rem;
    --container-width: 90%;
  }
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Merriweather', serif;
  }

  html {
    font-size: 16px;
    scroll-behavior: smooth;
  }

  body {
    background: var(--background);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
    font-size: var(--base-font);
  }

  /* ===== Core Layout ===== */
  .container {
    width: var(--container-width);
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .header {
    background: var(--primary);
    color: white;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }

  .nav {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    justify-content: center;
    padding: 0 1rem;
  }

  .nav a {
    color: white;
    text-decoration: none;
    padding: 0.75rem 1.25rem;
    transition: all 0.3s ease;
    border-radius: 4px;
    font-size: calc(var(--base-font) * 0.95);
  }

  .nav a.active,
  .nav a:hover {
    background: rgba(255,255,255,0.15);
  }

  /* ===== Content Styles ===== */
  .content-card {
    background: white;
    border-radius: 12px;
    padding: 2.5rem;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  }

  .content-card h1 {
    color: var(--primary);
    font-size: 2.2rem;
    margin-bottom: 1.5rem;
    border-bottom: 3px solid var(--accent);
    padding-bottom: 0.5rem;
  }

  .content-card article {
    font-size: 1.1rem;
  }

  .content-card article p {
    margin-bottom: 1.2rem;
  }

  footer {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #ddd;
    color: #666;
    font-size: 0.9rem;
  }

  /* ===== Universal Elements ===== */
  h1, h2, h3 {
    color: var(--primary);
    margin-bottom: 1rem;
  }

  a {
    color: var(--accent);
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }

  ul, ol {
    padding-left: 2rem;
    margin: 1rem 0;
  }

  li {
    margin-bottom: 0.5rem;
  }

  pre {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
  }

  /* ===== Responsive Design ===== */
  @media (max-width: 768px) {
    :root {
      --container-width: 95%;
      --base-font: 0.9375rem;
    }
    
    .content-card {
      padding: 1.5rem;
    }
    
    .nav {
      flex-direction: column;
      text-align: center;
      gap: 0.75rem;
    }
  }

  @media (max-width: 480px) {
    :root {
      --container-width: 98%;
    }
    
    .content-card h1 {
      font-size: 1.75rem;
    }
  }
</style>
"""

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return ''.join(c for c in name if c in valid_chars).strip().replace(' ', '-')

def process_entry(file_path: Path, section: str, subsection: str = None):
    try:
        if file_path.suffix.lower() not in ALLOWED_EXT or file_path.name.startswith('.'):
            return None

        base_name = sanitize_filename(file_path.stem)
        config = SECTION_CONFIG[section]
        
        output_path = config['public']
        nav_links = []
        current_page = ''

        if subsection:
            output_path = output_path / subsection
            subsection_config = config['subsections'][subsection]
            nav_links = [
                ('../../', 'Home'),
                ('../', config['title']),
                ('./', subsection_config['title'])
            ]
            current_page = subsection_config['title']
        else:
            nav_links = [
                ('../', 'Home'),
                ('./', config['title'])
            ]
            current_page = config['title']

        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{base_name}.html"

        # Content processing (unchanged from previous version)
        # ...

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{base_name.replace('-', ' ').title()} | {current_page}</title>
    {SHARED_CSS}
</head>
<body>
    <header class="header">
        <nav class="nav">
            {"".join(f'<a href="{link}"{" class=active" if title == current_page else ""}>{title}</a>' for link, title in nav_links)}
        </nav>
    </header>
    <div class="container">
        <div class="content-card">
            <h1>{base_name.replace('-', ' ').title()}</h1>
            <article class="content">
                {content}
            </article>
            <footer>
                Document generated: {datetime.now().strftime('%Y-%m-%d')}
            </footer>
        </div>
    </div>
</body>
</html>"""
        output_file.write_text(html)
        return base_name
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return None

# Rest of generate_indexes() and main() remain unchanged from previous version