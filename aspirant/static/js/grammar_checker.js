document.addEventListener("DOMContentLoaded", function () {
  const htmlStructure = `
    <div class="grammar-checker-container">
      <h2>Advanced NLP Grammar & Spelling Checker</h2>
      <div class="input-area">
        <textarea id="userEssay" placeholder="Paste your essay here..."></textarea>
      </div>
      <div class="controls">
        <button id="checkButton">Analyze Text</button>
        <button id="clearButton">Clear</button>
      </div>
      <div class="results-area">
        <h3>Analysis Results</h3>
        <div id="statistics" class="stats-panel"></div>
        <div id="errorCount" class="summary"></div>
        <div id="resultsList"></div>
      </div>
    </div>
  `;

  document.getElementById("grammar-checker-mount-point").innerHTML = htmlStructure;

  document.getElementById("checkButton").addEventListener("click", analyzeText);
  document.getElementById("clearButton").addEventListener("click", clearAll);

  async function analyzeText() {
    const text = document.getElementById("userEssay").value.trim();

    if (!text) {
      alert("Please enter some text to analyze.");
      return;
    }

    // Count words and sentences
    const wordCount = text.split(/\s+/).filter(w => w).length;
    const sentenceCount = text.split(/[.!?]+/).filter(s => s.trim()).length;

    // Display basic text statistics
    document.getElementById("statistics").innerHTML = `
      <div class="stat-item">
        <span class="stat-value">${wordCount}</span>
        <span class="stat-label">Words</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">${sentenceCount}</span>
        <span class="stat-label">Sentences</span>
      </div>
    `;

    // Call the LanguageTool API for grammar checking
    try {
      const response = await fetch("https://api.languagetool.org/v2/check", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `text=${encodeURIComponent(text)}&language=en-US`
      });

      const data = await response.json();

      if (data.matches.length > 0) {
        let errorHTML = data.matches.map(match => `
          <div class="error-item">
            <span class="error-type">${match.rule.issueType.toUpperCase()}:</span>
            <strong>${text.substring(match.offset, match.offset + match.length)}</strong>
            <br>
            <span class="suggestion">Suggested: ${match.replacements.map(r => r.value).join(", ")}</span>
            <br>
            <span class="explanation">${match.message}</span>
          </div>
        `).join("");

        document.getElementById("resultsList").innerHTML = errorHTML;
        document.getElementById("errorCount").innerHTML = `Total Errors: ${data.matches.length}`;
      } else {
        document.getElementById("resultsList").innerHTML = `<p>No errors found.</p>`;
        document.getElementById("errorCount").innerHTML = `Total Errors: 0`;
      }
    } catch (error) {
      console.error("Error checking grammar:", error);
      alert("Failed to analyze text. Please check your internet connection.");
    }
  }

  function clearAll() {
    document.getElementById("userEssay").value = "";
    document.getElementById("statistics").innerHTML = "";
    document.getElementById("errorCount").innerHTML = "";
    document.getElementById("resultsList").innerHTML = "";
  }
});
