import os
import datetime
from io import StringIO
from flask import Flask, request, jsonify, send_file, send_from_directory, make_response
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Se configura la carpeta estática (la build de React)
app = Flask(__name__, static_folder="../frontend/build", static_url_path="")
CORS(app)  # Habilita CORS para desarrollo

def extract_video_id(video_str):
    """
    Si el usuario pasa un enlace completo de YouTube (youtube.com o youtu.be),
    extrae el ID del video. De lo contrario, asume que 'video_str' es el ID.
    """
    # Normalizamos el string
    video_str = video_str.strip()

    # Comprobamos si es un enlace
    if "youtube.com" in video_str or "youtu.be" in video_str:
        parsed_url = urlparse(video_str)
        # Caso youtube.com
        if 'youtube.com' in parsed_url.netloc:
            qs = parse_qs(parsed_url.query)
            # Si existe el parámetro 'v', lo devolvemos
            if 'v' in qs:
                return qs['v'][0]
        # Caso youtu.be
        if 'youtu.be' in parsed_url.netloc:
            # El path contiene el ID
            return parsed_url.path.strip('/')
    # Si no es un enlace reconocible, lo tratamos directamente como ID
    return video_str

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_str = request.args.get('videoId')
    language = request.args.get('language')  # Opcional
    timestamps_param = request.args.get('timestamps', 'true').lower()
    with_timestamps = timestamps_param in ('true', '1', 'yes')

    if not video_str:
        return jsonify({'error': 'Falta el parámetro videoId'}), 400

    # Obtener el ID real (o el que se asuma) desde el posible link
    video_id = extract_video_id(video_str)

    try:
        # Obtener el transcript, opcionalmente en un idioma específico
        if language:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

        transcript_text = StringIO()
        for entry in transcript:
            text = entry.get('text', '')
            if with_timestamps:
                start = entry.get('start', 0)
                duration = entry.get('duration', 0)
                inicio = str(datetime.timedelta(seconds=int(start)))
                fin = str(datetime.timedelta(seconds=int(start + duration)))
                transcript_text.write(f"[{inicio} - {fin}] {text}\n")
            else:
                transcript_text.write(f"{text}\n")

        transcript_text.seek(0)
        response = make_response(transcript_text.read())
        # Nombre de archivo final
        response.headers['Content-Disposition'] = f'attachment; filename=transcript_{video_id}.txt'
        response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para servir la aplicación React
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # En desarrollo, para producción se recomienda utilizar un servidor WSGI (por ejemplo Gunicorn)
    app.run(debug=True, host='0.0.0.0', port=5000)
