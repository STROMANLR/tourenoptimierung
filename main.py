from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return 'Tourenoptimierung Backend läuft!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Keine Datei hochgeladen'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    # Hier müsste dein Code zur PDF-Verarbeitung und Tourenoptimierung stehen
    # Beispielhafte Dummy-Antwort
    return jsonify({
        'tour': ['Startpunkt: Schulstraße 98, 26903 Surwold', 'Adresse A', 'Adresse B', 'Adresse C']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)