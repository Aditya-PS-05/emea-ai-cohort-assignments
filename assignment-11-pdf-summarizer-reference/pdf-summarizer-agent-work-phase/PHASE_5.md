# Phase 5: Full Pipeline — All Chunks → Summarize → Combined Final Summary

## 📌 Status: ✅ COMPLETE

---

## 🎯 What We Did (Summary)

Andha phase-la namma Phase 4-ல build பண்ணின single-chunk summarization-ஐ **full pipeline** ah extend பண்ணோம் — Map-Reduce pattern use பண்ணி:

1. `summarize_all_chunks()` function create பண்ணோம் — **MAP step**: ella chunks-ஐயும் loop பண்ணி, ஒவ்வொன்றையும் தனித்தனியா summarize பண்ணும் (list of mini-summaries return பண்ணும்)
2. `combine_summaries()` function create பண்ணோம் — **REDUCE step**: ella mini-summaries-ஐயும் join பண்ணி, LLM-கிட்ட மீண்டும் கொடுத்து, ஒரே coherent final summary உருவாக்கும்
3. `/summarize-pdf` — namma project-oda **main/real endpoint** create பண்ணோம் (PDF upload → extract → chunk → map-summarize → reduce-combine → return)
4. Phase 4-oda temporary test endpoint (`/test-summarize-first-chunk`) remove பண்ணோம் — இனி thevai illa
5. Real PDF (16 chunks) மூலம் full pipeline test பண்ணி, clean coherent `final_summary` verify பண்ணோம்

**Analogy:** Phase 4-ல namma oru chunk mattum cook பண்ணி பாத்தோம். Ippo namma ella 16 chunks-ஐயும் (Map step) தனித்தனியா cook பண்ணி, appuram andha 16 chinna dishes-ஐயும் **ஒரே final dish ah combine பண்ணி** (Reduce step) serve பண்ணோம். "Summarize small pieces first, then summarize the summaries" — periya documents-ku idhு standard, reliable technique.

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

Idha phase-la ஒரு error-um varala — smooth implementation, முதல் try-லேயே success ஆயிடுச்சு. 🎉

---

## 💻 Final Working Commands & Code

### `app/summarizer_utils.py` (Map + Reduce functions added)

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


def summarize_all_chunks(chunks: list[str]) -> list[str]:
    """
    MAP step: Ella chunks-ayum oruvarusaga (one by one) loop
    pannitu, ovvoru chunk-ayum summarize pannum. List of
    mini-summaries return pannum.
    """
    chunk_summaries = []

    for index, chunk in enumerate(chunks, start=1):
        summary = summarize_chunk(chunk)
        chunk_summaries.append(summary)

    return chunk_summaries


def combine_summaries(chunk_summaries: list[str]) -> str:
    """
    REDUCE step: Ella mini-summaries-ayum onna serthu (join
    pannitu), adha marupadiyum LLM-kitta kudutthu, oru clean,
    coherent, single final summary create pannum.
    """
    combined_text = "\n\n".join(
        f"- {summary}" for summary in chunk_summaries
    )

    prompt = f"""Below are summaries of different sections of a document.
Combine them into a single, well-organized, coherent summary of the
entire document. Remove any repetition. Write it as flowing paragraphs,
not a list.

Section summaries:
{combined_text}

Final Combined Summary:"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise RuntimeError(f"Ollama final summarization failed: {e}")

    final_summary = response["message"]["content"].strip()
    return final_summary
```

### `app/main.py` (main `/summarize-pdf` endpoint added, test endpoint removed)

```python
import os
import shutil
import time

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.pdf_utils import extract_text_from_pdf
from app.chunking_utils import chunk_text
from app.summarizer_utils import summarize_all_chunks, combine_summaries

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


@app.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    """
    FULL PIPELINE: PDF upload -> text extract -> chunking ->
    ovvoru chunk-um summarize (MAP) -> ella summaries-um combine
    pannitu final summary (REDUCE) -> return pannum.
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

    try:
        chunk_summaries = summarize_all_chunks(chunks)
        final_summary = combine_summaries(chunk_summaries)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "filename": file.filename,
        "character_count": len(extracted_text),
        "total_chunks": len(chunks),
        "chunk_summaries": chunk_summaries,
        "final_summary": final_summary,
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

Test via `http://127.0.0.1:8000/docs` → `/summarize-pdf` → Try it out → Choose PDF → Execute

### Verified Test Result

- Input PDF: `hro4_2025_sensorsforhumanoidsandartificialskins.pdf` (19,248 characters, 16 chunks)
- `chunk_summaries`: 16 individual mini-summaries, each accurate and readable
- `final_summary`: Single coherent multi-paragraph summary covering humanoid robots, electronic skin, tactile sensors, EIT/EMT sensing technology, and applications — repetition removed, well-organized flowing text

---

## 📝 Important Notes for Future Reference

- **`/summarize-pdf` is now namma project-oda main endpoint.** Ella future phases-um (WebSocket progress, Docker deployment) idhே pipeline logic-ஐ base ah வைச்சு build ஆகும்.
- **Idhு time எடுக்கும்!** 16 chunks இருந்தா, 16 separate Ollama calls (Map) + 1 more call (Reduce) = 17 total LLM calls. Ungal machine speed-ஐ பொறுத்து 2-5 minutes ஆகலாம். Idhே கூட phase 6/7-ல WebSocket live progress தேவைப்படுவதற்கு main காரணம் — user-கு "waiting" feeling வராம, real-time progress காட்டறதுக்காக.
- `summarize_all_chunks()` and `combine_summaries()` — rendும் தனித்தனி functions ah வைச்சிருக்கோம் intentionally, ஏனெனில் Phase 7 (WebSocket)-ல ovvoru chunk summarize ஆனதும் progress update அனுப்ப வேண்டும் — idhை easy ஆ integrate பண்ண இந்த separation உதவும்.
- Response-ல `chunk_summaries` list-ஐயும் return பண்றோம் (final summary மட்டுமில்லாம்) — idhு transparency-க்கு நல்லது, மற்றும் debugging-க்கும் உதவும் (எந்த chunk correct-ஆ summarize ஆகல எனில் easy-ஆ கண்டுபிடிக்கலாம்).
- Prompt-ல "Remove any repetition" மற்றும் "flowing paragraphs, not a list" clearly mention பண்ணியிருப்பதால், Reduce step clean readable output தந்திருக்கு — idhு prompt engineering-oda முக்கியத்துவத்தை காட்டுது.

---

## ➡️ Next: Phase 6 — WebSocket Basic Setup (Live Progress Foundation)
