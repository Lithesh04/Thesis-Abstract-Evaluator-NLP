# Thesis Abstract Evaluator

Thesis Abstract Evaluator can run either as a Flask web app or as a Streamlit app. It scores thesis abstracts using a rubric-based engine and a lightweight ML signal.

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

## Run Flask Locally
```bash
python flask_app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Run Streamlit Locally
```bash
streamlit run streamlit_app.py
```

Open the local Streamlit URL shown in the terminal.

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

## Deploy on Streamlit Cloud
Use `app.py` or `streamlit_app.py` as the app entrypoint on Streamlit Cloud.

Important:
- `app.py` now points to the Streamlit UI, so existing Streamlit Cloud setups that still use `app.py` will work.
- `flask_app.py` is the Flask server entry file.
- Streamlit Cloud should install packages from `requirements.txt` automatically.
- `gunicorn` is only installed on non-Windows environments because it is used for Linux-based production hosting, not local Windows runs.
- This repo is pinned to Python `3.12.10` because the current Streamlit dependency set is more reliable there than on Python `3.13`.
- If you previously deployed an older commit, redeploy from the latest `main` branch so Streamlit picks up the new entrypoint.

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
