document.addEventListener("DOMContentLoaded", function () {
    const videoInput = document.getElementById("video-input");
    const languageSelect = document.getElementById("language-select");
    const timestampsCheckbox = document.getElementById("timestamps-checkbox");
    const downloadButton = document.getElementById("download-button");
    const errorMessage = document.getElementById("error-message");

    downloadButton.addEventListener("click", async function () {
        const videoId = extractVideoId(videoInput.value);
        const language = languageSelect.value;
        const withTimestamps = timestampsCheckbox.checked;

        if (!videoId) {
            errorMessage.textContent = "Por favor ingresa un ID o enlace válido de YouTube.";
            return;
        }

        errorMessage.textContent = "";
        downloadButton.textContent = "Descargando...";
        downloadButton.disabled = true;

        let url = `/api/transcript?videoId=${encodeURIComponent(videoId)}&language=${language}&timestamps=${withTimestamps}`;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error("Error al obtener el transcript.");
            }

            const disposition = response.headers.get("Content-Disposition");
            let filename = "transcript.txt";
            if (disposition && disposition.includes("filename=")) {
                filename = disposition.split("filename=")[1].replace(/"/g, '');
            }

            const blob = await response.blob();
            const urlBlob = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = urlBlob;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            errorMessage.textContent = error.message;
        } finally {
            downloadButton.textContent = "Descargar Transcript";
            downloadButton.disabled = false;
        }
    });

    function extractVideoId(url) {
        const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&?/]+)/;
        const match = url.match(regex);
        return match ? match[1] : "";
    }
});
