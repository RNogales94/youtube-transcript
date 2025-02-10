import os
import datetime
from io import StringIO
from flask import Flask, request, jsonify, send_file, send_from_directory, make_response
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Se configura la carpeta estática (ahora frontend/public se copia a backend/static/)
app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)  # Habilita CORS para desarrollo

def extract_video_id(video_str):
    """
    Si el usuario pasa un enlace completo de YouTube (youtube.com o youtu.be),
    extrae el ID del video. De lo contrario, asume que 'video_str' es el ID.
    """
    video_str = video_str.strip()

    if "youtube.com" in video_str or "youtu.be" in video_str:
        parsed_url = urlparse(video_str)
        if 'youtube.com' in parsed_url.netloc:
            qs = parse_qs(parsed_url.query)
            if 'v' in qs:
                return qs['v'][0]
        if 'youtu.be' in parsed_url.netloc:
            return parsed_url.path.strip('/')
    
    return video_str

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_str = request.args.get('videoId')
    language = request.args.get('language')  
    timestamps_param = request.args.get('timestamps', 'true').lower()
    with_timestamps = timestamps_param in ('true', '1', 'yes')

    if not video_str:
        return jsonify({'error': 'Falta el parámetro videoId'}), 400

    video_id = extract_video_id(video_str)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language] if language else None)

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
        response.headers['Content-Disposition'] = f'attachment; filename=transcript_{video_id}.txt'
        response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para servir archivos estáticos (HTML, CSS, JS)
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
