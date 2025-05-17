from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best[ext=mp4]/best',
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = {'low': [], 'medium': [], 'high': []}

            for f in info.get('formats', []):
                if f.get('ext') == 'mp4' and f.get('url'):
                    height = f.get('height') or 0
                    format_entry = {
                        'format_id': f.get('format_id'),
                        'format_note': f.get('format_note'),
                        'url': f.get('url'),
                        'height': height  # ✅ make sure this line has a comma above it
                    }

                    if height < 480:
                        formats['low'].append(format_entry)
                    elif 480 <= height < 720:
                        formats['medium'].append(format_entry)
                    elif height >= 720:
                        formats['high'].append(format_entry)

            return jsonify({
                'title': info.get('title'),
                'formats': formats
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
