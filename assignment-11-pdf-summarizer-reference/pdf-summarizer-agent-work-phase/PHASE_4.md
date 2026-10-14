# Phase 4: Ollama Connect + Single Chunk Summarization

## 📌 Status: ✅ COMPLETE

---

## 🎯 What We Did (Summary)

Andha phase-la namma local LLM (Ollama)-ஐ namma project-oடன் connect பண்ணி, oru single text chunk-ஐ summarize பண்ண test பண்ணோம்:

1. Ollama install ஆயிருக்கா nு verify பண்ணோம் (`ollama --version`)
2. `llama3.1` model pull பண்ணோம் (`ollama pull llama3.1`)
3. `ollama` Python client library install பண்ணோம்
4. `app/summarizer_utils.py`-ல `summarize_chunk()` function create பண்ணோம் — oru chunk-ஐ Ollama-கிட்ட அனுப்பி, summary வாங்கும்
5. Temporary test endpoint `/test-summarize-first-chunk` create பண்ணோம் — PDF upload → chunks split → **முதல் chunk mattum** எடுத்து summarize பண்ணி result kாட்டும்
6. Real PDF test பண்ணி, Ollama clean ah 2-3 sentence summary generate பண்ணுthு nu verify பண்ணோம்

**Analogy:** Cutting board-la வைச்ச vegetables (chunks)-ஐ **cook பண்ண** oru chef தேவை. Andha chef தான் Ollama — namma own computer-ல run ஆகும் "local AI chef" (internet இல்லாமல் கூட வேலை செய்யும்). Namma முதலில் oru chunk mattum எடுத்து chef-கிட்ட "இதை சுருக்கமா சொல்லு" nu கேட்டோம் — full pipeline (ella chunks-ஐயும்) Phase 5-ல வரும்.

---

## 🗂️ Final Folder Structure

```
D:\project\pdf-summarizer-agent\
│
├── venv\
├── app\
│   ├── main.py
│   ├── pdf_utils.py
│   ├── chunking_utils.py
│   └── summarizer_utils.py
├── uploads\
└── requirements.txt
```

---

## ⚠️ Errors Faced & How We Solved Them

Idha phase-la ஒரு error-um varala — smooth setup, Ollama connection first try-லேயே success ஆயிடுச்சு. 🎉

---

## 💻 Final Working Commands & Code

### Ollama Setup Commands

```cmd
ollama --version
ollama pull llama3.1
ollama list
```

### Install Python Package

```cmd
venv\Scripts\activate
pip install ollama
```

### `requirements.txt`

```
fastapi
uvicorn[standard]
python-multipart
PyMuPDF
langchain
langchain-text-splitters
ollama
```

### `app/summarizer_utils.py`

```python
import ollama

MODEL_NAME = "llama3.1"


def summarize_chunk(chunk: str) -> str:
    """
    Oru single text chunk-ah eduthukondu, Ollama local LLM
    (llama3.1) use pannitu, adhoda summary-ah return pannum.
    """
    prompt = f"""Summarize the following text in 2-3 concise sentences.
Only output the summary, nothing else.

Text:
{chunk}

Summary:"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise RuntimeError(f"Ollama summarization failed: {e}")

    summary = response["message"]["content"].strip()
    return summary
```

### `app/main.py` (test endpoint added)

```python
import os
import shutil
import time

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.pdf_utils import extract_text_from_pdf
from app.chunking_utils import chunk_text
from app.summarizer_utils import summarize_chunk

app = FastAPI(title="PDF Summarizer Agent", version="0.1.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "PDF Summarizer Agent is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def _safe_delete_file(file_path: str, retries: int = 5, delay: float = 0.3):
    for attempt in range(retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        except PermissionError:
            time.sleep(delay)


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _safe_delete_file(file_path)

    return {
        "filename": file.filename,
        "character_count": len(extracted_text),
        "extracted_text": extracted_text,
    }


@app.post("/upload-pdf-chunked")
async def upload_pdf_chunked(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _safe_delete_file(file_path)

    chunks = chunk_text(extracted_text)

    return {
        "filename": file.filename,
        "character_count": len(extracted_text),
        "total_chunks": len(chunks),
        "chunks_preview": [
            {"chunk_number": i + 1, "char_count": len(c), "preview": c[:150]}
            for i, c in enumerate(chunks)
        ],
    }


@app.post("/test-summarize-first-chunk")
async def test_summarize_first_chunk(file: UploadFile = File(...)):
    """
    PHASE 4 TEST ENDPOINT: PDF upload pannitu, MUTHAL chunk mattum
    eduthu, Ollama use pannitu summarize pannum. Idha vachu Ollama
    connection + summarization logic correct ah velai pannuthu nu
    verify pannalam - full pipeline Phase 5-la varum.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _safe_delete_file(file_path)

    chunks = chunk_text(extracted_text)

    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks generated from this PDF")

    first_chunk = chunks[0]

    try:
        summary = summarize_chunk(first_chunk)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "first_chunk_char_count": len(first_chunk),
        "first_chunk_preview": first_chunk[:150],
        "summary_of_first_chunk": summary,
    }
```

### Run + Test Commands

Terminal 1 (Ollama server):
```cmd
ollama serve
```

Terminal 2 (FastAPI server):
```cmd
cd D:\project\pdf-summarizer-agent
venv\Scripts\activate
python -m py_compile app\main.py
python -m py_compile app\summarizer_utils.py
uvicorn app.main:app --reload
```

Test via `http://127.0.0.1:8000/docs` → `/test-summarize-first-chunk` → Try it out → Choose PDF → Execute

### Verified Test Result

- Input PDF: `hro4_2025_sensorsforhumanoidsandartificialskins.pdf` (16 chunks total)
- First chunk: 1034 characters
- Output: Clean 2-3 sentence summary about humanoid robot sensors, encoders, and hall effect sensors — accurate and readable

---

## 📝 Important Notes for Future Reference

- **Ollama server (`ollama serve`) background-la run ஆகணும்** — illana `ollama.chat()` call பண்ணும்போது connection error வரும். Puthு terminal window-la run பண்ணி, andha window-ஐ open ah வைச்சுக்கணும் (namma work பண்ணும்போது).
- **First request எப்போதும் konjam slow** (10-30 seconds) — model memory-ல load ஆகும் time. Adutha requests fast ah இருக்கும் (model already loaded).
- `/test-summarize-first-chunk` endpoint **temporary ah irundhа thaan** — Phase 5-ல ella chunks-ஐயும் summarize பண்ணி, final combined summary create பண்ணும் "real" endpoint வரும்.
- Prompt-ல clear ah instruction கொடுப்பது important — "Only output the summary, nothing else" nு சொல்லாட்டி, LLM extra commentary/preamble add பண்ணிடும் (example: "Here's the summary:").
- `MODEL_NAME` variable top-la constant ah வைச்சிருக்கோம் — future-ல model மாத்தணும் na (example: `mistral`, `llama3.2`), ஒரே இடத்தில் change பண்ணலாம்.

---

## ➡️ Next: Phase 5 — Full Pipeline (All Chunks → Summarize → Combined Final Summary)
