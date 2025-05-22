from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import os
import subprocess

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
        video_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_video.mp4")
        audio_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_audio.m4a")
        output_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_merged.mp4")

        ydl_video_opts = {
            'format': 'bestvideo[ext=mp4]',
            'outtmpl': video_path,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True
        }

        ydl_audio_opts = {
            'format': 'bestaudio[ext=m4a]',
            'outtmpl': audio_path,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True
        }

        # Download best video
        with yt_dlp.YoutubeDL(ydl_video_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Download best audio
        with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
            ydl.download([url])

        # Merge using ffmpeg
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]
        subprocess.run(cmd, check=True)

        # Optional: return a direct download URL instead
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
