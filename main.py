from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import re
import os
from werkzeug.utils import secure_filename
from optimize import optimize_route

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return 'Tourenoptimierung Backend mit ORS läuft!'

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
            blocks = page.get_text("blocks")
            for b in sorted(blocks, key=lambda x: x[1]):
                text = b[4].strip()
                if not text:
                    continue
                if 'Tour: T-PBG' in text:
                    current_tour = 'T-PBG'
                    continue
                elif 'Tour: T-WRL' in text:
                    current_tour = 'T-WRL'
                    continue
                elif 'Tour: T-DER' in text:
                    current_tour = 'T-DER'
                    continue
                elif 'Tour: T-HAR' in text:
                    current_tour = 'T-HAR'
                    continue

                if current_tour and re.search(r'\b\d{5}\b', text):
                    parts = text.split()
                    plz_index = next((i for i, p in enumerate(parts) if re.fullmatch(r'\d{5}', p)), -1)
                    if plz_index > 0 and plz_index - 1 >= 0:
                        try:
                            plz = parts[plz_index]
                            ort = parts[plz_index + 1] if len(parts) > plz_index + 1 else ''
                            strasse = ' '.join(parts[:plz_index - 1])
                            hausnummer = parts[plz_index - 1]
                            full_address = f"{strasse} {hausnummer}, {plz} {ort}".strip()
                            addresses_by_tour[current_tour].append(full_address)
                        except IndexError:
                            continue

    start_address = 'Schulstraße 98 26903 Surwold'
    result = {}
    for tour, addresses in addresses_by_tour.items():
        if addresses:
            full_list = [start_address] + addresses
            sorted_list = optimize_route(full_list)
            result[tour] = sorted_list

    if not result:
        return jsonify({'error': 'Keine vollständigen Adressen gefunden!'}), 400

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)