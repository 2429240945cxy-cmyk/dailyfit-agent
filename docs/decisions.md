# Decisions

- Use FastAPI static files instead of a Node-dependent frontend.
- Use SQLite for memory, cache, usage, and benchmark metadata.
- Use OpenAI Python SDK only with DashScope OpenAI-compatible `base_url`.
- Avoid vector databases for v1; embedding vectors can be stored in SQLite.
