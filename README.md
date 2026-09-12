# AtlasIQ Enterprise Knowledge Assistant

An enterprise-grade **Retrieval-Augmented Generation (RAG) knowledge assistant** designed for internal policy, operations, employee onboarding, and incident-response workflows.

AtlasIQ combines **hybrid retrieval**, **LangChain-powered answer orchestration**, **grounded citations**, **prompt-injection guardrails**, persistent document indexing, and a browser-based enterprise console into a single application.

---

## Overview

Enterprise teams often need to search across internal policies, operational documentation, onboarding material, and incident-response knowledge.

AtlasIQ provides a centralized interface where users can upload or seed enterprise knowledge and ask natural-language questions.

The system retrieves relevant knowledge, ranks the results, and produces grounded answers with supporting citations.

### Core Workflow

```text
                    ┌──────────────────────┐
                    │    Browser Console   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    │        Layer         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Enterprise Knowledge│
                    │       Engine         │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌────────────┐   ┌─────────────┐
        │Guardrails │    │  Chunker + │   │   Hybrid    │
        │           │    │   Loader   │   │  Retriever  │
        └───────────┘    └─────┬──────┘   └──────┬──────┘
                               │                 │
                               └────────┬────────┘
                                        ▼
                               ┌─────────────────┐
                               │ Registry Store  │
                               └────────┬────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ Optional LangChain│
                              │      Runtime      │
                              └─────────┬──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │   LLM Provider     │
                              └────────────────────┘
```

---

## Key Features

- 🧠 Enterprise knowledge question answering
- 🔎 Hybrid document retrieval
- 📚 Grounded answers based on indexed enterprise knowledge
- 📌 Ranked citations
- 🛡️ Prompt-injection and data-exfiltration guardrails
- 💾 Persistent document indexing
- 💬 Session-based conversation history
- 📄 Multiple knowledge-file formats
- ✍️ Manual knowledge ingestion
- 🌱 Seeded enterprise demo knowledge
- 🔄 Offline deterministic mode
- 🤖 Optional LangChain LLM runtime
- 🖥️ Browser-based enterprise console
- ❤️ Health and system overview information

The project documentation describes hybrid retrieval, LangChain orchestration, guardrails, persistent storage, citations, and a layered architecture as core parts of the application. :contentReference[oaicite:1]{index=1}

---

## Enterprise Use Cases

AtlasIQ is designed around internal enterprise workflows such as:

### 📋 Internal Policies

Ask questions about company policies and retrieve relevant supporting information.

### ⚙️ Operations

Search operational knowledge and procedures using natural-language questions.

### 👋 Employee Onboarding

Help employees find information related to security onboarding and internal procedures.

### 🚨 Incident Response

Retrieve relevant operational knowledge for incident-response workflows.

### 🚀 Release Readiness

Search enterprise deployment and release-readiness documentation.

---

## Supported Knowledge Files

AtlasIQ supports the following knowledge-file formats:

| Format | Supported |
|---|---|
| `.txt` | ✅ |
| `.md` | ✅ |
| `.json` | ✅ |
| `.csv` | ✅ |

Users can upload multiple supported knowledge files or paste knowledge directly into the application. :contentReference[oaicite:2]{index=2}

---

## Retrieval Architecture

AtlasIQ uses a hybrid retrieval approach.

The documented retrieval system combines:

```text
Semantic-Style Retrieval
          +
Lexical Scoring
          │
          ▼
   Hybrid Retrieval
          │
          ▼
 Ranked Knowledge Results
```

This allows the application to work in its local/default setup even before external model credentials are configured. :contentReference[oaicite:3]{index=3}

---

## RAG Workflow

The application follows a Retrieval-Augmented Generation style workflow:

```text
User Question
      │
      ▼
Query Processing
      │
      ▼
Hybrid Retrieval
      │
      ▼
Relevant Knowledge Chunks
      │
      ▼
Ranked Context
      │
      ▼
Guardrails
      │
      ▼
Answer Orchestration
      │
      ▼
Grounded Answer
      │
      ▼
Citations + Confidence
```

When an LLM provider is unavailable, AtlasIQ can fall back to a deterministic synthesis engine while still returning citations and confidence scores. :contentReference[oaicite:4]{index=4}

---

## Grounded Answers

AtlasIQ is designed to answer questions using retrieved enterprise knowledge.

For example:

```text
Question:
What is our customer escalation SLA for P1 incidents?

        ↓

Hybrid Retrieval

        ↓

Relevant Enterprise Knowledge

        ↓

Grounded Answer

        ↓

Supporting Citations
```

The application exposes ranked citations alongside grounded answers. :contentReference[oaicite:5]{index=5}

---

## Prompt-Injection Guardrails

A major component of AtlasIQ is its security guardrail layer.

The project includes guardrails designed to block common:

- Prompt-injection attempts
- Data-exfiltration attempts

These checks are intended to occur before requests reach the model layer. :contentReference[oaicite:6]{index=6}

This provides an additional protection layer for enterprise knowledge applications.

---

## Persistent Storage

AtlasIQ maintains persistent application data through:

```text
storage/registry.json
```

The registry is used to maintain indexed documents and session-related memory. :contentReference[oaicite:7]{index=7}

---

## Conversation History

The application tracks conversation history per session to provide short-term contextual continuity.

This allows follow-up questions to remain connected to the current conversation. :contentReference[oaicite:8]{index=8}

---

## LLM Runtime Modes

AtlasIQ supports different runtime configurations.

### Local / Offline Mode

The application can operate without external model credentials.

The default documented local setup uses **Ollama**. :contentReference[oaicite:9]{index=9}

### LangChain Mode

LangChain orchestration can be enabled for richer grounded responses.

The project supports configuring an LLM provider through environment variables. :contentReference[oaicite:10]{index=10}

---

# Ollama Configuration

## 1. Install Ollama

Install Ollama for Windows.

## 2. Pull the Model

```bash
ollama pull llama3.2
```

## 3. Configure `.env`

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## 4. Start AtlasIQ

Start the application and ask questions normally.

The Ollama setup and model configuration are documented in the original project documentation. :contentReference[oaicite:11]{index=11}

---

# OpenAI Configuration

If you want to use OpenAI instead of the local Ollama configuration:

```env
LLM_PROVIDER=openai
ENABLE_LANGCHAIN_RUNTIME=true
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=your_model_name
```

The documented setup requires:

1. `LLM_PROVIDER=openai`
2. `ENABLE_LANGCHAIN_RUNTIME=true`
3. An `OPENAI_API_KEY`
4. Optionally, an `OPENAI_CHAT_MODEL` value. :contentReference[oaicite:12]{index=12}

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DarshanS2004/AtlasIQ-Enterprise-Knowledge-Assistant.git
cd AtlasIQ-Enterprise-Knowledge-Assistant
```

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

The project documentation uses editable installation with development dependencies:

```bash
pip install -e .[dev]
```

:contentReference[oaicite:13]{index=13}

---

## Environment Configuration

Copy the example environment file:

### Windows

```powershell
copy .env.example .env
```

Then update the configuration values as required.

:contentReference[oaicite:14]{index=14}

### Important Security Rule

Never commit your real `.env` file to GitHub.

Your `.env.example` should contain placeholders only.

For example:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Never:

```env
OPENAI_API_KEY=sk-real-secret-key
```

---

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.api.main:app --reload
```

Then open:

```text
http://localhost:8000
```

The documented project startup process uses Uvicorn and exposes the application on port 8000. :contentReference[oaicite:15]{index=15}

---

## API Overview

The project exposes the following documented endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Application health |
| `GET` | `/api/v1/overview` | System overview |
| `GET` | `/api/v1/documents` | List indexed documents |
| `POST` | `/api/v1/ingest/seed` | Seed demo knowledge |
| `POST` | `/api/v1/ingest/manual` | Ingest manually provided knowledge |
| `POST` | `/api/v1/ingest/files` | Upload knowledge files |
| `POST` | `/api/v1/chat/query` | Ask a knowledge question |

These endpoints are documented in the project API overview. :contentReference[oaicite:16]{index=16}

---

## Knowledge Ingestion

AtlasIQ provides several ways to add knowledge.

### Seed Knowledge

The application can populate the workspace with example enterprise policies and knowledge.

```text
POST /api/v1/ingest/seed
```

This allows the application to be demonstrated without first creating a custom knowledge base.

### Manual Knowledge

Knowledge can be entered directly through the application.

```text
POST /api/v1/ingest/manual
```

### File Ingestion

Supported enterprise knowledge files can be uploaded through:

```text
POST /api/v1/ingest/files
```

---

## Demo Questions

Example questions supported by the project include:

```text
What is our customer escalation SLA for P1 incidents?
```

```text
How should a new employee complete security onboarding?
```

```text
Which controls are required before a vendor gets production access?
```

```text
Summarize the release readiness checklist for enterprise deployments.
```

These examples are included in the project's original documentation. :contentReference[oaicite:17]{index=17}

---

## Architecture

The application is organized into clear layers:

```text
app/
│
├── api/
│
├── core/
│
├── domain/
│
├── services/
│
├── static/
│
└── templates/
│
data/
│
└── knowledge/
│
storage/
│
└── registry.json
│
└── tests/
```

The documented architecture separates API, configuration, domain models, services, static assets, templates, knowledge data, persistent storage, and tests. :contentReference[oaicite:18]{index=18}

---

## Architecture Layers

### API Layer

Handles HTTP requests and exposes the application's endpoints.

### Core Layer

Contains configuration and core application behavior.

### Domain Layer

Contains domain models and enterprise knowledge concepts.

### Services Layer

Contains retrieval, ingestion, orchestration, and other application services.

### Static / Templates

Provides the browser-console interface.

### Storage

Maintains persistent application registry data.

---

## Docker

The project also supports Docker Compose.

Build and start the application with:

```bash
docker compose up --build
```

:contentReference[oaicite:19]{index=19}

---

## Testing & Verification

The project includes unit tests covering:

- Document chunking
- Retrieval
- Guardrails

A syntax compilation pass can also be used for verification in minimal environments. :contentReference[oaicite:20]{index=20}

---

## Security

Enterprise knowledge systems require careful handling of sensitive information.

### API Keys

Never commit:

```text
.env
```

to GitHub.

Use:

```text
.env.example
```

with placeholder values.

### Prompt Injection

AtlasIQ includes guardrails designed to identify and block common prompt-injection and data-exfiltration attempts before they reach the model layer. :contentReference[oaicite:21]{index=21}

### Enterprise Data

Before using the application with confidential enterprise information in production, implement appropriate authentication, authorization, access control, and data-protection mechanisms.

---

## Privacy Considerations

AtlasIQ maintains persistent indexed documents and session memory through its local registry storage. :contentReference[oaicite:22]{index=22}

For production environments, organizations should establish:

- Data retention policies
- Access controls
- User authentication
- Authorization
- Audit logging
- Secure storage
- Encryption where appropriate
- Document-level permissions

---

## Fallback Behavior

One of the project's useful characteristics is its ability to operate without an external LLM provider.

When the configured LLM provider is unavailable, the application can fall back to a deterministic synthesis engine while continuing to provide citations and confidence scores. :contentReference[oaicite:23]{index=23}

This makes the application useful for local demonstrations and environments where external model access is unavailable.

---

## Advantages

- 🏢 Enterprise-oriented architecture
- 🔎 Hybrid retrieval
- 🧠 RAG-style grounded question answering
- 📌 Ranked citations
- 🛡️ Prompt-injection guardrails
- 💾 Persistent indexing
- 💬 Session context
- 🧩 Modular application architecture
- 🔄 Local deterministic fallback
- 🤖 Optional LangChain runtime
- 🌐 Browser-based interface
- 🧪 Automated tests

---

## Limitations

- AI-generated answers may contain errors.
- Retrieval quality depends on the quality of the indexed enterprise knowledge.
- LLM functionality depends on the configured provider.
- Production deployments require stronger authentication and authorization controls.
- Sensitive enterprise data requires appropriate security and privacy configuration.
- The documented supported knowledge formats are `.txt`, `.md`, `.json`, and `.csv`.

---

## Potential Use Cases

AtlasIQ can serve as a foundation for:

- 🏢 Enterprise knowledge assistants
- 📋 Internal policy assistants
- 👋 Employee onboarding assistants
- 🚨 Incident-response knowledge systems
- ⚙️ Operations assistants
- 📚 Internal documentation search
- 🔎 Enterprise knowledge retrieval
- 🚀 Release-readiness assistants

---

## Future Improvements

Potential future enhancements include:

- 🔐 Enterprise authentication
- 👥 Role-based access control
- 📑 Document-level permissions
- 🧠 Advanced retrieval and reranking
- 📊 Retrieval analytics
- 🔍 Advanced citation management
- 💬 Long-term conversation memory
- 🗂️ Document lifecycle management
- 🔄 Automatic knowledge synchronization
- 📈 Usage analytics
- 🛡️ Advanced security policies
- ☁️ Cloud deployment
- 🧪 Expanded integration and security testing

---

## Learning Objectives

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation
- Hybrid information retrieval
- Semantic-style retrieval
- Lexical scoring
- LangChain orchestration
- FastAPI backend development
- Document ingestion
- Document chunking
- Citation-based answers
- Prompt-injection protection
- Persistent document indexing
- Session-based conversation context
- Local LLM integration
- API-based LLM integration

---

## Project Highlights

### 🏢 Enterprise Architecture

Designed around internal policy, operations, onboarding, and incident-response workflows.

### 🔎 Hybrid Retrieval

Combines semantic-style retrieval with lexical scoring for knowledge discovery.

### 🧠 RAG

Retrieves relevant enterprise knowledge before composing grounded answers.

### 📌 Citations

Provides supporting citations to make answers easier to verify.

### 🛡️ Security Guardrails

Includes protection against common prompt-injection and data-exfiltration attempts.

### 💾 Persistent Knowledge

Maintains indexed documents and session memory through persistent storage.

### 🔄 Flexible Runtime

Supports local deterministic behavior as well as optional LangChain-powered LLM execution.

---

## Security Checklist

Before publishing this project to GitHub:

```text
[ ] .env is included in .gitignore
[ ] No real API keys are committed
[ ] .env.example contains placeholders only
[ ] No passwords are committed
[ ] No AWS/OpenAI/Ollama secrets are committed
[ ] Local sensitive knowledge files are reviewed
[ ] storage/registry.json is reviewed
[ ] Test data contains no confidential information
[ ] No private enterprise documents are committed
```

Recommended `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

If your local `storage/` or `data/knowledge/` directories contain private enterprise information, consider adding the appropriate paths to `.gitignore` before publishing.

---

## Example Workflow

```text
1. Start AtlasIQ
        ↓
2. Open Browser Console
        ↓
3. Seed or Upload Knowledge
        ↓
4. Documents Are Chunked
        ↓
5. Knowledge Is Indexed
        ↓
6. User Asks a Question
        ↓
7. Hybrid Retrieval
        ↓
8. Guardrail Validation
        ↓
9. LangChain / Local Runtime
        ↓
10. Grounded Answer
        ↓
11. Supporting Citations
```

---

## Conclusion

**AtlasIQ Enterprise Knowledge Assistant** demonstrates how modern RAG concepts can be combined with enterprise-oriented software architecture to create a practical internal knowledge system.

The project brings together **hybrid retrieval, LangChain orchestration, document ingestion, persistent indexing, grounded citations, conversation context, and security guardrails** into a single application.

It provides a strong foundation for building enterprise knowledge assistants focused on internal policies, operations, onboarding, incident response, and organizational documentation.

---

## Author

**Darshan S**

GitHub:

```text
https://github.com/DarshanS2004
```

---

## License

This project is available under the license included in this repository.