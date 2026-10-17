const contentInput = document.getElementById("content");
const charCount = document.getElementById("char-count");

if (contentInput && charCount) {
  const updateCount = () => {
    charCount.textContent = contentInput.value.length;
  };

  contentInput.addEventListener("input", updateCount);
  updateCount();
}

document.querySelectorAll(".delete-form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const confirmed = window.confirm("Delete this note?");
    if (!confirmed) event.preventDefault();
  });
});