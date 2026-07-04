// ---- Configuration ----
const API_BASE_URL = "http://localhost:8000";

// ---- Elements ----
const reportForm = document.getElementById("reportForm");
const input = document.getElementById("subjectInput");
const btn = document.getElementById("submitBtn");
const btnLabel = document.getElementById("submitBtnLabel");
const heroMessage = document.querySelector(".hero");
const userPrompt = document.getElementById("userPrompt");
const statusRow = document.getElementById("statusRow");
const statusText = document.getElementById("statusText");
const errorBox = document.getElementById("errorBox");
const resultBox = document.getElementById("resultBox");
const previewLink = document.getElementById("previewLink");
const downloadBtn = document.getElementById("downloadBtn");

let currentPdfUrl = null;
let currentQuery = "report";

function resetPanels() {
  statusRow.hidden = true;
  errorBox.hidden = true;
  resultBox.hidden = true;
  errorBox.textContent = "";
}

function setLoading(isLoading) {
  btn.disabled = isLoading;
  btnLabel.textContent = isLoading ? "…" : "↑"; 
}

async function generateReport(e) {
  if (e) e.preventDefault();

  const query = input.value.trim();
  if (!query) {
    resetPanels();
    errorBox.hidden = false;
    errorBox.textContent = "Please enter a company name or website.";
    return;
  }

  resetPanels();
  setLoading(true);
  
  if (heroMessage) heroMessage.style.display = "none";
  if (userPrompt) {
    userPrompt.textContent = `Research request: ${query}`;
    userPrompt.hidden = false;
  }

  statusRow.hidden = false;
  statusText.textContent = `Researching "${query}"… this can take up to a minute.`;
  currentQuery = query;

  try {
    const res = await fetch(`${API_BASE_URL}/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const message = data?.detail || `Request failed (${res.status})`;
      throw new Error(message);
    }

    currentPdfUrl = `${API_BASE_URL}${data.pdf_url}`;
    previewLink.href = currentPdfUrl;
    previewLink.target = "_blank"; 

    statusRow.hidden = true;
    resultBox.hidden = false;
    input.value = "";
  } catch (err) {
    statusRow.hidden = true;
    errorBox.hidden = false;
    errorBox.textContent = `Something went wrong: ${err.message}`;
  } finally {
    setLoading(false);
  }
}

async function downloadPdf() {
  if (!currentPdfUrl) return;
  const originalLabel = downloadBtn.textContent;
  downloadBtn.textContent = "Downloading…";
  try {
    const res = await fetch(currentPdfUrl);
    if (!res.ok) throw new Error(`Download failed (${res.status})`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const safeName = currentQuery.replace(/[^a-z0-9]+/gi, "_").toLowerCase();
    a.href = url;
    a.download = `${safeName}_report.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    errorBox.hidden = false;
    errorBox.textContent = `Download failed: ${err.message}`;
  } finally {
    downloadBtn.textContent = originalLabel;
  }
}

if (reportForm) {
  reportForm.addEventListener("submit", generateReport);
}
downloadBtn.addEventListener("click", downloadPdf);