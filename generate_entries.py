import os
import json

journal_folder = "journal"
entries_file = os.path.join(journal_folder, "entries.json")

entries = []
for filename in os.listdir(journal_folder):
    if filename.endswith(".txt") or filename.endswith(".md"):
        filepath = os.path.join(journal_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Generate an HTML file
        html_filename = filename.rsplit(".", 1)[0] + ".html"
        html_filepath = os.path.join(journal_folder, html_filename)
        
        # Wrap content in HTML
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{html_filename}</title>
            </head>
            <body>
                <h1>{filename}</h1>
                <p>{content.replace("\n", "<br>")}</p>
            </body>
            </html>
            """)

        # Add to JSON index
        entries.append({"title": filename, "file": html_filename})

# Save entries.json
with open(entries_file, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=4)