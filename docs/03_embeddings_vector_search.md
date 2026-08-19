# Embeddings and Vector Search

Text embeddings are numeric vector representations of text that capture
semantic meaning. Similar text produces similar vectors, which enables
semantic search: you can find passages that mean the same thing as a
query even if they don't share the exact same words.

To perform semantic search, you embed every document chunk once and store
the resulting vectors. When a user asks a question, you embed the question
with the same embedding model, then measure the similarity between the
question's vector and each stored vector, commonly with cosine similarity.
The chunks with the highest similarity scores are the most relevant and
are returned as the top matches.

For small document collections (a handful of documents), it is perfectly
fine to keep all vectors in memory and compare them one by one in a loop.
Specialized vector databases only become necessary at a much larger scale.
