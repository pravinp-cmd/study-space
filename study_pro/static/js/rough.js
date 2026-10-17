const editor = document.getElementById("rough-text");
const status = document.getElementById("save-status");
const wordCount = document.getElementById("word-count");
const clearButton = document.getElementById("clear-button");
const downloadButton = document.getElementById("download-button");

const storageKey = "study-space-rough-notes";

function updateWordCount() {
  const words = editor.value.trim()
    ? editor.value.trim().split(/\s+/).length
    : 0;

  wordCount.textContent = words;
}

function saveText() {
  localStorage.setItem(storageKey, editor.value);
  status.textContent = "Saved";
  updateWordCount();
}

editor.value = localStorage.getItem(storageKey) || "";
updateWordCount();

editor.addEventListener("input", () => {
  status.textContent = "Saving…";
  window.clearTimeout(editor.saveTimer);
  editor.saveTimer = window.setTimeout(saveText, 250);
});

clearButton.addEventListener("click", () => {
  if (!editor.value) return;

  if (window.confirm("Clear all rough notes?")) {
    editor.value = "";
    localStorage.removeItem(storageKey);
    status.textContent = "Cleared";
    updateWordCount();
  }
});

downloadButton.addEventListener("click", () => {
  const file = new Blob([editor.value], {
    type: "text/plain;charset=utf-8",
  });

  const url = URL.createObjectURL(file);
  const link = document.createElement("a");
  link.href = url;
  link.download = "study-rough-notes.txt";
  link.click();

  URL.revokeObjectURL(url);
});