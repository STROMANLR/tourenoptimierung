from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # CORS erlauben

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
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    addresses_by_tour = {"T-PBG": [], "T-WRL": [], "T-DER": [], "T-HAR": []}
    current_tour = None

    with fitz.open(file_path) as pdf:
        for page in pdf:
            text = page.get_text()
            lines = text.split('\n')
            for line in lines:
                if 'Tour: T-PBG' in line:
                    current_tour = 'T-PBG'
                elif 'Tour: T-WRL' in line:
                    current_tour = 'T-WRL'
                elif 'Tour: T-DER' in line:
                    current_tour = 'T-DER'
                elif 'Tour: T-HAR' in line:
                    current_tour = 'T-HAR'
                elif 'https://www.google.de/maps/place/' in line and current_tour:
                    match = re.search(r'place/(.*?)/@', line)
                    if match:
                        address = match.group(1).replace('+', ' ').replace(',', ', ').strip()
                        addresses_by_tour[current_tour].append(address)

    start_address = 'Schulstraße 98 26903 Surwold'
    result = {}
    for tour, addresses in addresses_by_tour.items():
        if addresses:
            result[tour] = [start_address] + addresses

    if not result:
        return jsonify({'error': 'Keine Adressen gefunden! Bitte überprüfen Sie die hochgeladene PDF.'}), 400

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)