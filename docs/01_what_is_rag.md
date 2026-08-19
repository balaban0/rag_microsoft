# What is RAG (Retrieval-Augmented Generation)?

RAG is an AI design pattern where you Retrieve relevant information from a
document set, Augment the model's input prompt with that info as context,
then have the model Generate an answer. The model's responses are grounded
in your own data, which reduces hallucination and enables source citations.

RAG combines embedding-based semantic search with a large language model
(LLM). Without RAG, an LLM can only answer from what it learned during
training and may get domain-specific questions wrong or make things up.
With RAG, the assistant looks up relevant passages first and gives the
model that context before it answers, so the answer is grounded in your
actual documents instead of the model's general knowledge.

The three steps are:

1. Retrieve - find the passages most relevant to the user's question.
2. Augment - insert those passages into the prompt sent to the model.
3. Generate - the model writes an answer using the provided passages.
