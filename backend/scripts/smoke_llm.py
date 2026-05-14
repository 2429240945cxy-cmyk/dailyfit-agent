from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.memory.embeddings import AliyunEmbeddingClient
from backend.runtime.config import get_settings
from backend.runtime.llm import get_chat_client, get_judge_client


async def run() -> dict:
    settings = get_settings()
    if not settings.dashscope_api_key_present:
        return {
            "chat_ok": False,
            "judge_ok": False,
            "embedding_ok": False,
            "usage_tokens": 0,
            "provider": "aliyun_openai",
            "base_url_configured": bool(settings.dashscope_base_url),
            "mode": "live_missing_key_not_run",
            "error": "DASHSCOPE_API_KEY missing",
        }
    chat = await get_chat_client().generate([{"role": "user", "content": "Say ok."}], purpose="chat")
    judge = await get_judge_client().generate(
        [{"role": "user", "content": "Return JSON {\"passed\": true}."}], purpose="judge"
    )
    emb = await AliyunEmbeddingClient().embed("memory smoke")
    usage_tokens = chat.input_tokens + chat.output_tokens + judge.input_tokens + judge.output_tokens
    return {
        "chat_ok": not chat.error and bool(chat.content),
        "judge_ok": not judge.error and bool(judge.content),
        "embedding_ok": bool(emb),
        "usage_tokens": usage_tokens,
        "provider": "aliyun_openai",
        "base_url_configured": bool(settings.dashscope_base_url),
        "mode": "live_real",
    }


def main() -> None:
    print(json.dumps(asyncio.run(run()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
