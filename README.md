# Thesis Abstract Evaluator

Thesis Abstract Evaluator is a Flask web app that scores thesis abstracts using a rubric-based engine and a lightweight ML signal.

## Features
- Evaluate pasted abstract text (`/evaluate`)
- Upload and evaluate PDF or DOCX (`/evaluate-file`)
- Category-wise rubric scoring with comments
- Strength/improvement feedback and rewrite suggestions
- Extracted preview text display

## Tech Stack
- Python 3.11+
- Flask
- scikit-learn
- PyPDF2
- python-docx

## Project Structure
- `app.py`: Flask app, scoring logic, extraction pipeline
- `train_model.py`: small training script for the demo model
- `templates/index.html`: UI template
- `static/style.css`: styling
- `static/script.js`: frontend logic
- `model.pkl`, `vectorizer.pkl`: trained artifacts
- `tests/test_app.py`: route-level smoke tests

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run
```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Deploy on Render
This repository is now set up for Render with:
- `render.yaml` for a GitHub-connected web service
- `Procfile` and `wsgi.py` for a production Gunicorn entrypoint
- `runtime.txt` to pin the Python version

Steps:
1. Push this project to your GitHub repository.
2. Open Render and create a new Blueprint deployment from that repository, or create a Web Service from the same repo.
3. Render will install dependencies from `requirements.txt` and start the app with `gunicorn wsgi:app`.
4. After the first deploy finishes, open the Render URL for the live app.

## Run Tests
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Re-train the Demo Model
If you update training examples in `train_model.py`, regenerate artifacts with:

```bash
python train_model.py
```

## Notes
- Recommended abstract length is 120 to 300 words.
- If PDF/DOCX support fails, ensure `PyPDF2` and `python-docx` are installed.
