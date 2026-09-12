const elements = {
  runtimeMode: document.getElementById("runtimeMode"),
  documentCount: document.getElementById("documentCount"),
  chunkCount: document.getElementById("chunkCount"),
  sessionCount: document.getElementById("sessionCount"),
  documentsList: document.getElementById("documentsList"),
  citationsList: document.getElementById("citationsList"),
  responseCard: document.getElementById("responseCard"),
  answerOutput: document.getElementById("answerOutput"),
  confidenceBadge: document.getElementById("confidenceBadge"),
  strategyBadge: document.getElementById("strategyBadge"),
  statusPill: document.getElementById("statusPill"),
  questionInput: document.getElementById("questionInput"),
  sessionId: document.getElementById("sessionId"),
  audience: document.getElementById("audience"),
};

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

function setStatus(message) {
  elements.statusPill.textContent = message;
}

function renderOverview(data) {
  elements.runtimeMode.textContent = data.runtime_mode;
  elements.documentCount.textContent = data.document_count;
  elements.chunkCount.textContent = data.chunk_count;
  elements.sessionCount.textContent = data.sessions_tracked;
}

function renderDocuments(documents) {
  if (!documents.length) {
    elements.documentsList.innerHTML = '<p class="empty-state">No documents indexed yet.</p>';
    return;
  }

  elements.documentsList.innerHTML = documents
    .map(
      (doc) => `
        <article class="document-item">
          <h3>${doc.title}</h3>
          <p class="documents-meta">${doc.source_path}</p>
          <p class="document-tags">${doc.department} • ${doc.chunk_count} chunks</p>
        </article>
      `,
    )
    .join("");
}

function renderCitations(citations) {
  if (!citations.length) {
    elements.citationsList.innerHTML =
      '<p class="empty-state">No evidence returned for the last request.</p>';
    return;
  }

  elements.citationsList.innerHTML = citations
    .map(
      (citation) => `
        <article class="citation-item">
          <h3>${citation.title}</h3>
          <p class="citation-path">${citation.source_path}</p>
          <p>${citation.excerpt}</p>
          <p class="citation-score">score ${citation.score.toFixed(2)}</p>
        </article>
      `,
    )
    .join("");
}

async function loadDashboard() {
  const [overview, documents] = await Promise.all([
    request("/api/v1/overview"),
    request("/api/v1/documents"),
  ]);
  renderOverview(overview);
  renderDocuments(documents);
}

document.getElementById("refreshButton").addEventListener("click", async () => {
  setStatus("Refreshing");
  try {
    await loadDashboard();
    setStatus("Ready");
  } catch (error) {
    setStatus("Refresh failed");
    console.error(error);
  }
});

document.getElementById("seedButton").addEventListener("click", async () => {
  setStatus("Indexing seed docs");
  try {
    await request("/api/v1/ingest/seed", { method: "POST" });
    await loadDashboard();
    setStatus("Seed complete");
  } catch (error) {
    setStatus("Seed failed");
    console.error(error);
  }
});

document.getElementById("manualIngestForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Ingesting text");

  const payload = {
    title: document.getElementById("manualTitle").value,
    department: document.getElementById("manualDepartment").value,
    tags: document
      .getElementById("manualTags")
      .value.split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    body: document.getElementById("manualBody").value,
  };

  try {
    await request("/api/v1/ingest/manual", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    event.target.reset();
    await loadDashboard();
    setStatus("Knowledge added");
  } catch (error) {
    setStatus("Ingestion failed");
    console.error(error);
  }
});

document.getElementById("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Uploading files");

  const input = document.getElementById("uploadInput");
  const formData = new FormData();
  Array.from(input.files).forEach((file) => formData.append("files", file));

  try {
    await request("/api/v1/ingest/files", {
      method: "POST",
      body: formData,
    });
    input.value = "";
    await loadDashboard();
    setStatus("Upload complete");
  } catch (error) {
    setStatus("Upload failed");
    console.error(error);
  }
});

document.getElementById("chatForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Thinking");

  try {
    const response = await request("/api/v1/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: elements.questionInput.value,
        session_id: elements.sessionId.value || "default",
        audience: elements.audience.value || "operations",
      }),
    });

    elements.responseCard.classList.remove("hidden");
    elements.answerOutput.textContent = response.blocked
      ? `${response.answer}\n\nReason: ${response.block_reason || "Request blocked"}`
      : response.runtime_note
        ? `${response.answer}\n\nNote: ${response.runtime_note}`
        : response.answer;
    elements.confidenceBadge.textContent = `confidence ${response.confidence}`;
    elements.strategyBadge.textContent = response.retrieval_strategy;
    renderCitations(response.citations);
    await loadDashboard();
    setStatus("Response ready");
  } catch (error) {
    setStatus("Query failed");
    elements.responseCard.classList.remove("hidden");
    elements.answerOutput.textContent =
      "The query reached the server, but the backend returned an error. If documents are indexed and the runtime is enabled, the most likely cause is a local model/provider connectivity or configuration problem.";
    elements.confidenceBadge.textContent = "confidence unknown";
    elements.strategyBadge.textContent = "error";
    console.error(error);
  }
});

document.querySelectorAll(".chip").forEach((button) => {
  button.addEventListener("click", async () => {
    elements.questionInput.value = button.dataset.question;
    document.getElementById("chatForm").requestSubmit();
  });
});

loadDashboard().catch((error) => {
  setStatus("Initialization failed");
  console.error(error);
});
