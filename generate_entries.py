import os
import json
import markdown

# Paths
journal = "journal"
entries_file = os.path.join(journal, "entries.json")
css_file = "style.css"  # Global CSS file

entries = []  # Start fresh every time

# Scan the journal folder for .md files
for filename in os.listdir(journal):
    if filename.endswith(".md", ".*"):  # Only process markdown files
        filepath = os.path.join(journal, filename)
        
        # Read the Markdown file
        with open(filepath, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)

        # Generate HTML filename
        html_filename = filename.rsplit(".", 1)[0] + ".html"
        html_filepath = os.path.join(journal, html_filename)

        # Create the formatted HTML file
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

        # Add the new entry to the JSON list
        entries.append({"title": filename.replace(".md", ""), "file": html_filename})

# Overwrite entries.json with the updated list
with open(entries_file, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=4)

print("Journal entries successfully updated!")