# Document Chunking Strategy

Before a document can be embedded and retrieved, it needs to be split
into smaller passages, or "chunks." Chunking matters because embedding an
entire long document as one vector blurs together many different topics,
which hurts retrieval accuracy; chunking too finely (e.g. one sentence
per chunk) loses surrounding context that the model needs to answer well.

This project's ingestion pipeline (`ingest.chunk_text`) splits each
document on blank-line paragraph boundaries, then greedily groups
consecutive paragraphs together until adding another paragraph would
exceed `CHUNK_MAX_CHARS` (800 characters by default, configured in
`config.py`). This keeps each chunk to roughly one to three paragraphs,
matching the passage-level granularity that works well for short course
notes, FAQs, and manuals.

Every chunk is stored in SQLite together with its source file name, so
that when a chunk is retrieved for a question, the assistant can tell the
user exactly which document the information came from.
