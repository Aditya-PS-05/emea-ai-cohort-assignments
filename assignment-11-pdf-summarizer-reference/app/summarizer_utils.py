import os

import ollama

MODEL_NAME = "llama3.1"

# OLLAMA_HOST environment variable irundha adha use pannum
# (Docker-la host.docker.internal), illana default local ah use pannum
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

client = ollama.Client(host=OLLAMA_HOST)


def summarize_chunk(chunk: str) -> str:
    prompt = f"""Summarize the following text in 2-3 concise sentences.
Only output the summary, nothing else.

Text:
{chunk}

Summary:"""

    try:
        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise RuntimeError(f"Ollama summarization failed: {e}")

    return response["message"]["content"].strip()


def summarize_all_chunks(chunks: list[str]) -> list[str]:
    chunk_summaries = []
    for chunk in chunks:
        chunk_summaries.append(summarize_chunk(chunk))
    return chunk_summaries


async def summarize_all_chunks_with_progress(chunks: list[str], progress_callback):
    chunk_summaries = []
    total = len(chunks)

    for index, chunk in enumerate(chunks, start=1):
        summary = summarize_chunk(chunk)
        chunk_summaries.append(summary)
        await progress_callback(index, total)

    return chunk_summaries


def combine_summaries(chunk_summaries: list[str]) -> str:
    combined_text = "\n\n".join(f"- {s}" for s in chunk_summaries)

    prompt = f"""Below are summaries of different sections of a document.
Combine them into a single, well-organized, coherent summary of the
entire document. Remove any repetition. Write it as flowing paragraphs,
not a list.

Section summaries:
{combined_text}

Final Combined Summary:"""

    try:
        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise RuntimeError(f"Ollama final summarization failed: {e}")

    return response["message"]["content"].strip()