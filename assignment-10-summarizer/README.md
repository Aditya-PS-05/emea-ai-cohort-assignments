# Assignment 10: local LLM text summarizer

Create the Conda environment and install the local model:

```bash
conda env create -f environment.yml
conda activate emea-summarizer
ollama pull tinyllama
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. Ollama must be running locally on port 11434. The form validates text length, shows loading and error messages, and displays the returned summary. The endpoint is also available as `POST /summarize` with JSON `{"text":"..."}`.

In this checkout, a compatible Conda environment was created with Micromamba at `../.mamba/envs/emea-summarizer`. From this folder, run it directly with `../.mamba/envs/emea-summarizer/bin/uvicorn app:app --reload`. The homepage returned HTTP 200 from this environment.

TinyLlama's small context limits faithful summarization of long input. The app accepts at most 6,000 characters; for text close to that bound, input may be truncated by the model's 2K context window. Check summaries against the source before using them.

Local demonstration: the FastAPI endpoint returned HTTP 200 and a summary for a short library notice. The model added a "first floor" location that was not in the source. This is an observed factual error, so the response should not be treated as verified without checking the input.
