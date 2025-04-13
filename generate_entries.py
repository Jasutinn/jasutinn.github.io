import os
import markdown
import pdfplumber
import docx
from datetime import datetime
from bs4 import BeautifulSoup
import shutil

# ===== DESIGN-CORRECTED VERSION =====
JOURNAL_DIR = "journal"
PUBLIC_DIR = "public"
OUTPUT_DIR = os.path.join(PUBLIC_DIR, "journal")

PROFESSIONAL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #00274D;
            --accent: #8B0000;
        }}
        * {{ box-sizing: border-box; margin: 0; }}
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 680px;
            margin: 2rem auto;
            padding: 0 1rem;
            color: #333;
        }}
        header {{
            border-bottom: 3px solid var(--primary);
            margin-bottom: 2rem;
            padding-bottom: 1rem;
        }}
        h1 {{
            color: var(--primary);
            font-size: 2rem;
            letter-spacing: -0.5px;
        }}
        .entry-list {{
            list-style: none;
            padding: 0;
            margin-top: 2rem;
        }}
        .entry-item {{
            margin: 1.2rem 0;
            padding: 1rem;
            border-left: 4px solid var(--accent);
            transition: all 0.2s;
        }}
        .entry-item:hover {{
            background: #f8f8f8;
            transform: translateX(5px);
        }}
        .entry-link {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            font-size: 1.1rem;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            color: #666;
            border-top: 1px solid #ddd;
            text-align: center;
        }}
        @media (max-width: 480px) {{
            body {{ margin: 1rem auto; }}
            h1 {{ font-size: 1.6rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Political Memoranda</h1>
    </header>

    <ul class="entry-list">
        {entries}
    </ul>

    <footer>
        &copy; {year} Justine de La Torre<br>
        Official digital repository - All rights reserved
    </footer>
</body>
</html>
"""

def process_entries():
    # Clean previous build
    shutil.rmtree(PUBLIC_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    entries = []
    
    # Process journal files
    for filename in sorted(os.listdir(JOURNAL_DIR), reverse=True):
        if not filename.lower().endswith(('.md', '.docx', '.pdf', '.txt')):
            continue

        try:
            base_name = os.path.splitext(filename)[0]
            title = ' '.join(base_name.split('-')).title()
            entry_path = os.path.join(OUTPUT_DIR, f"{base_name}.html")
            
            # Generate entry content
            with open(os.path.join(JOURNAL_DIR, filename), "r") as f:
                content = markdown.markdown(f.read()) if filename.endswith('.md') else f.read()

            # Save individual entry
            with open(entry_path, "w") as f:
                f.write(f"""<!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{title}</title>
                    <style>
                        body {{ 
                            font-family: 'Georgia', serif;
                            line-height: 1.8;
                            max-width: 680px;
                            margin: 2rem auto;
                            padding: 0 1rem;
                        }}
                        .content {{ margin: 2rem 0; }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    <div class="content">{content}</div>
                </body>
                </html>
                """)

            entries.append(f"""
            <li class="entry-item">
                <a href="journal/{base_name}.html" class="entry-link">
                    {title}
                </a>
            </li>
            """)

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    # Generate professional index
    with open(os.path.join(PUBLIC_DIR, "index.html"), "w") as f:
        f.write(PROFESSIONAL_TEMPLATE.format(
            entries='\n'.join(entries),
            year=datetime.now().year
        ))

if __name__ == "__main__":
    process_entries()