from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import threading
import os

app = Flask(__name__)
CORS(app)

# Make sure 'static' folder exists
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')
os.makedirs(STATIC_FOLDER, exist_ok=True)

progress = {
    'status': 'idle',
    'percentage': 0,
    'filename': '',
    'url': '',
    'error': ''
}

@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(progress)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    def hook(d):
        if d['status'] == 'downloading':
            percent = float(d.get('_percent_str', '0.0').replace('%', '').strip())
            progress['status'] = 'downloading'
            progress['percentage'] = percent
            progress['filename'] = d.get('filename', '')
        elif d['status'] == 'finished':
            progress['status'] = 'finished'
            progress['percentage'] = 100

    def run_download():
        try:
            ydl_opts = {
                'progress_hooks': [hook],
                'outtmpl': os.path.join(STATIC_FOLDER, '%(title)s.%(ext)s'),
                'format': 'best[ext=mp4]/best',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url)
                filename = ydl.prepare_filename(info)
                short_name = os.path.basename(filename)
                progress['url'] = f'/static/{short_name}'
        except Exception as e:
            progress['status'] = 'error'
            progress['error'] = str(e)

    # Reset progress and start thread
    progress.update({
        'status': 'starting',
        'percentage': 0,
        'filename': '',
        'url': '',
        'error': ''
    })

    threading.Thread(target=run_download).start()
    return jsonify({'message': 'Download started'}), 202

# To serve downloaded files
@app.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory(STATIC_FOLDER, filename)

# Required for Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
