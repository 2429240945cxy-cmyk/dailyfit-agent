from __future__ import annotations

from backend.guardian.policy import apply_guardian_policy
from backend.guardian.schemas import GuardianVerdict


def classify_guardian(message: str) -> GuardianVerdict:
    return apply_guardian_policy(message)
