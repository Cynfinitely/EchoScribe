// Configuration
const API_BASE_URL = "http://localhost:8000";

// State
let selectedFile = null;
let transcriptionData = null;

// DOM Elements
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const transcribeBtn = document.getElementById("transcribeBtn");
const modelSelect = document.getElementById("modelSelect");
const languageSelect = document.getElementById("languageSelect");

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

// Event Listeners
uploadArea.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", handleFileSelect);
transcribeBtn.addEventListener("click", handleTranscribe);
copyBtn.addEventListener("click", handleCopy);
downloadTxtBtn.addEventListener("click", () => handleDownload("txt"));
downloadSrtBtn.addEventListener("click", () => handleDownload("srt"));
downloadJsonBtn.addEventListener("click", () => handleDownload("json"));
newTranscriptionBtn.addEventListener("click", resetApp);
retryBtn.addEventListener("click", resetApp);

// Drag and Drop
uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("drag-over");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("drag-over");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("drag-over");
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelect({ target: { files } });
  }
});

// File Selection Handler
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file type
  const validTypes = [
    "video/mp4",
    "video/avi",
    "video/quicktime",
    "video/x-matroska",
    "video/x-flv",
    "video/x-ms-wmv",
    "video/webm",
    "video/mpeg",
  ];

  if (
    !validTypes.includes(file.type) &&
    !file.name.match(/\.(mp4|avi|mov|mkv|flv|wmv|webm|mpg|mpeg)$/i)
  ) {
    showError("Invalid file type. Please select a video file.");
    return;
  }

  // Validate file size (500MB max)
  const maxSize = 500 * 1024 * 1024;
  if (file.size > maxSize) {
    showError("File size exceeds 500MB limit. Please select a smaller file.");
    return;
  }

  selectedFile = file;
  displaySelectedFile(file);
  transcribeBtn.disabled = false;
}

// Display Selected File
function displaySelectedFile(file) {
  const fileName = file.name;
  const fileSize = (file.size / (1024 * 1024)).toFixed(2);

  // Update upload area
  const uploadIcon = uploadArea.querySelector(".upload-icon");
  const h2 = uploadArea.querySelector("h2");
  const firstP = uploadArea.querySelector("p");

  uploadIcon.textContent = "✅";
  h2.textContent = "File Selected";
  firstP.innerHTML = `<strong>${fileName}</strong> (${fileSize} MB)`;
}

// Handle Transcription
async function handleTranscribe() {
  if (!selectedFile) return;

  // Show processing section
  showSection("processing");

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("model", modelSelect.value);

  const language = languageSelect.value;
  if (language) {
    formData.append("language", language);
  }

  try {
    processingStatus.textContent = `Transcribing with ${modelSelect.value} model...`;

    const response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Transcription failed");
    }

    transcriptionData = await response.json();
    displayResults();
  } catch (error) {
    console.error("Transcription error:", error);
    showError(error.message || "Failed to transcribe video. Please try again.");
  }
}

// Display Results
function displayResults() {
  showSection("results");

  // Display transcription text
  transcriptionContent.textContent = transcriptionData.text;

  // Display metadata
  detectedLanguage.textContent = transcriptionData.language.toUpperCase();
  videoDuration.textContent = formatDuration(transcriptionData.duration);
  modelUsed.textContent = transcriptionData.model_used;

  // Display segments
  displaySegments(transcriptionData.segments);
}

// Display Segments
function displaySegments(segments) {
  segmentsList.innerHTML = "";

  segments.forEach((segment, index) => {
    const segmentDiv = document.createElement("div");
    segmentDiv.className = "segment-item";

    const timeDiv = document.createElement("div");
    timeDiv.className = "segment-time";
    timeDiv.textContent = `${formatTimestamp(
      segment.start
    )} → ${formatTimestamp(segment.end)}`;

    const textDiv = document.createElement("div");
    textDiv.className = "segment-text";
    textDiv.textContent = segment.text.trim();

    segmentDiv.appendChild(timeDiv);
    segmentDiv.appendChild(textDiv);
    segmentsList.appendChild(segmentDiv);
  });
}

// Copy to Clipboard
async function handleCopy() {
  try {
    await navigator.clipboard.writeText(transcriptionData.text);
    copyBtn.textContent = "✅ Copied!";
    setTimeout(() => {
      copyBtn.textContent = "📋 Copy";
    }, 2000);
  } catch (error) {
    alert("Failed to copy to clipboard");
  }
}

// Download Handler
async function handleDownload(format) {
  let content, filename, mimeType;

  switch (format) {
    case "txt":
      content = transcriptionData.text;
      filename = `transcription_${Date.now()}.txt`;
      mimeType = "text/plain";
      break;

    case "json":
      content = JSON.stringify(transcriptionData, null, 2);
      filename = `transcription_${Date.now()}.json`;
      mimeType = "application/json";
      break;

    case "srt":
      // Request SRT format from backend
      await downloadSRT();
      return;
  }

  // Create and trigger download
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Download SRT (requires separate API call)
async function downloadSRT() {
  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("model", modelSelect.value);

  const language = languageSelect.value;
  if (language) {
    formData.append("language", language);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/transcribe/srt`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to generate SRT");
    }

    const data = await response.json();
    const blob = new Blob([data.srt], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcription_${Date.now()}.srt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("SRT download error:", error);
    alert("Failed to generate SRT file. Please try again.");
  }
}

// Utility Functions
function showSection(section) {
  uploadSection.classList.add("hidden");
  processingSection.classList.add("hidden");
  resultsSection.classList.add("hidden");
  errorSection.classList.add("hidden");

  switch (section) {
    case "upload":
      uploadSection.classList.remove("hidden");
      break;
    case "processing":
      processingSection.classList.remove("hidden");
      break;
    case "results":
      resultsSection.classList.remove("hidden");
      break;
    case "error":
      errorSection.classList.remove("hidden");
      break;
  }
}

function showError(message) {
  errorMessage.textContent = message;
  showSection("error");
}

function resetApp() {
  selectedFile = null;
  transcriptionData = null;
  fileInput.value = "";
  transcribeBtn.disabled = true;

  // Reset upload area
  const uploadIcon = uploadArea.querySelector(".upload-icon");
  const h2 = uploadArea.querySelector("h2");
  const firstP = uploadArea.querySelector("p");

  uploadIcon.textContent = "📹";
  h2.textContent = "Drop your video here";
  firstP.textContent = "or click to browse";

  showSection("upload");
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

function formatTimestamp(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${minutes.toString().padStart(2, "0")}:${secs
    .toString()
    .padStart(2, "0")}.${ms.toString().padStart(3, "0")}`;
}

// Check backend connection on load
async function checkBackendConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      console.warn("Backend connection check failed");
    }
  } catch (error) {
    console.warn(
      "Could not connect to backend. Make sure the server is running at",
      API_BASE_URL
    );
  }
}

// Initialize
checkBackendConnection();
