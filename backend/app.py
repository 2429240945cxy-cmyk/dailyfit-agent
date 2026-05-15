from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.graph.workflow import run_agent
from backend.runtime.audit_logger import AuditLogger
from backend.runtime.config import ROOT_DIR, get_settings
from backend.runtime.llm_usage import UsageStore


class ChatRequest(BaseModel):
    user_id: str = "u1"
    session_id: str = "s1"
    message: str


app = FastAPI(title="DailyFit Agent", version="1.0.0")
WEB_DIR = ROOT_DIR / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "mode": settings.mode,
        "public_mode": settings.public_mode,
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "web": True,
    }


def _source_attribution(tool_results: list[dict]) -> list[dict]:
    sources = []
    for item in tool_results:
        if item.get("name") == "lookup_nutrition":
            result = item["result"]
            sources.append(
                {
                    "name": result["name"],
                    "source": result["source"],
                    "source_url": result.get("source_url"),
                    "source_detail": result.get("source_detail"),
                    "fallback_used": result.get("fallback_used", False),
                    "fallback_reason": result.get("fallback_reason"),
                }
            )
    return sources


@app.post("/chat")
async def chat(request: ChatRequest) -> dict[str, Any]:
    state = await run_agent(request.user_id, request.session_id, request.message)
    return {
        "trace_id": state.trace_id,
        "mode": state.mode,
        "response": state.response,
        "guardian": state.guardian.model_dump() if state.guardian else {},
        "memory_hits": state.memories,
        "tool_results": state.tool_results,
        "source_attribution": _source_attribution(state.tool_results),
        "usage": state.usage.model_dump(),
    }


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def events():
        state = await run_agent(request.user_id, request.session_id, request.message)
        yield f"data: {json.dumps({'trace_id': state.trace_id, 'response': state.response}, ensure_ascii=False)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/profile/{user_id}")
async def profile(user_id: str) -> dict[str, Any]:
    from backend.memory.store import MemoryStore

    store = MemoryStore()
    return {"user_id": user_id, "memories": [m.model_dump() for m in store.list_by_user(user_id)]}


@app.get("/logs")
async def logs() -> dict[str, Any]:
    return {"logs": AuditLogger().list_recent()}


@app.get("/logs/{trace_id}")
async def log_detail(trace_id: str) -> dict[str, Any]:
    record = AuditLogger().read(trace_id)
    if record is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return record


@app.get("/benchmarks/latest")
async def benchmarks_latest() -> dict[str, Any]:
    result_dir = ROOT_DIR / "evals/results"
    results = []
    for path in sorted(result_dir.glob("*_v2_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if "pre_judge_fix" in path.name or "pre_v6" in path.name:
            continue
        try:
            results.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return {"results": results[:8]}


@app.get("/usage/today")
async def usage_today() -> dict[str, Any]:
    return UsageStore().today_summary()
