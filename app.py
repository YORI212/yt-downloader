from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/mission-api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestvideo+bestaudio/best',
            'cookiefile': 'cookies.txt',
            'nocheckcertificate': True,
            'noplaylist': True,
            'cachedir': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_only = []
            progressive = []

            for f in info.get('formats', []):
                if f.get('ext') != 'mp4' or not f.get('url'):
                    continue

                format_data = {
                    'format_id': f.get('format_id'),
                    'format_note': f.get('format_note') or f.get('resolution'),
                    'url': f.get('url'),
                    'height': f.get('height') or 0
                }

                if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                    video_only.append(format_data)
                elif f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    progressive.append(format_data)

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'progressive': progressive,
                'video_only': video_only
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

