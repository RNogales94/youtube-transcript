import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import './App.css';

import { FaGithub, FaEnvelope, FaTelegramPlane } from 'react-icons/fa';

function App() {
  const [videoId, setVideoId] = useState('');
  const [language, setLanguage] = useState('es');
  const [withTimestamps, setWithTimestamps] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDownload = async () => {
    if (!videoId.trim()) {
      setError('Por favor ingresa el ID o el enlace del video de YouTube.');
      return;
    }
    setError('');
    setLoading(true);

    let url = `/api/transcript?videoId=${encodeURIComponent(videoId.trim())}`;
    if (language.trim()) {
      url += `&language=${language.trim()}`;
    }
    url += `&timestamps=${withTimestamps ? 'true' : 'false'}`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        let errMsg = 'Error al obtener el transcript.';
        try {
          const errData = await response.json();
          if (errData.error) errMsg = errData.error;
        } catch (e) {
          // Ignoramos si no se puede parsear
        }
        throw new Error(errMsg);
      }

      const disposition = response.headers.get('Content-Disposition');
      let filename = 'transcript.txt';
      if (disposition && disposition.indexOf('filename=') !== -1) {
        filename = disposition.split('filename=')[1].replace(/"/g, '');
      }

      const blob = await response.blob();
      const urlBlob = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlBlob;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {/* Metadatos para SEO con React Helmet */}
      <Helmet>
        <title>Descargar Transcript de YouTube</title>
        <meta
          name="description"
          content="Descarga el transcript de un video de YouTube en formato .txt, con o sin marcas de tiempo. Ideal para subtítulos o guiones."
        />
        <meta
          name="keywords"
          content="YouTube, transcript, subtítulos, guion, descargar, video"
        />
      </Helmet>

      {/* Logo reemplazado por emojis */}
      <div className="emoji-logo" aria-label="Vídeo y Texto">
        <span role="img" aria-label="Claqueta" className="emoji-big">
          🎬
        </span>
        <span className="emoji-plus">+</span>
        <span role="img" aria-label="Bloc de notas" className="emoji-big">
          📝
        </span>
      </div>

      <h1 className="title">Descargar Transcript</h1>

      <main className="form-box">
        <label htmlFor="video-input">Enlace del video de YouTube:</label>
        <input
          id="video-input"
          type="text"
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
          placeholder="Ej: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        />

        <label htmlFor="language-select">Idioma del video (o subtítulos autogenerados):</label>
        <select
          id="language-select"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="language-select"
        >
          <option value="en">🇺🇸 Inglés</option>
          <option value="es">🇪🇸 Español</option>
          <option value="pt">🇵🇹 Portugués</option>
          <option value="ru">🇷🇺 Ruso</option>
          <option value="ja">🇯🇵 Japonés</option>
          <option value="ko">🇰🇷 Coreano</option>
          <option value="fr">🇫🇷 Francés</option>
          <option value="de">🇩🇪 Alemán</option>
          <option value="tr">🇹🇷 Turco</option>
          <option value="hi">🇮🇳 Hindi</option>
        </select>

        <div className="timestamps-checkbox">
          <label>
            <input
              type="checkbox"
              checked={withTimestamps}
              onChange={(e) => setWithTimestamps(e.target.checked)}
            />
            Incluir marcas de tiempo
          </label>
        </div>

        <button onClick={handleDownload} disabled={loading} className="download-button">
          {loading ? 'Descargando...' : 'Descargar Transcript'}
        </button>

        {error && <p className="error-message">{error}</p>}
      </main>

      <footer className="footer">
        <p>
          Desarrollado por <strong>Rafael Nogales</strong>.
        </p>
        <p className="mini-disclaimer">
          Organiza una llamada gratuita conmigo para ayudarte en tus proyectos.
        </p>
        <p>
          <a
            href="https://github.com/RNogales94"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            <FaGithub className="icon" /> GitHub
          </a>
          &nbsp;|&nbsp;
          <a
            href="mailto:rnogales.dev@gmail.com"
            className="footer-link"
          >
            <FaEnvelope className="icon" /> Email
          </a>
          &nbsp;|&nbsp;
          <a
            href="https://t.me/RNogales"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            <FaTelegramPlane className="icon" /> Telegram
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
