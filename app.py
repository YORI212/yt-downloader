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
    'cookiefile': 'cookies.txt'  # 👈 Add this line
}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('ext') == 'mp4' and f.get('url'):
                    formats.append({
                        'format_id': f.get('format_id'),
                        'format_note': f.get('format_note'),
                        'url': f.get('url')
                    })
            return jsonify({'title': info.get('title'), 'formats': formats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Required for Render deployment
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
