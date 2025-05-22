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
        output_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_output.mp4")
        temp_video = os.path.join(DOWNLOAD_DIR, f"{video_id}_video.mp4")
        temp_audio = os.path.join(DOWNLOAD_DIR, f"{video_id}_audio.m4a")

        # First, try downloading best combined progressive format (video+audio)
        ydl_opts_combined = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts_combined) as ydl:
            info = ydl.extract_info(url, download=True)

        # If file exists, return directly
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)

        # If combined format is not available, download video and audio separately and merge

        # Download video-only (bestvideo)
        ydl_opts_video = {
            'format': 'bestvideo[ext=mp4]/bestvideo',
            'outtmpl': temp_video,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        # Download best audio
        ydl_opts_audio = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': temp_audio,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([url])

        # Merge video and audio
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-i', temp_audio,
            '-c:v', 'copy',
            '-c:a', 'aac',
            output_path
        ]
        subprocess.run(cmd, check=True)

        # Cleanup temp files
        os.remove(temp_video)
        os.remove(temp_audio)

        # Return merged file
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
