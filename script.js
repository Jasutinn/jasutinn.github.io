async function loadEntries() {
    const response = await fetch('https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO_NAME/contents/journal');
    const files = await response.json();
    
    const entriesList = document.getElementById("entries");
    files.forEach(file => {
        if (file.name.endsWith(".html")) {
            const filename = file.name.replace(".html", "").replace(/\d{4}-\d{2}-\d{2}-/, "").replace(/-/g, " ");
            const link = document.createElement("a");
            link.href = `journal/${file.name}`;
            link.textContent = filename;
            
            const listItem = document.createElement("li");
            listItem.appendChild(link);
            entriesList.appendChild(listItem);
        }
    });
}

loadEntries();