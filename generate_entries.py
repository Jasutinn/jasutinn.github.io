import os
import json
import markdown

# Paths
journal_folder = "journal"
entries_file = os.path.join(journal_folder, "entries.json")
css_file = "style.css"  # Global CSS file

entries = []
for filename in os.listdir(journal_folder):
    if filename.endswith(".md"):  # Only convert markdown files
        filepath = os.path.join(journal_folder, filename)
        
        # Read the Markdown file
        with open(filepath, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)

        # Generate HTML filename
        html_filename = filename.rsplit(".", 1)[0] + ".html"
        html_filepath = os.path.join(journal_folder, html_filename)

        # Wrap in a styled blog format
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{filename.replace('.md', '')}</title>
                <link rel="stylesheet" href="../{css_file}">
            </head>
            <body>
                <div class="blog-container">
                    <h1>{filename.replace('.md', '')}</h1>
                    <div class="blog-content">
                        {html_content}
                    </div>
                </div>
            </body>
            </html>
            """)

        # Add to JSON index
        entries.append({"title": filename.replace(".md", ""), "file": html_filename})

# Save entries.json
with open(entries_file, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=4)