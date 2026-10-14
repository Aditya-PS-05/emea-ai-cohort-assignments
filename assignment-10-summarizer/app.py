"""FastAPI frontend for a local Ollama TinyLlama text summarizer."""
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Local Text Summarizer")
PAGE = Path(__file__).with_name("index.html")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


class SummaryRequest(BaseModel):
    text: str = Field(min_length=30, max_length=6000)


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE.read_text(encoding="utf-8")


@app.post("/summarize")
def summarize(body: SummaryRequest):
    source = body.text.strip()
    if len(source) < 30:
        raise HTTPException(422, "Enter at least 30 non-space characters.")
    prompt = "Summarize the following text in 2 to 4 clear sentences. Use only facts stated in the text.\n\nText:\n" + source + "\n\nSummary:"
    payload = json.dumps({"model": "tinyllama", "prompt": prompt, "stream": False, "options": {"num_ctx": 2048, "num_predict": 160, "temperature": 0}}).encode()
    request = Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=90) as response:
            summary = json.load(response).get("response", "").strip()
    except HTTPError as error:
        if error.code == 404:
            raise HTTPException(503, "TinyLlama is missing. Run: ollama pull tinyllama") from error
        raise HTTPException(502, "Ollama could not generate a summary.") from error
    except (URLError, TimeoutError) as error:
        raise HTTPException(503, "Ollama is unavailable or timed out. Start Ollama and try again.") from error
    except (ValueError, KeyError) as error:
        raise HTTPException(502, "Ollama returned an invalid response.") from error
    if not summary:
        raise HTTPException(502, "Ollama returned an empty summary.")
    return {"summary": summary}
