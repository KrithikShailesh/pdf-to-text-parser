from flask import Flask, request, jsonify
from flask_cors import CORS
from resume_parser import extract_text_from_pdf
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/parse", methods=["POST"])
def parse_resume_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded file
    file_path = os.path.join("/tmp", file.filename)
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
