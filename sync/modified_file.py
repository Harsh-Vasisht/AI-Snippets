import os
import hashlib
import secrets
from flask import Flask, request, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# App setup
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Helpers ---

def is_authorized(req):
    api_key = req.headers.get("X-API-KEY")
    return api_key and api_key == API_KEY

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_file_hash(filepath):
    # Use SHA-256 instead of MD5
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# --- Routes ---

@app.before_request
def check_api_key():
    if not is_authorized(request):
        abort(401, description="Unauthorized: Invalid or missing API key")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        safe_name = secure_filename(file.filename)
        unique_suffix = secrets.token_hex(4)
        final_filename = f"{unique_suffix}_{safe_name}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
        file.save(filepath)

        file_hash = generate_file_hash(filepath)

        return jsonify({
            'message': 'File uploaded',
            'filename': final_filename,
            'sha256': file_hash
        }), 201

    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({'files': files})

@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    safe_name = secure_filename(filename)
    full_path = os.path.join(UPLOAD_FOLDER, safe_name)

    if not os.path.exists(full_path):
        return jsonify({'message': 'File not found'}), 404

    return send_from_directory(UPLOAD_FOLDER, safe_name, as_attachment=True)

@app.route('/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    safe_name = secure_filename(filename)
    full_path = os.path.join(UPLOAD_FOLDER, safe_name)

    if not os.path.exists(full_path):
        return jsonify({'message': 'File not found'}), 404

    os.remove(full_path)
    return jsonify({'message': f'{safe_name} deleted'}), 200

# --- Run Server ---
if __name__ == '__main__':
    # Never run with debug=True in production
    app.run(debug=False, port=5000)
