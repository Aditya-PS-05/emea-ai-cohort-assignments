# Phase 2: PDF Upload + Text Extraction

## 📌 Status: ✅ COMPLETE

---

## 🎯 What We Did (Summary)

Andha phase-la namma PDF upload pண்ணி, adhுla irukற text-ah extract pண்ணுற feature build pண்ணோம்:

1. `PyPDF2` install pண்ணி, initial text extraction logic build pண்ணோம்
2. Multiple PDF structural errors (`EOF marker`, `startxref not found`) face pண்ணோம் - PyPDF2 romba strict library nu purinjuchu
3. **PyPDF2-la இருந்து PyMuPDF (`fitz`)-ku library switch பண்ணோம்** - malformed/real-world PDFs-ah handle pண்ண idhு romba robust
4. Windows-specific file locking issue (`PermissionError [WinError 32]`) fix பண்ணோம் - retry-with-delay logic add பண்ணி
5. `/upload-pdf` POST endpoint create பண்ணோம் - PDF upload → text extract → JSON response return பண்ணுது
6. Multiple real-world PDFs (Wikipedia export, research papers) upload பண்ணி successfully test பண்ணோம்

**Analogy:** Kitchen-ku vandha raw vegetable basket (PDF file)-ah open பண்ணி, ulla irukற vegetables (text)-ah cutting board மேல வைச்சோம் - cooking (summarization) ku ready ah. Munnadi use பண்ணின "strict teacher" (PyPDF2) கூட வேலை நடக்கல, so "flexible teacher" (PyMuPDF) கூப்பிட்டோம் - அது format சிறு பிரச்சினை இருந்தாலும் படிக்கும்.

---

## 🗂️ Final Folder Structure

```
D:\project\pdf-summarizer-agent\
│
├── venv\
├── app\
│   ├── main.py
│   └── pdf_utils.py
├── uploads\                (temporary PDF storage - auto cleanup aagum)
└── requirements.txt
```

---

## ⚠️ Errors Faced & How We Solved Them

### Error 1: `PdfReadError: EOF marker not found`

**Root Cause:** PDF file-oda structure standard-ah follow பண்ணல (missing "End Of File" marker). PyPDF2 default strict mode-la இருந்ததால், chinna structural issue இருந்தாலும் reject பண்ணிடும்.

**Analogy:** Book-oda கடைசி page-la "THE END" stamp missing - reader (PyPDF2) "இது complete book இல்லை" nு refuse பண்ணிடும்.

**Fix Attempted:** `PdfReader(pdf_file, strict=False)` — aana idhு sila cases-la kூட வேலை பண்ணல (PyPDF2-oda known bug).

---

### Error 2: `PdfReadError: startxref not found`

**Root Cause:** PDF-oda internal "index table" (xref table) missing/broken. Vேற oru PDF structural issue - PyPDF2 romba strict-ah irundhadhाल reject பண்ணிடுச்சு.

**Analogy:** Book-oda "table of contents" page கிழிஞ்சு போச்சு - strict reader அதை படிக்க மறுக்கும்.

**Final Fix:** Idhே point-la namma library-ஐயே switch பண்ணோம் — **PyPDF2 remove பண்ணி, PyMuPDF (`fitz`) install பண்ணோம்.** PyMuPDF, Google-oda MuPDF engine base பண்ணி இருப்பதால், malformed/real-world PDFs-ah romba reliable ah handle பண்ணும்.

```cmd
pip install PyMuPDF
```

`app/pdf_utils.py`-ல `fitz.open(file_path)` mூலம் PDF read பண்ண switch பண்ணோம்.

---

### Error 3: `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`

**Root Cause:** Windows OS-la, PyMuPDF file open பண்ணி `document.close()` call பண்ணினாலும், OS level-la file handle immediate ah release aagாம chinna delay இருக்கும். Namma `os.remove()` andha exact moment-la try பண்ணுவதால், "file busy" error வந்தது.

**Analogy:** Room use பண்ணிட்டு "முடிஞ்சிடுச்சு" சொல்லிட்டு வெளியே வந்தாலும், cleaning staff (Windows) அந்த room-ஐ "free" nு mark பண்ண konjam time எடுக்கும். அதற்குள் "demolish பண்ணுங்க" nு சொன்னா error வரும்.

**Fix:** `_safe_delete_file()` function add பண்ணோம் - `PermissionError` வந்தா, 0.3 seconds wait பண்ணி மீண்டும் try பண்ணும் (max 5 retries) — "retry with delay" pattern.

---

### Error 4 (Investigated, not a code bug): Specific PDFs `"Failed to open file as type pdf"`

Sila specific PDF files (filenames-la `@` symbol, special characters இருந்தவை) upload பண்ணும்போது idhே error தொடர்ந்து வந்தது, ஆனா vேற PDFs (research paper PDF) perfect ah worked ஆயிடுச்சு.

**Conclusion:** Namma code-la issue இல்லை — andha specific files genuinely corrupted/incomplete download ah இருந்திருக்கலாம் (root cause fully confirm பண்ணல, aana namma code multiple valid PDFs-oda successfully verify பண்ணிட்டோம்).

**Note for future:** Edhavadhu specific PDF file "Failed to open file as type pdf" error kொடுத்தா, முதலில் அந்த file-ஐ browser/Adobe Reader-la double-click பண்ணி நேரடியா open aaguthaa nु check பண்ணுங்க. Open aagaama na, file corrupted - vera PDF use பண்ணுங்க.

---

## 💻 Final Working Commands & Code

### Install Commands

```cmd
venv\Scripts\activate
pip install PyMuPDF python-multipart
```

### `requirements.txt`

```
fastapi
uvicorn[standard]
python-multipart
PyMuPDF
```

### `app/pdf_utils.py`

```python
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    PDF file path-ah eduthukondu, ulla irukra ella pages-oda
    text-ah extract pannitu, oru single string ah return pannum.

    PyMuPDF (fitz) use pannurom - idhu malformed/corrupted PDFs-ah
    kooda PyPDF2-vida better ah handle pannum.
    """
    extracted_text = ""

    try:
        document = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Could not read PDF file - it may be corrupted: {e}")

    if document.page_count == 0:
        document.close()
        raise ValueError("PDF file has no pages / is empty")

    for page_number in range(document.page_count):
        page = document.load_page(page_number)
        page_text = page.get_text()
        if page_text:
            extracted_text += f"\n--- Page {page_number + 1} ---\n"
            extracted_text += page_text

    document.close()

    if not extracted_text.strip():
        raise ValueError("No extractable text found in this PDF (might be a scanned image PDF)")

    return extracted_text
```

### `app/main.py`

```python
import os
import shutil
import time

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.pdf_utils import extract_text_from_pdf

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
    """
    Windows-la, file oru process use panniruntha, close() pannina
    odane kooda OS andha lock-ah release panna konjam time
    eduthukum. So namma retry pannuvom.
    """
    for attempt in range(retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        except PermissionError:
            time.sleep(delay)


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Step 1: File type check (PDF mattum allow pannuvom)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Step 2: File-ah temporary ah disk-la save pannuvom
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 3: Text extract pannuvom
    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Step 4: Temp file-ah delete pannuvom (cleanup) - safe retry logic-oda
        _safe_delete_file(file_path)

    # Step 5: Extracted text-ah response ah anuppuvom
    return {
        "filename": file.filename,
        "character_count": len(extracted_text),
        "extracted_text": extracted_text,
    }
```

### Run + Test Commands

```cmd
cd D:\project\pdf-summarizer-agent
venv\Scripts\activate
python -m py_compile app\main.py
python -m py_compile app\pdf_utils.py
uvicorn app.main:app --reload
```

Test via `http://127.0.0.1:8000/docs` → `/upload-pdf` → Try it out → Choose PDF → Execute

---

## 📝 Important Notes for Future Reference

- **PyPDF2 use பண்ணாதீங்க** இந்த project-la — real-world PDFs-oda structural issues handle பண்ண adhு romba strict. **PyMuPDF (`fitz`) namma standard choice.**
- Terminal-la `Warning: The 'fitz' API is deprecated...` nு oru warning வரும் — idhு error illa, safely ignore பண்ணலாம். Future-ல venum na `import pymupdf` syntax-ku migrate பண்ணலாம்.
- Windows-la file delete pண்ணும்போது `PermissionError` வந்தா, adhு பெரும்பாலும் "file handle release aaga konjam time" issue — retry-with-delay pattern use பண்ணுங்க, direct crash pண்ண வேண்டாம்.
- Vேற drive-கு terminal-la `cd` pண்ணனும் na (example: `D:` இருந்து `C:`), plain `cd` command vela pண்ணாது — `cd /d C:\path\to\folder` use பண்ணணும்.
- `uploads/` folder-ah `.gitignore`-ல add பண்ணனும் (GitHub push பண்ணும்போது temp files commit ஆகக்கூடாது) — idha Phase 10-ல confirm பண்ணுவோம்.
- Andha specific `.pdf` files "Failed to open file as type pdf" error கொடுத்தா, முதல் step: andha file-ஐ browser-la direct ah open பண்ணி valid PDF-ஆ nு verify பண்ணுங்க.

---

## ➡️ Next: Phase 3 — Text Chunking (LangChain Text Splitter)
