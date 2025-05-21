from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, origins="*")

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
            
            progressive_formats = []  # video + audio
            video_only_formats = []   # video only

            for f in info.get('formats', []):
                if f.get('ext') != 'mp4' or not f.get('url'):
                    continue

                format_entry = {
                    'format_id': f.get('format_id'),
                    'format_note': f.get('format_note'),
                    'url': f.get('url'),
                    'height': f.get('height') or 0,
                    'has_audio': f.get('acodec') != 'none',
                    'has_video': f.get('vcodec') != 'none',
                }

                if format_entry['has_audio'] and format_entry['has_video']:
                    progressive_formats.append(format_entry)
                elif format_entry['has_video'] and not format_entry['has_audio']:
                    video_only_formats.append(format_entry)

            return jsonify({
                'title': info.get('title'),
                'progressive': progressive_formats,
                'video_only': video_only_formats
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
