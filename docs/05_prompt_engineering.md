# Prompt Engineering for Q&A

Retrieving the right documents isn't enough on its own; how the retrieved
text is presented to the model matters a great deal. Chat models accept a
system message, which sets the assistant's role and rules, and a user
message, which carries the actual question.

For a grounded Q&A assistant, the system prompt should instruct the model
to answer only using the provided context, to say it doesn't know when the
context doesn't contain the answer instead of guessing, and to mention
which source document the information came from. This reduces
hallucination and makes answers easier to trust and verify.

A simple, effective pattern is to put the retrieved passages first,
labeled with their source, followed by the user's question, and to give
the system prompt an explicit instruction not to use outside knowledge.
