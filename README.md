# Local RAG Q&A Assistant (Foundry Local)

A fully offline document Q&A assistant built for the "Local RAG AI
Assistant with Microsoft Foundry Local" summer program. It answers
questions about a small collection of documents by retrieving relevant
passages locally (SQLite + embeddings) and feeding them to a local LLM via
[Microsoft Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local) —
no cloud account and no network calls at inference time.

## How it works

1. **Ingestion** (`ingest.py`): documents in `docs/` are split into
   paragraph-based chunks, embedded with a local embedding model, and
   stored in a SQLite database (`data/rag.db`) alongside their source
   file name.
2. **Retrieval** (`retrieval.py`): a user's question is embedded with the
   same model, compared against every stored chunk via cosine similarity,
   and the top-K most relevant chunks are selected.
3. **Generation** (`foundry_client.py`, `main.py`): the retrieved chunks
   are inserted into a system-prompted context, and the local chat model
   generates an answer grounded in that context. If the context doesn't
   contain the answer, the assistant says so instead of guessing. Casual
   greetings/small talk ("hello", "thanks") are recognized separately and
   answered naturally, rather than being treated as unanswerable questions.

```
User question -> embed -> cosine similarity vs SQLite chunks -> top-K chunks
              -> context + question -> local LLM (Foundry Local) -> answer
```

## Requirements

- Windows, macOS, or Linux
- Python 3.9+
- [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/get-started) installed
  and its `foundry` CLI available on PATH
  (Windows: `winget install Microsoft.FoundryLocal`)

## Setup

```powershell
cd rag_assistant
pip install -r requirements.txt
```

`foundry_client.py` drives the `foundry` CLI directly (`server status/start`,
`model download/load/info`) rather than through the `foundry-local-sdk`
Python package, since that package's REST client has drifted out of sync
with recent Foundry Local server versions on some installs. Only `openai`
and `numpy` are required as pip dependencies.

## Running

```powershell
python main.py
```

On first run this will:
- start the Foundry Local service and download the chat model
  (`phi-3.5-mini`) and embedding model (`qwen3-embedding-0.6b`) if not
  already cached,
- ingest every `.md`/`.txt` file in `docs/` into `data/rag.db`,
- drop you into an interactive prompt where you can ask questions.

Type `exit` or `quit` to leave. Use `python main.py --reingest` to force
re-ingestion after changing the documents in `docs/`.

## Adding your own documents

Drop any `.md` or `.txt` files into `docs/` and run
`python main.py --reingest`. Keep documents reasonably short (course
notes, FAQs, manuals) — chunks are split on paragraph boundaries up to
`CHUNK_MAX_CHARS` (see `config.py`).

## Web UI (Streamlit)

A minimal chat-style web front end over the same `answer_query()`
pipeline the CLI uses:

```powershell
streamlit run app_streamlit.py
```

Opens at http://localhost:8501. The sidebar lists the ingested source
documents; the chat area shows each answer along with the source
file(s) it was retrieved from.

## Testing

`evaluate.py` implements the program plan's Week 5 functional-testing
milestone: a fixed set of answerable and unanswerable questions, two
greeting/small-talk regression cases, plus edge cases (blank input, a
vague/general question).

```powershell
python evaluate.py
```

This writes a pass/fail report with response times to `TEST_RESULTS.md`.
Answerable questions pass if the expected source document is retrieved;
unanswerable questions pass if the answer reads as a refusal (a broad
keyword check — the model paraphrases its refusal each time rather than
reproducing the system prompt's exact wording, so this is inherently
approximate, not exact-match). Re-run any time after changing `docs/`,
`config.py`, or the prompt.

## Project layout

```
rag_assistant/
  main.py             CLI entry point / interactive loop
  app_streamlit.py     Streamlit web UI over the same pipeline
  evaluate.py           Functional test suite -> TEST_RESULTS.md
  config.py             Model aliases, paths, chunking + prompt settings
  foundry_client.py     Wraps Foundry Local (chat + embeddings)
  db.py                 SQLite storage for chunks + embeddings
  ingest.py             Document chunking + ingestion pipeline
  retrieval.py           Cosine-similarity top-K retrieval
  docs/                  Knowledge base: 16 short notes. 12 about this
                          project itself (RAG, Foundry Local, embeddings,
                          SQLite, prompt engineering, architecture, project
                          structure, chunking, model trade-offs, testing,
                          web UI, FAQ) + 4 unrelated topics (Blender
                          modeling, Unity URP, narrative design, mesh/LOD)
                          added to demonstrate the knowledge base isn't
                          hardcoded to one domain -- any short docs work
  data/rag.db            Generated on first run
  TEST_RESULTS.md         Generated by evaluate.py
```

## Configuration

Edit `config.py` to change:
- `CHAT_MODEL_ALIAS` / `EMBEDDING_MODEL_ALIAS` — any alias from `foundry model list`
- `TOP_K` — how many chunks are retrieved per question
- `CHUNK_MAX_CHARS` — max characters per chunk during ingestion
- `SYSTEM_PROMPT` — the grounding/citation instructions given to the model

## Known limitations

- Retrieval is brute-force cosine similarity over all stored chunks in
  Python — fine for small document sets, not meant to scale to large
  corpora (a real vector database would be needed there).
- The knowledge base only covers this project's own domain (RAG,
  Foundry Local, embeddings, SQLite, testing, etc.). Real questions
  outside `docs/` are correctly refused rather than answered from the
  model's general knowledge — this is intentional (see
  `05_prompt_engineering.md` / `10_testing_and_evaluation.md`), not a bug.
  To broaden what it can answer, add more documents to `docs/` and
  re-ingest.
- On this development machine (no dedicated GPU), average response time
  is ~6-10s per question, above the plan's ~1-3s target — see
  `TEST_RESULTS.md` for current numbers and mitigation options (smaller
  model, lower `TOP_K`).
