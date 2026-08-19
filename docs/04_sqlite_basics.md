# SQLite for Local Data

SQLite is a lightweight, serverless, self-contained SQL database engine
stored as a single file on disk. It is the world's most widely deployed
database engine. Its advantages include requiring no separate server, wide
cross-platform support, and simple integration into any application.

In this project, SQLite stores each document chunk's text together with
its embedding vector (serialized as JSON) in a single `chunks` table. This
makes it easy to persist the knowledge base between runs: the assistant
only needs to re-embed documents when they are added or changed, not every
time the program starts.

Basic operations used here are: creating a table if it doesn't exist,
inserting a row per chunk, and selecting all rows back out to compute
similarity scores against a query.
