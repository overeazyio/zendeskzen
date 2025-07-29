document.addEventListener("DOMContentLoaded", () => {
    const extractBtn = document.getElementById("extract-btn");
    const jsonFilesList = document.getElementById("json-files");
    const xmlFilesList = document.getElementById("xml-files");
    const fileContent = document.getElementById("file-content");

    const fetchFiles = async () => {
        const response = await fetch("/files");
        const files = await response.json();
        jsonFilesList.innerHTML = "";
        xmlFilesList.innerHTML = "";
        files.json_files.forEach(file => {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = `/files/json/${file}`;
            a.textContent = file;
            a.target = "_blank";
            li.appendChild(a);
            jsonFilesList.appendChild(li);
        });
        files.xml_files.forEach(file => {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = `/files/xml/${file}`;
            a.textContent = file;
            a.target = "_blank";
            li.appendChild(a);
            xmlFilesList.appendChild(li);
        });
    };

    extractBtn.addEventListener("click", async () => {
        const response = await fetch("/extract", { method: "POST" });
        const data = await response.json();
        alert(data.message);
        fetchFiles();
    });

    fetchFiles();
});
