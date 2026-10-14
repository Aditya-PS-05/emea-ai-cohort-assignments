# 📄 PDF Summarizer Agent

A fully local, AI-powered PDF summarization tool with **live progress tracking** via WebSocket. Upload any PDF, watch it get chunked and summarized chunk-by-chunk in real time, and receive a clean, coherent final summary — all running on your own machine with **Ollama** (no cloud APIs, no data leaves your computer).

---

## 🏗️ Architecture

```
┌─────────────┐     PDF Upload      ┌──────────────────┐
│   Client    │ ───────────────────>│   FastAPI Server   │
│ (Browser /  │                     │                    │
│  API call)  │<─── Live Progress ──│  ┌──────────────┐  │
└─────────────┘     (WebSocket)     │  │ Text Extract │  │
                                     │  │  (PyMuPDF)   │  │
                                     │  └──────┬───────┘  │
                                     │         ▼          │
                                     │  ┌──────────────┐  │
                                     │  │   Chunking   │  │
                                     │  │ (LangChain)  │  │
                                     │  └──────┬───────┘  │
                                     │         ▼          │
                                     │  ┌──────────────┐  │
                                     │  │  Map: Summ.  │  │
                                     │  │ each chunk   │──┼──> Ollama
                                     │  └──────┬───────┘  │   (Llama 3.1)
                                     │         ▼          │
                                     │  ┌──────────────┐  │
                                     │  │Reduce: Combine│──┼──> Ollama
                                     │  │  into 1 summ. │  │   (Llama 3.1)
                                     │  └──────────────┘  │
                                     └────────────────────┘
```

**Flow:** PDF is uploaded → text is extracted → text is split into chunks → each chunk is summarized individually (Map step) → all chunk summaries are combined into one coherent final summary (Reduce step) → progress at every stage is streamed live to the client over WebSocket.

---

## ✨ Features

- 📤 **PDF Upload & Text Extraction** — Robust extraction using PyMuPDF (handles malformed/real-world PDFs that stricter libraries reject)
- ✂️ **Smart Text Chunking** — LangChain's `RecursiveCharacterTextSplitter` with configurable size and overlap, respecting sentence/paragraph boundaries
- 🤖 **Local LLM Summarization** — Runs entirely on Ollama (Llama 3.1) — no external API calls, no internet required after setup
- 🔀 **Map-Reduce Pipeline** — Summarizes each chunk individually, then combines into one coherent, repetition-free summary
- 📡 **Live Progress via WebSocket** — Real-time updates as each chunk is processed (upload → extract → chunk → summarize → combine)
- ✅ **Pydantic Validation** — Typed request/response models across all endpoints for reliability and self-documenting API schemas
- 🐳 **Dockerized** — Fully containerized with host-machine Ollama connectivity via `host.docker.internal`
- 📝 **Structured Logging** — Timestamped logs for easy debugging and monitoring
- 🛡️ **File Size Limits & Safe Cleanup** — 20MB upload cap, automatic temp file cleanup with Windows-safe retry logic

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend Framework | FastAPI |
| Server | Uvicorn |
| PDF Processing | PyMuPDF (fitz) |
| Text Chunking | LangChain |
| LLM | Ollama (Llama 3.1) — local, offline |
| Real-time Communication | WebSocket |
| Data Validation | Pydantic |
| Containerization | Docker, Docker Compose |
| Language | Python 3.11 |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/download) installed
- Docker Desktop (optional, for containerized deployment)

### 1. Clone the repository
```bash
git clone https://github.com/ThePrakashV/pdf-summarizer-agent.git
cd pdf-summarizer-agent
```

### 2. Set up Ollama
```bash
ollama pull llama3.1
ollama serve
```
Keep this running in a separate terminal — the app connects to this local Ollama server for all summarization.

### 3. Local Setup (without Docker)
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the interactive API docs (Swagger UI).

### 4. Docker Setup (recommended for deployment)
```bash
docker compose up --build
```

Ollama must be running on the **host machine** (not inside the container) — the container connects to it via `host.docker.internal:11434`, configured in `docker-compose.yml`.

To stop:
```bash
docker compose down
```

### 5. Test the Live WebSocket Flow
Open `test_websocket.html` directly in your browser (double-click the file), choose a PDF, and click **Summarize** to watch live progress as each chunk is processed.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health/welcome message |
| GET | `/health` | Health check |
| POST | `/upload-pdf` | Upload PDF, get extracted text |
| POST | `/upload-pdf-chunked` | Upload PDF, get chunked text preview |
| POST | `/summarize-pdf` | Full pipeline (HTTP) — returns final summary (blocking, no progress) |
| WS | `/ws/summarize` | Full pipeline with **live progress** over WebSocket (recommended) |

### Example: `/summarize-pdf` response shape
```json
{
  "filename": "example.pdf",
  "character_count": 19248,
  "total_chunks": 16,
  "chunk_summaries": ["...", "..."],
  "final_summary": "..."
}
```

### Example: `/ws/summarize` message flow
```json
// Client sends:
{ "filename": "example.pdf", "file_base64": "<base64-encoded-pdf>" }

// Server streams:
{ "status": "progress", "stage": "extracting", "message": "Extracting text from PDF..." }
{ "status": "progress", "stage": "chunking_done", "message": "Created 16 chunks", "total_chunks": 16 }
{ "status": "progress", "stage": "summarizing", "message": "Summarizing chunk 1/16...", "current_chunk": 1, "total_chunks": 16 }
...
{ "status": "progress", "stage": "combining", "message": "Combining all summaries into final result..." }
{ "status": "complete", "filename": "example.pdf", "total_chunks": 16, "chunk_summaries": [...], "final_summary": "..." }
```

---

## 📁 Project Structure

```
pdf-summarizer-agent/
├── app/
│   ├── main.py               # FastAPI app, routes, WebSocket handler
│   ├── models.py             # Pydantic request/response models
│   ├── pdf_utils.py          # PDF text extraction (PyMuPDF)
│   ├── chunking_utils.py     # Text chunking (LangChain)
│   └── summarizer_utils.py   # Ollama summarization (Map-Reduce)
├── docs/                     # Phase-by-phase development documentation
├── uploads/                  # Temp storage for uploaded PDFs (auto-cleaned)
├── test_websocket.html       # Standalone browser test page for live WebSocket flow
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 📋 Phase-wise Development Summary

| Phase | Description |
|---|---|
| 1 | Project setup + basic FastAPI server |
| 2 | PDF upload + text extraction (PyMuPDF) |
| 3 | Text chunking (LangChain) |
| 4 | Ollama connection + single chunk summarization |
| 5 | Full Map-Reduce pipeline (all chunks → final summary) |
| 6 | WebSocket basic setup (live progress foundation) |
| 7 | Real summarization pipeline + WebSocket live progress |
| 8 | Pydantic models, error handling, code cleanup |
| 9 | Docker containerization |
| 10 | Final testing + GitHub push |

Detailed phase-by-phase documentation (including errors faced and how they were fixed) is available in [`docs/`](./docs).

---

## ⚠️ Known Limitations

- Scanned/image-only PDFs (no embedded text layer) are not supported — OCR is not implemented
- Summarization speed depends on local machine specs (CPU/GPU) and chunk count — larger PDFs can take several minutes
- Max file size capped at 20MB (configurable via `MAX_PDF_SIZE_MB` in `app/main.py`)
- Swagger UI (`/docs`) does not support testing WebSocket endpoints — use `test_websocket.html` instead

---

## 🔮 Possible Future Improvements

- OCR support for scanned PDFs
- Multi-model support (switch between Ollama models via config)
- Summary length/style customization (bullet points, executive summary, etc.)
- Persistent job history / database storage
- Authentication for multi-user deployments

---

## 📄 License

This project is open source and available under the MIT License.
