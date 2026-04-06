import os

from flask import Flask, jsonify, render_template, request

from evaluator import evaluate_abstract, extract_text_from_upload


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json(silent=True) or {}
    text = (data.get("abstract") or "").strip()

    if not text:
        return jsonify({"error": "Please enter an abstract before evaluating."}), 400

    return jsonify(evaluate_abstract(text))


@app.route("/evaluate-file", methods=["POST"])
def evaluate_file():
    upload = request.files.get("file")

    if upload is None or not upload.filename:
        return jsonify({"error": "Please choose a PDF or DOCX file to upload."}), 400

    try:
        extracted_text = extract_text_from_upload(upload)
        result = evaluate_abstract(extracted_text)
        result["source"] = upload.filename
        return jsonify(result)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "").lower() == "true",
    )
