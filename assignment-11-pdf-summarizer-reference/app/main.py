import base64
import logging
import os
import shutil
import time

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.pdf_utils import extract_text_from_pdf
from app.chunking_utils import chunk_text
from app.summarizer_utils import (
    summarize_all_chunks,
    summarize_all_chunks_with_progress,
    combine_summaries,
)
from app.models import (
    HealthResponse,
    RootResponse,
    UploadPDFResponse,
    UploadPDFChunkedResponse,
    ChunkPreview,
    SummarizePDFResponse,
    WebSocketUploadRequest,
)

# Logging setup - print() statements-ku badhila proper logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("pdf_summarizer")

app = FastAPI(title="PDF Summarizer Agent", version="0.1.0")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_PDF_SIZE_MB = 20
MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024


@app.get("/", response_model=RootResponse)
def root():
    return {"message": "PDF Summarizer Agent is running"}


@app.get("/health", response_model=HealthResponse)
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
    logger.warning(f"Could not delete file after {retries} retries: {file_path}")


def _validate_pdf_upload(file: UploadFile):
    """
    Common validation - filename extension check pannum.
    Size check request body already read aana apparam pannuvom
    (Step-la kaanom).
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")


def _save_uploaded_file(file: UploadFile, file_path: str):
    """
    File-ah disk-la save pannitu, size limit exceed aacha nu
    check pannum. Exceed aana, file-ah delete pannitu error raise pannum.
    """
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    if file_size > MAX_PDF_SIZE_BYTES:
        _safe_delete_file(file_path)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_PDF_SIZE_MB}MB",
        )


@app.post("/upload-pdf", response_model=UploadPDFResponse)
async def upload_pdf(file: UploadFile = File(...)):
    _validate_pdf_upload(file)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    _save_uploaded_file(file, file_path)

    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _safe_delete_file(file_path)

    logger.info(f"Extracted text from {file.filename} ({len(extracted_text)} chars)")

    return UploadPDFResponse(
        filename=file.filename,
        character_count=len(extracted_text),
        extracted_text=extracted_text,
    )


@app.post("/upload-pdf-chunked", response_model=UploadPDFChunkedResponse)
async def upload_pdf_chunked(file: UploadFile = File(...)):
    _validate_pdf_upload(file)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    _save_uploaded_file(file, file_path)

    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _safe_delete_file(file_path)

    chunks = chunk_text(extracted_text)
    logger.info(f"Split {file.filename} into {len(chunks)} chunks")

    return UploadPDFChunkedResponse(
        filename=file.filename,
        character_count=len(extracted_text),
        total_chunks=len(chunks),
        chunks_preview=[
            ChunkPreview(chunk_number=i + 1, char_count=len(c), preview=c[:150])
            for i, c in enumerate(chunks)
        ],
    )


@app.post("/summarize-pdf", response_model=SummarizePDFResponse)
async def summarize_pdf(file: UploadFile = File(...)):
    _validate_pdf_upload(file)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    _save_uploaded_file(file, file_path)

    try:
        extracted_text = extract_text_from_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _safe_delete_file(file_path)

    chunks = chunk_text(extracted_text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks generated from this PDF")

    logger.info(f"Summarizing {file.filename} ({len(chunks)} chunks)")

    try:
        chunk_summaries = summarize_all_chunks(chunks)
        final_summary = combine_summaries(chunk_summaries)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    logger.info(f"Completed summarization for {file.filename}")

    return SummarizePDFResponse(
        filename=file.filename,
        character_count=len(extracted_text),
        total_chunks=len(chunks),
        chunk_summaries=chunk_summaries,
        final_summary=final_summary,
    )


@app.websocket("/ws/summarize")
async def websocket_summarize(websocket: WebSocket):
    """
    REAL PIPELINE + LIVE PROGRESS:
    Client oru JSON message anuppanum: {"filename": "...", "file_base64": "..."}
    Server: file save -> text extract -> chunk -> ovvoru chunk
    summarize aana odane progress anuppum -> final combine ->
    final result anuppum.
    """
    await websocket.accept()
    file_path = None

    try:
        raw_data = await websocket.receive_json()

        # Pydantic model mூlam validate pannuvom
        try:
            request_data = WebSocketUploadRequest(**raw_data)
        except ValidationError as e:
            await websocket.send_json({"status": "error", "message": f"Invalid request: {e}"})
            return

        filename = request_data.filename
        file_base64 = request_data.file_base64

        if not filename.lower().endswith(".pdf"):
            await websocket.send_json({"status": "error", "message": "Only PDF files are allowed"})
            return

        await websocket.send_json({"status": "progress", "stage": "uploading", "message": "Saving file..."})

        try:
            file_bytes = base64.b64decode(file_base64)
        except Exception:
            await websocket.send_json({"status": "error", "message": "Invalid file data (base64 decode failed)"})
            return

        if len(file_bytes) > MAX_PDF_SIZE_BYTES:
            await websocket.send_json({
                "status": "error",
                "message": f"File too large. Maximum allowed size is {MAX_PDF_SIZE_MB}MB",
            })
            return

        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        await websocket.send_json({"status": "progress", "stage": "extracting", "message": "Extracting text from PDF..."})
        extracted_text = extract_text_from_pdf(file_path)

        await websocket.send_json({"status": "progress", "stage": "chunking", "message": "Splitting text into chunks..."})
        chunks = chunk_text(extracted_text)

        if not chunks:
            await websocket.send_json({"status": "error", "message": "No chunks generated from this PDF"})
            return

        await websocket.send_json({
            "status": "progress", "stage": "chunking_done",
            "message": f"Created {len(chunks)} chunks", "total_chunks": len(chunks),
        })

        async def send_chunk_progress(current: int, total: int):
            await websocket.send_json({
                "status": "progress", "stage": "summarizing",
                "message": f"Summarizing chunk {current}/{total}...",
                "current_chunk": current, "total_chunks": total,
            })

        logger.info(f"[WS] Summarizing {filename} ({len(chunks)} chunks)")
        chunk_summaries = await summarize_all_chunks_with_progress(chunks, send_chunk_progress)

        await websocket.send_json({"status": "progress", "stage": "combining", "message": "Combining all summaries into final result..."})
        final_summary = combine_summaries(chunk_summaries)

        logger.info(f"[WS] Completed summarization for {filename}")

        await websocket.send_json({
            "status": "complete", "filename": filename,
            "total_chunks": len(chunks), "chunk_summaries": chunk_summaries,
            "final_summary": final_summary,
        })

    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected from /ws/summarize")
    except ValueError as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    except RuntimeError as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    except Exception as e:
        logger.exception("[WS] Unexpected error in /ws/summarize")
        await websocket.send_json({"status": "error", "message": f"Unexpected error: {e}"})
    finally:
        if file_path:
            _safe_delete_file(file_path)
        await websocket.close()