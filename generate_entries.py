import os
import json

journal_folder = "journal"
entries = []

for file in os.listdir(journal_folder):
    if file.endswith(".html"):
        entries.append({"filename": file, "title": file.replace(".html", "").capitalize()})

with open(os.path.join(journal_folder, "entries.json"), "w") as f:
    json.dump(entries, f, indent=4)

print("Updated entries.json successfully.")