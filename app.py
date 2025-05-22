from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = '/tmp/downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/mission-api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        video_id = str(uuid.uuid4())
        output_base = os.path.join(DOWNLOAD_DIR, f"{video_id}")
        output_path = f"{output_base}.mp4"

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{output_base}.%(ext)s',
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
