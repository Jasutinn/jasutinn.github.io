import os
import json
from bs4 import BeautifulSoup

# Directory containing journal entries
journal_dir = "./journal"

# Output JSON file
output_file = "entries.json"

# List to store journal data
entries = []

# Ensure the directory exists
if not os.path.exists(journal_dir):
    os.makedirs(journal_dir)

# Loop through HTML files in the directory
for filename in os.listdir(journal_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(journal_dir, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            title = soup.title.string if soup.title else filename
            content = soup.body.prettify() if soup.body else ""

            entries.append({
                "title": title,
                "filename": filename,
                "content": content
            })

# Save entries to JSON
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(entries, json_file, indent=4, ensure_ascii=False)

print(f"Converted {len(entries)} journal entries to JSON.")