import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from io import BytesIO
import pickle
import re

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


BASE_DIR = Path(__file__).resolve().parent


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


RUBRIC = {
    "length": {
        "label": "Length and density",
        "weight": 15,
        "ideal_min": 120,
        "ideal_max": 300,
    },
    "objective": {
        "label": "Problem and objective",
        "weight": 18,
        "keywords": ["aim", "objective", "purpose", "problem", "research", "study", "propose"],
    },
    "methodology": {
        "label": "Methodology",
        "weight": 18,
        "keywords": ["method", "methodology", "approach", "framework", "algorithm", "analysis", "model"],
    },
    "results": {
        "label": "Results and evidence",
        "weight": 18,
        "keywords": ["result", "findings", "performance", "evaluation", "accuracy", "improvement", "outcome"],
    },
    "conclusion": {
        "label": "Conclusion and contribution",
        "weight": 16,
        "keywords": ["conclusion", "conclude", "contribution", "impact", "significance", "future work"],
    },
    "clarity": {
        "label": "Clarity and cohesion",
        "weight": 15,
    },
}


REWRITE_TEMPLATES = {
    "length": "Expand the abstract into 4 compact parts: context, objective, method, and result. Keep it between 120 and 300 words.",
    "objective": "Open with one sentence that states the research problem and the exact aim of the study.",
    "methodology": "Add one sentence explaining the method, dataset, model, or experimental procedure used in the work.",
    "results": "Add one result sentence with a measurable outcome such as accuracy, percentage improvement, error reduction, or comparison.",
    "conclusion": "Close with the main contribution or implication of the work and, if suitable, one short future-work note.",
    "clarity": "Rewrite long sentences into shorter ones and connect them in a logical order: problem, method, result, conclusion.",
}


def load_artifacts():
    try:
        with open(BASE_DIR / "model.pkl", "rb") as model_file:
            model = pickle.load(model_file)
        with open(BASE_DIR / "vectorizer.pkl", "rb") as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
        return model, vectorizer
    except FileNotFoundError:
        return None, None


model, vectorizer = load_artifacts()


def tokenize(text):
    return re.findall(r"\b[\w-]+\b", text.lower())


def split_sentences(text):
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text.strip()) if item.strip()]
    return sentences


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def score_length(word_count):
    if 120 <= word_count <= 300:
        return 15, "Length fits the expected range for a thesis abstract."
    if 100 <= word_count < 120 or 301 <= word_count <= 330:
        return 11, "Length is close to the target range, but can be refined."
    if 80 <= word_count < 100 or 331 <= word_count <= 380:
        return 7, "Length is somewhat imbalanced and should be adjusted."
    return 3, "Abstract is too short or too long for a strong academic summary."


def score_keyword_dimension(text, dimension_id):
    config = RUBRIC[dimension_id]
    matches = [keyword for keyword in config["keywords"] if keyword in text]

    if len(matches) >= 3:
        return config["weight"], f"{config['label']} is communicated clearly."
    if len(matches) == 2:
        return int(config["weight"] * 0.8), f"{config['label']} is present with reasonable clarity."
    if len(matches) == 1:
        return int(config["weight"] * 0.55), f"{config['label']} appears, but it needs more detail."
    return int(config["weight"] * 0.22), f"{config['label']} is weak or missing."


def score_clarity(text, sentences, word_count):
    if not sentences:
        return 0, "No readable abstract content was detected."

    average_sentence_length = word_count / len(sentences)
    transition_hits = len(
        [word for word in ["therefore", "thus", "based on", "using", "results", "finally"] if word in text]
    )
    long_sentences = sum(1 for sentence in sentences if len(sentence.split()) > 32)

    score = 5

    if 3 <= len(sentences) <= 6:
        score += 4
    if 14 <= average_sentence_length <= 28:
        score += 4
    if transition_hits >= 1:
        score += 2
    if long_sentences == 0:
        score += 2
    elif long_sentences > 2:
        score -= 2

    score = max(3, min(RUBRIC["clarity"]["weight"], score))

    if score >= 13:
        comment = "The abstract reads clearly and follows a sensible flow."
    elif score >= 9:
        comment = "The abstract is readable, but cohesion can still improve."
    else:
        comment = "Sentence flow and clarity need improvement."

    return score, comment


def ml_signal(text):
    if not model or not vectorizer:
        return None

    prediction = model.predict(vectorizer.transform([text]))[0]
    return "positive" if prediction == 1 else "negative"


def build_dimension_result(dimension_id, score, comment):
    return {
        "id": dimension_id,
        "label": RUBRIC[dimension_id]["label"],
        "score": score,
        "max_score": RUBRIC[dimension_id]["weight"],
        "comment": comment,
        "percentage": round((score / RUBRIC[dimension_id]["weight"]) * 100),
    }


def generate_feedback(text, word_count, dimensions):
    strengths = []
    improvements = []

    if word_count >= 120:
        strengths.append("The abstract has enough substance to summarize the research meaningfully.")
    else:
        improvements.append("Expand the abstract so it covers the study more completely before final submission.")

    if re.search(r"\d", text):
        strengths.append("The abstract includes a measurable signal, which strengthens academic credibility.")
    else:
        improvements.append("Add at least one quantitative or comparative result to support the claims.")

    for item in dimensions:
        if item["percentage"] >= 80:
            strengths.append(item["comment"])
        elif item["percentage"] < 60:
            improvements.append(item["comment"])

    if not strengths:
        strengths.append("The draft has the basic starting material needed for revision.")

    if not improvements:
        improvements.append("The abstract is balanced overall; focus next on precision and academic style.")

    return list(dict.fromkeys(strengths))[:4], list(dict.fromkeys(improvements))[:5]


def generate_rewrite_suggestions(dimensions):
    suggestions = []

    for item in dimensions:
        if item["percentage"] < 70:
            suggestions.append(
                {
                    "dimension": item["label"],
                    "priority": "High" if item["percentage"] < 50 else "Medium",
                    "suggestion": REWRITE_TEMPLATES[item["id"]],
                }
            )

    if not suggestions:
        suggestions.append(
            {
                "dimension": "Overall polish",
                "priority": "Low",
                "suggestion": "Refine wording, remove repetition, and make the research contribution more specific.",
            }
        )

    return suggestions


def extract_text_from_pdf(file_bytes):
    if PdfReader is None:
        raise ValueError("PDF support is not installed. Install PyPDF2 to enable PDF uploads.")

    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text_from_docx(file_bytes):
    if Document is None:
        raise ValueError("DOCX support is not installed. Install python-docx to enable DOCX uploads.")

    document = Document(BytesIO(file_bytes))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_upload(upload):
    filename = (upload.filename or "").lower()
    file_bytes = upload.read()

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")

    cleaned_text = normalize_whitespace(text)

    if not cleaned_text:
        raise ValueError("No readable text was extracted from the uploaded file.")

    return cleaned_text


def evaluate_abstract(text):
    cleaned_text = normalize_whitespace(text)
    normalized_text = cleaned_text.lower()
    tokens = tokenize(cleaned_text)
    sentences = split_sentences(cleaned_text)
    word_count = len(tokens)

    dimensions = []

    length_score, length_comment = score_length(word_count)
    dimensions.append(build_dimension_result("length", length_score, length_comment))

    for dimension_id in ["objective", "methodology", "results", "conclusion"]:
        score, comment = score_keyword_dimension(normalized_text, dimension_id)
        dimensions.append(build_dimension_result(dimension_id, score, comment))

    clarity_score, clarity_comment = score_clarity(normalized_text, sentences, word_count)
    dimensions.append(build_dimension_result("clarity", clarity_score, clarity_comment))

    total_score = sum(item["score"] for item in dimensions)
    signal = ml_signal(cleaned_text)

    if signal == "positive":
        total_score = min(100, total_score + 3)
    elif signal == "negative":
        total_score = max(0, total_score - 3)

    if word_count < 60:
        total_score = min(total_score, 55)
    elif word_count < 90:
        total_score = min(total_score, 68)

    if total_score >= 85:
        rating = "Excellent"
    elif total_score >= 70:
        rating = "Good"
    elif total_score >= 50:
        rating = "Average"
    else:
        rating = "Needs improvement"

    strengths, improvements = generate_feedback(normalized_text, word_count, dimensions)
    rewrite_suggestions = generate_rewrite_suggestions(dimensions)

    return {
        "score": total_score,
        "rating": rating,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "dimensions": dimensions,
        "strengths": strengths,
        "improvements": improvements,
        "rewrite_suggestions": rewrite_suggestions,
        "ml_signal": signal,
        "extracted_preview": cleaned_text[:450],
    }


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
