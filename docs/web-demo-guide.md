# Web Demo Guide

Start:

```bash
uvicorn backend.app:app --port 8000
```

Open `http://localhost:8000`. Type a paragraph in the composer and submit it to
get a chat-style assistant reply. The right inspector updates with guardian
verdict, memory hits, source attribution, tool calls, trace id, usage, cost, and
cache status. Demo buttons still cover nutrition, workout, preference, injury,
and dangerous weight-loss flows.
