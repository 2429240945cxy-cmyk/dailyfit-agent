# Architecture

DailyFit Agent uses a small LangGraph workflow:

```text
guardian -> intent -> memory -> tool_selection -> tools -> reflect -> finalize
```

`guardian -> finalize` is used for hard-deny cases. Every path writes a JSON
audit trace with mode, provider, model, guardian verdict, memory hits, tool
results, fallback metadata, usage, and final response.
