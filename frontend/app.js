const API_BASE_URL =
  window.location.protocol === "file:" ? "http://localhost:8000" : "";

const MAX_FILE_SIZE = 500 * 1024 * 1024;
const VALID_EXTENSIONS = /\.(mp4|avi|mov|mkv|flv|wmv|webm|m4v|mpg|mpeg)$/i;
const VALID_TYPES = [
  "video/mp4",
  "video/avi",
  "video/quicktime",
  "video/x-matroska",
  "video/x-flv",
  "video/x-ms-wmv",
  "video/webm",
  "video/mpeg",
];

let selectedFile = null;
let transcriptionData = null;
let transcribeController = null;

const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const transcribeBtn = document.getElementById("transcribeBtn");
const modelSelect = document.getElementById("modelSelect");
const languageSelect = document.getElementById("languageSelect");
const inlineError = document.getElementById("inlineError");
const statusBanner = document.getElementById("statusBanner");
const statusBannerText = document.getElementById("statusBannerText");
const retryConnectionBtn = document.getElementById("retryConnectionBtn");

const uploadSection = document.getElementById("uploadSection");
const processingSection = document.getElementById("processingSection");
const resultsSection = document.getElementById("resultsSection");
const errorSection = document.getElementById("errorSection");

const processingStatus = document.getElementById("processingStatus");
const errorMessage = document.getElementById("errorMessage");
const transcriptionContent = document.getElementById("transcriptionContent");
const detectedLanguage = document.getElementById("detectedLanguage");
const videoDuration = document.getElementById("videoDuration");
const modelUsed = document.getElementById("modelUsed");
const segmentsList = document.getElementById("segmentsList");

const copyBtn = document.getElementById("copyBtn");
const downloadTxtBtn = document.getElementById("downloadTxtBtn");
const downloadSrtBtn = document.getElementById("downloadSrtBtn");
const downloadJsonBtn = document.getElementById("downloadJsonBtn");
const newTranscriptionBtn = document.getElementById("newTranscriptionBtn");
const retryBtn = document.getElementById("retryBtn");
const cancelBtn = document.getElementById("cancelBtn");
const uploadTitle = document.getElementById("uploadTitle");
const uploadHint = document.getElementById("uploadHint");

uploadArea.addEventListener("click", () => fileInput.click());
uploadArea.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});
fileInput.addEventListener("change", handleFileSelect);
transcribeBtn.addEventListener("click", handleTranscribe);
copyBtn.addEventListener("click", handleCopy);
downloadTxtBtn.addEventListener("click", () => handleDownload("txt"));
downloadSrtBtn.addEventListener("click", () => handleDownload("srt"));
downloadJsonBtn.addEventListener("click", () => handleDownload("json"));
newTranscriptionBtn.addEventListener("click", () => resetApp(true));
retryBtn.addEventListener("click", () => {
  showSection("upload");
  if (selectedFile) {
    transcribeBtn.disabled = false;
  }
});
cancelBtn.addEventListener("click", cancelTranscription);
retryConnectionBtn.addEventListener("click", checkBackendConnection);

uploadArea.addEventListener("dragover", (event) => {
  event.preventDefault();
  uploadArea.classList.add("drag-over");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("drag-over");
});

uploadArea.addEventListener("drop", (event) => {
  event.preventDefault();
  uploadArea.classList.remove("drag-over");
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelect({ target: { files } });
  }
});

function showInlineError(message) {
  inlineError.textContent = message;
  inlineError.classList.remove("hidden");
}

function clearInlineError() {
  inlineError.textContent = "";
  inlineError.classList.add("hidden");
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (!VALID_TYPES.includes(file.type) && !VALID_EXTENSIONS.test(file.name)) {
    showInlineError("That file type is not supported. Choose a video file.");
    fileInput.value = "";
    return;
  }

  if (file.size > MAX_FILE_SIZE) {
    showInlineError("File is larger than 500MB. Choose a smaller video.");
    fileInput.value = "";
    return;
  }

  clearInlineError();
  selectedFile = file;
  displaySelectedFile(file);
  transcribeBtn.disabled = false;
}

function displaySelectedFile(file) {
  const fileSize = (file.size / (1024 * 1024)).toFixed(2);
  uploadTitle.textContent = "File selected";
  uploadHint.textContent = `${file.name} (${fileSize} MB)`;
}

function buildFormData() {
  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("model", modelSelect.value);
  if (languageSelect.value) {
    formData.append("language", languageSelect.value);
  }
  return formData;
}

async function handleTranscribe() {
  if (!selectedFile) return;

  transcribeController = new AbortController();
  showSection("processing");
  processingStatus.textContent = "Uploading…";
  const transcribeLabel = `Transcribing with ${modelSelect.value} model…`;
  const statusTimer = window.setTimeout(() => {
    processingStatus.textContent = transcribeLabel;
  }, 600);

  try {
    const response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: "POST",
      body: buildFormData(),
      signal: transcribeController.signal,
    });
    window.clearTimeout(statusTimer);
    processingStatus.textContent = transcribeLabel;

    if (!response.ok) {
      let detail = "Transcription failed";
      try {
        const error = await response.json();
        detail = error.detail || detail;
      } catch {
        detail = `Transcription failed (${response.status})`;
      }
      throw new Error(detail);
    }

    transcriptionData = await response.json();
    displayResults();
  } catch (error) {
    if (error.name === "AbortError") {
      showSection("upload");
      return;
    }
    console.error("Transcription error:", error);
    showError(error.message || "Failed to transcribe video. Please try again.");
  } finally {
    window.clearTimeout(statusTimer);
    transcribeController = null;
  }
}

function cancelTranscription() {
  if (transcribeController) {
    transcribeController.abort();
  }
  showSection("upload");
}

function displayResults() {
  showSection("results");
  transcriptionContent.textContent = transcriptionData.text;
  detectedLanguage.textContent = (transcriptionData.language || "unknown").toUpperCase();
  videoDuration.textContent = formatDuration(transcriptionData.duration);
  modelUsed.textContent = transcriptionData.model_used;
  displaySegments(transcriptionData.segments || []);
}

function displaySegments(segments) {
  segmentsList.innerHTML = "";
  segments.forEach((segment) => {
    const segmentDiv = document.createElement("div");
    segmentDiv.className = "segment-item";

    const timeDiv = document.createElement("div");
    timeDiv.className = "segment-time";
    timeDiv.textContent = `${formatTimestamp(segment.start)} → ${formatTimestamp(segment.end)}`;

    const textDiv = document.createElement("div");
    textDiv.className = "segment-text";
    textDiv.textContent = segment.text.trim();

    segmentDiv.appendChild(timeDiv);
    segmentDiv.appendChild(textDiv);
    segmentsList.appendChild(segmentDiv);
  });
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(transcriptionData.text);
    copyBtn.textContent = "Copied";
    setTimeout(() => {
      copyBtn.textContent = "Copy";
    }, 2000);
  } catch (error) {
    copyBtn.textContent = "Copy failed";
    setTimeout(() => {
      copyBtn.textContent = "Copy";
    }, 2000);
  }
}

function downloadStem() {
  const name = selectedFile?.name || "transcription";
  return name.replace(/\.[^.]+$/, "") || "transcription";
}

function triggerDownload(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function formatSrtTimestamp(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  const whole = Math.floor(secs);
  const millis = Math.round((secs - whole) * 1000);
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(whole).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
}

function generateSrt(segments) {
  return segments
    .map((segment, index) => {
      const start = formatSrtTimestamp(segment.start);
      const end = formatSrtTimestamp(segment.end);
      const text = (segment.text || "").trim();
      return `${index + 1}\n${start} --> ${end}\n${text}\n`;
    })
    .join("\n");
}

function handleDownload(format) {
  if (!transcriptionData) return;
  const stem = downloadStem();

  if (format === "txt") {
    triggerDownload(transcriptionData.text, `${stem}.txt`, "text/plain");
    return;
  }

  if (format === "json") {
    triggerDownload(
      JSON.stringify(transcriptionData, null, 2),
      `${stem}.json`,
      "application/json"
    );
    return;
  }

  triggerDownload(
    generateSrt(transcriptionData.segments || []),
    `${stem}.srt`,
    "application/x-subrip"
  );
}

function showSection(section) {
  uploadSection.classList.add("hidden");
  processingSection.classList.add("hidden");
  resultsSection.classList.add("hidden");
  errorSection.classList.add("hidden");

  const sections = {
    upload: uploadSection,
    processing: processingSection,
    results: resultsSection,
    error: errorSection,
  };
  sections[section].classList.remove("hidden");
}

function showError(message) {
  errorMessage.textContent = String(message || "").replace(
    /^Transcription failed:\s*/i,
    ""
  );
  showSection("error");
}

function resetApp(clearFile) {
  if (clearFile) {
    selectedFile = null;
    fileInput.value = "";
    transcribeBtn.disabled = true;
    uploadTitle.textContent = "Drop your video here";
    uploadHint.textContent = "or press Enter to browse";
  }
  transcriptionData = null;
  clearInlineError();
  showSection("upload");
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  return `${secs}s`;
}

function formatTimestamp(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${minutes.toString().padStart(2, "0")}:${secs
    .toString()
    .padStart(2, "0")}.${ms.toString().padStart(3, "0")}`;
}

async function checkBackendConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error("unhealthy");
    }
    statusBanner.classList.add("hidden");
  } catch (error) {
    statusBannerText.textContent =
      "Cannot reach the transcription server. Start EchoScribe and try again.";
    statusBanner.classList.remove("hidden");
  }
}

checkBackendConnection();
