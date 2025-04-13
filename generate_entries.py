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

# ===== DESIGN SYSTEM =====
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

    html {
        visibility: hidden;
        opacity: 0;
    }
    
    html.loaded {
        visibility: visible;
        opacity: 1;
        transition: opacity 0.3s ease;
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
        min-width: 320px;
        transition: background 0.5s ease, color 0.5s ease;
        font-size: clamp(1rem, 0.75rem + 0.5vw, 1.1rem);
    }

    .container {
        width: min(92%, var(--max-width));
        margin: 0 auto;
        padding: 0 2rem;
    }

    header {
        border-bottom: 2px solid var(--primary);
        padding: 0 0 1.5rem 2rem;
        margin-bottom: 3rem;
    }

    h1 {
        font-size: clamp(2rem, 1.5rem + 1.5vw, 2.5rem);
        color: var(--primary);
        margin: 0 0 1rem 0;
        font-weight: normal;
    }

    .content {
        max-width: min(95%, var(--line-length));
        min-width: 280px;
        margin: 0 auto;
    }

    .content p {
        margin: 1.5rem 0;
        line-height: 1.8;
    }

    footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-size: 0.9em;
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
        transition: all 0.3s ease;
    }

    .theme-toggle:hover {
        opacity: 1;
        transform: scale(1.05);
    }

    a {
        color: var(--text);
        text-decoration: none;
        transition: color 0.3s ease;
    }

    a:hover {
        color: var(--accent);
        text-decoration: underline;
    }

    @media (pointer: coarse) {
        body {
            font-size: clamp(1.05rem, 1rem + 0.5vw, 1.15rem);
            line-height: 1.8;
        }
        
        .theme-toggle {
            width: 4rem;
            height: 4rem;
            bottom: 3rem;
            right: 3rem;
        }
    }

    @media (max-width: 768px) {
        .container {
            padding: 0 1.5rem;
        }
        
        header {
            padding-left: 1rem;
        }
    }

    @media (min-width: 1600px) {
        :root {
            font-size: 105%;
        }
    }
</style>
"""

THEME_SCRIPT = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        document.documentElement.classList.add('loaded');
        
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)');
        const updateTheme = (isDark) => {
            document.documentElement.style.transition = 'none';
            requestAnimationFrame(() => {
                document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
                document.documentElement.style.transition = '';
            });
        };

        const storedTheme = localStorage.getItem('theme');
        if (!storedTheme) {
            updateTheme(systemDark.matches);
        } else {
            document.documentElement.setAttribute('data-theme', storedTheme);
        }

        systemDark.addListener((e) => {
            if (!localStorage.getItem('theme')) {
                updateTheme(e.matches);
            }
        });

        window.toggleTheme = function() {
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            updateTheme(newTheme === 'dark');
        }
    });
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
    """Generate formal archive index"""
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

# ... (rest of the code remains identical to previous version)
