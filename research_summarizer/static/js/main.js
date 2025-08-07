// static/js/main.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("AI Summarizer JS loaded.");
    
    // Optional: Show filename after upload
    const input = document.getElementById("pdf_file");
    if (input) {
        input.addEventListener("change", function () {
            const fileLabel = document.querySelector("label[for='pdf_file']");
            if (this.files.length > 0) {
                fileLabel.innerText = `Selected: ${this.files[0].name}`;
            }
        });
    }
});
