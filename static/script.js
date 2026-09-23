const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("error");
const results = document.getElementById("results");

dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) handleFile(fileInput.files[0]);
});

async function handleFile(file) {
  errorBox.classList.add("hidden");
  results.classList.add("hidden");
  loading.classList.remove("hidden");

  const formData = new FormData();
  formData.append("image", file);

  try {
    const res = await fetch("/analyze", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Something went wrong.");
    }

    renderResults(data);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
  }
}

function renderResults(data) {
  document.getElementById("annotatedImg").src = data.annotated_url;
  document.getElementById("elaImg").src = data.ela_url;
  document.getElementById("verdictText").textContent = data.verdict;

  const reasonsList = document.getElementById("reasonsList");
  reasonsList.innerHTML = "";
  if (data.reasons.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No specific flags raised.";
    reasonsList.appendChild(li);
  } else {
    data.reasons.forEach((reason) => {
      const li = document.createElement("li");
      li.textContent = reason;
      reasonsList.appendChild(li);
    });
  }

  const tbody = document.querySelector("#metadataTable tbody");
  tbody.innerHTML = "";
  const entries = Object.entries(data.metadata);
  if (entries.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = "<td colspan='2'>No EXIF metadata present.</td>";
    tbody.appendChild(row);
  } else {
    entries.forEach(([key, value]) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${key}</td><td>${value}</td>`;
      tbody.appendChild(row);
    });
  }

  results.classList.remove("hidden");
}
