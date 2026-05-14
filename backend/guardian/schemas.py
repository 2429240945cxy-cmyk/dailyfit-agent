from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GuardianVerdictLiteral = Literal["allow", "warn", "require_confirmation", "deny"]
RiskCategory = Literal[
    "extreme_weight_loss",
    "eating_disorder_risk",
    "injury_training",
    "supplement_abuse",
    "medical_condition",
    "underage_or_vulnerable",
    "prompt_injection",
]


class GuardianVerdict(BaseModel):
    verdict: GuardianVerdictLiteral = "allow"
    risk_categories: list[RiskCategory] = Field(default_factory=list)
    reason: str = ""
    safe_alternative: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
