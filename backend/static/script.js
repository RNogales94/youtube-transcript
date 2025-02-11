document.addEventListener("DOMContentLoaded", function () {
    const formatToggle = document.getElementById("format-toggle");
    const formatLabel = document.getElementById("format-label");
    const downloadButton = document.getElementById("download-button");

    // Función para actualizar el DOM cuando se cambia de formato
    function updateFormatUI() {
        const isSRT = formatToggle.checked;
        formatLabel.textContent = isSRT ? "SRT" : "TXT";
        
        // Cambiar la apariencia del botón para reflejar el formato
        downloadButton.textContent = `Descargar ${isSRT ? "SRT" : "TXT"}`;
        downloadButton.classList.toggle("srt-mode", isSRT);
    }

    // Evento al cambiar el formato
    formatToggle.addEventListener("change", updateFormatUI);

    const videoInput = document.getElementById("video-input");
    const languageSelect = document.getElementById("language-select");
    const errorMessage = document.getElementById("error-message");

    downloadButton.addEventListener("click", async function () {
        const videoId = extractVideoId(videoInput.value);
        const language = languageSelect.value;
        const format = formatToggle.checked ? "srt" : "txt";

        if (!videoId) {
            errorMessage.textContent = "Por favor ingresa un enlace válido.";
            return;
        }

        errorMessage.textContent = "";
        downloadButton.textContent = "Descargando...";
        downloadButton.disabled = true;

        let url = `/api/transcript?videoId=${encodeURIComponent(videoId)}&language=${language}&format=${format}`;

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Error al obtener el transcript.");

            const blob = await response.blob();
            const urlBlob = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = urlBlob;
            a.download = `transcript.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            errorMessage.textContent = error.message;
        } finally {
            updateFormatUI(); // Restaurar el botón con el formato correcto
            downloadButton.disabled = false;
        }
    });

    function extractVideoId(url) {
        const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&?/]+)/;
        const match = url.match(regex);
        return match ? match[1] : "";
    }

    // Iniciar con la configuración correcta
    updateFormatUI();
});
