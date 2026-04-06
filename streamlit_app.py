import streamlit as st

from evaluator import evaluate_abstract, extract_text_from_file


st.set_page_config(page_title="Thesis Abstract Evaluator", page_icon="📘", layout="wide")

st.title("Thesis Abstract Evaluator")
st.caption("Evaluate thesis abstracts with rubric-based scoring, feedback, and rewrite suggestions.")


def show_result(data):
    metric_col, meta_col = st.columns([1, 2])
    with metric_col:
        st.metric("Score", f"{data['score']}/100", data["rating"])
    with meta_col:
        labels = [
            f"Words: {data['word_count']}",
            f"Sentences: {data['sentence_count']}",
        ]
        if data.get("source"):
            labels.append(f"Source: {data['source']}")
        if data.get("ml_signal"):
            labels.append(f"ML signal: {data['ml_signal']}")
        st.write(" | ".join(labels))

    st.subheader("Score Breakdown")
    for item in data["dimensions"]:
        st.write(f"**{item['label']}**  ({item['score']}/{item['max_score']})")
        st.progress(item["percentage"] / 100)
        st.caption(item["comment"])

    strengths_col, improvements_col = st.columns(2)
    with strengths_col:
        st.subheader("Strengths")
        for entry in data["strengths"]:
            st.write(f"- {entry}")
    with improvements_col:
        st.subheader("Improvements")
        for entry in data["improvements"]:
            st.write(f"- {entry}")

    st.subheader("Rewrite Suggestions")
    for item in data["rewrite_suggestions"]:
        st.write(f"- **{item['priority']}** | **{item['dimension']}**: {item['suggestion']}")

    st.subheader("Extracted Preview")
    st.write(data.get("extracted_preview") or "Preview unavailable.")


input_mode = st.radio("Choose input type", ["Paste abstract text", "Upload PDF or DOCX"], horizontal=True)

if input_mode == "Paste abstract text":
    abstract = st.text_area("Abstract", height=260, placeholder="Paste the thesis abstract here...")
    if st.button("Evaluate Text", type="primary"):
        if not abstract.strip():
            st.error("Please enter an abstract before evaluating.")
        else:
            show_result(evaluate_abstract(abstract))
else:
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])
    if st.button("Evaluate File", type="primary"):
        if uploaded_file is None:
            st.error("Please choose a PDF or DOCX file before evaluating.")
        else:
            try:
                extracted_text = extract_text_from_file(uploaded_file.name, uploaded_file.getvalue())
                result = evaluate_abstract(extracted_text)
                result["source"] = uploaded_file.name
                show_result(result)
            except ValueError as error:
                st.error(str(error))
