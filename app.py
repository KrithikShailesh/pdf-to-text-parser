from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from resume_parser import extract_text_from_pdf
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

import jwt

load_dotenv()

SHARED_SECRET = os.getenv('SHARED_SECRET')
JWT_SECRET = os.getenv('JWT_SECRET')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')
ALLOWED_ORIGINS_LIST = [origin.strip().rstrip("/") for origin in ALLOWED_ORIGINS.split(",")] if ALLOWED_ORIGINS != "*" else ["*"]

if not SHARED_SECRET:
    raise ValueError("No SHARED_SECRET set for Flask application. Security risk.")
if not JWT_SECRET:
    raise ValueError("No JWT_SECRET set for Flask application. Security risk.")

app = Flask(__name__)
# Enable CORS with specific origins if provided, otherwise allow all (default)
CORS(app, resources={r"/parse": {"origins": ALLOWED_ORIGINS.split(",") if ALLOWED_ORIGINS != "*" else "*"}})

# Set maximum file size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def require_auth(view_function):
    def wrapper(*args, **kwargs):

        # 1. Shared Secret Verification
        if request.headers.get('X-Secret-Key') != SHARED_SECRET:
            abort(401, description="Unauthorized: Invalid key")

        # 2. JWT Verification
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
             abort(401, description="Unauthorized: Invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            # Verify the token using the secret and HS256 algorithm
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            abort(401, description="Unauthorized: Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Unauthorized: Invalid token")

        return view_function(*args, **kwargs)
    return wrapper

@app.route("/parse", methods=["POST"])
@require_auth
def parse_resume_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join("/tmp", filename)
    os.makedirs("/tmp", exist_ok=True)
    file.save(file_path)

    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(file_path)
        
        # Delete the file after processing
        os.remove(file_path)
    
    except Exception as e:
        # Ensure file is deleted even if extraction fails
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500
    
    # Parse resume

    return jsonify({"text": resume_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
