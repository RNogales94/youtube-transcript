import os
import datetime
from io import StringIO
from flask import Flask, request, jsonify, send_from_directory, make_response
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

def format_transcript_srt(transcript):
    """
    Convierte la transcripción en formato SRT.
    """
    srt_text = StringIO()
    for i, entry in enumerate(transcript, start=1):
        start = str(datetime.timedelta(seconds=int(entry['start']))).replace('.', ',')
        end = str(datetime.timedelta(seconds=int(entry['start'] + entry['duration']))).replace('.', ',')
        text = entry.get('text', '')

        srt_text.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    return srt_text.getvalue()

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_str = request.args.get('videoId')
    language = request.args.get('language')
    format_type = request.args.get('format', 'txt').lower()  # Nuevo parámetro para elegir formato

    if not video_str:
        return jsonify({'error': 'Falta el parámetro videoId'}), 400

    video_id = extract_video_id(video_str)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language] if language else None)

        if format_type == 'srt':
            transcript_text = format_transcript_srt(transcript)
            filename = f"transcript_{video_id}.srt"
            content_type = "application/x-subrip"
        else:
            # Formato TXT
            transcript_text = StringIO()
            for entry in transcript:
                text = entry.get('text', '')
                transcript_text.write(f"{text}\n")

            transcript_text.seek(0)
            transcript_text = transcript_text.read()
            filename = f"transcript_{video_id}.txt"
            content_type = "text/plain; charset=utf-8"

        response = make_response(transcript_text)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers["Content-Type"] = content_type
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
    app.run(debug=True, host='127.0.0.1', port=5000)
