# Project Architecture

This assistant's architecture keeps every component on one machine, so it
can run fully offline. It has four parts:

- Client interface: a console (CLI) loop where the user types a question.
- Server/pipeline layer: the code that handles a query by embedding it,
  retrieving relevant chunks, and calling the local LLM to generate an
  answer.
- Data layer: a SQLite database file that stores document chunks and
  their embedding vectors.
- AI layer: Foundry Local, which performs on-device inference for both
  the embedding model and the chat model.

The flow for answering a question is: the user's question is embedded,
the embedding is compared against every stored chunk's embedding using
cosine similarity, the top few chunks are selected as context, and the
context plus the question are sent to the local chat model, which returns
an answer grounded in the retrieved text.
