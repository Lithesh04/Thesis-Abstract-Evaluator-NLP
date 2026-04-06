function renderList(items) {
    return items.map((item) => `<li>${item}</li>`).join("");
}

function renderBars(dimensions) {
    return dimensions
        .map(
            (dimension) => `
                <div class="bar-item">
                    <div class="bar-meta">
                        <strong>${dimension.label}</strong>
                        <span>${dimension.score}/${dimension.max_score}</span>
                    </div>
                    <div class="bar-track">
                        <div class="bar-fill" style="width: ${dimension.percentage}%;"></div>
                    </div>
                    <p class="dimension-comment">${dimension.comment}</p>
                </div>
            `
        )
        .join("");
}

function renderSuggestions(suggestions) {
    return suggestions
        .map(
            (item) => `
                <li>
                    <span class="priority">${item.priority}</span>
                    <strong>${item.dimension}:</strong> ${item.suggestion}
                </li>
            `
        )
        .join("");
}

function renderResult(data) {
    const result = document.getElementById("result");
    const sourcePill = data.source ? `<span class="pill">Source: ${data.source}</span>` : "";
    const mlSignalText = data.ml_signal ? `<span class="pill">ML signal: ${data.ml_signal}</span>` : "";

    result.classList.remove("hidden");
    result.innerHTML = `
        <div class="score-row">
            <div class="score-card">
                <p class="score-value">${data.score}/100</p>
                <p class="score-label">${data.rating}</p>
            </div>
            <div class="meta">
                <span class="pill">Word count: ${data.word_count}</span>
                <span class="pill">Sentences: ${data.sentence_count}</span>
                ${sourcePill}
                ${mlSignalText}
            </div>
        </div>

        <h2 class="section-title">Score Breakdown</h2>
        <div class="chart-grid">
            <section class="chart-card">
                <h3>Category chart</h3>
                <div class="bar-list">${renderBars(data.dimensions)}</div>
            </section>
            <section class="feedback-box">
                <h3>Targeted rewrite suggestions</h3>
                <ol class="suggestion-list">${renderSuggestions(data.rewrite_suggestions)}</ol>
            </section>
        </div>

        <h2 class="section-title">Feedback</h2>
        <div class="feedback-columns">
            <section class="feedback-box">
                <h3>Strengths</h3>
                <ul>${renderList(data.strengths)}</ul>
            </section>
            <section class="feedback-box">
                <h3>Improvements</h3>
                <ul>${renderList(data.improvements)}</ul>
            </section>
        </div>

        <section class="preview-box">
            <h3>Extracted text preview</h3>
            <p>${data.extracted_preview || "Preview unavailable."}</p>
        </section>
    `;
}

function showError(message) {
    const result = document.getElementById("result");
    result.classList.remove("hidden");
    result.innerHTML = `<p class="error">${message}</p>`;
}

async function evaluateTextRequest() {
    const text = document.getElementById("abstract").value.trim();

    if (!text) {
        throw new Error("Please enter an abstract before evaluating.");
    }

    const response = await fetch("/evaluate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ abstract: text })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Unable to evaluate the abstract.");
    }

    renderResult(data);
}

async function evaluateFileRequest() {
    const input = document.getElementById("file-input");

    if (!input.files.length) {
        throw new Error("Please choose a PDF or DOCX file before evaluating.");
    }

    const formData = new FormData();
    formData.append("file", input.files[0]);

    const response = await fetch("/evaluate-file", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Unable to evaluate the uploaded file.");
    }

    document.getElementById("abstract").value = data.extracted_preview || "";
    renderResult(data);
}

function setButtonState(buttonId, isLoading, loadingText, idleText) {
    const button = document.getElementById(buttonId);
    button.disabled = isLoading;
    button.textContent = isLoading ? loadingText : idleText;
}

async function evaluateAbstract() {
    setButtonState("evaluate-button", true, "Evaluating...", "Evaluate Text");

    try {
        await evaluateTextRequest();
    } catch (error) {
        showError(error.message);
    } finally {
        setButtonState("evaluate-button", false, "Evaluating...", "Evaluate Text");
    }
}

async function evaluateFile() {
    setButtonState("upload-button", true, "Extracting...", "Evaluate File");

    try {
        await evaluateFileRequest();
    } catch (error) {
        showError(error.message);
    } finally {
        setButtonState("upload-button", false, "Extracting...", "Evaluate File");
    }
}
