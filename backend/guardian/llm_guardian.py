from __future__ import annotations

import json

from backend.guardian.classifier import classify_guardian
from backend.guardian.schemas import GuardianVerdict
from backend.runtime.config import get_settings
from backend.runtime.llm import get_judge_client


async def classify_with_optional_llm(message: str) -> GuardianVerdict:
    baseline = classify_guardian(message)
    if baseline.verdict == "deny":
        return baseline
    settings = get_settings()
    if settings.mode != "live":
        return baseline
    client = get_judge_client()
    prompt = (
        "Classify this fitness/nutrition user request as allow, warn, "
        "require_confirmation, or deny. Return JSON with verdict, reason, risk_categories. "
        "Do not provide harmful steps.\n\n"
        f"User request: {message}"
    )
    response = await client.generate(
        [{"role": "user", "content": prompt}], temperature=0.0, purpose="guardian"
    )
    if response.error:
        return baseline
    try:
        payload = json.loads(response.content)
        candidate = GuardianVerdict(
            verdict=payload.get("verdict", baseline.verdict),
            risk_categories=payload.get("risk_categories", baseline.risk_categories),
            reason=payload.get("reason", baseline.reason),
            safe_alternative=payload.get("safe_alternative", baseline.safe_alternative),
            confidence=float(payload.get("confidence", baseline.confidence)),
        )
    except Exception:
        return baseline
    if candidate.verdict == "allow" and baseline.verdict != "allow":
        return baseline
    return candidate
