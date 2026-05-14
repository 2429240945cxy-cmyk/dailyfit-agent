from __future__ import annotations

from dataclasses import dataclass

from backend.guardian.schemas import GuardianVerdict


@dataclass(frozen=True)
class Rule:
    category: str
    verdict: str
    keywords: tuple[str, ...]
    reason: str
    safe_alternative: str


RULES = [
    Rule(
        "prompt_injection",
        "deny",
        ("ignore previous", "忽略之前", "系统提示", "泄露", "developer message", "api key"),
        "The request attempts to bypass system or safety instructions.",
        "I can help with fitness and nutrition questions without exposing hidden instructions or secrets.",
    ),
    Rule(
        "extreme_weight_loss",
        "deny",
        ("一天瘦", "三天瘦", "lose 10 kg in a week", "water fast", "不吃饭", "断食七天"),
        "Extreme weight-loss requests can be unsafe.",
        "Aim for a moderate calorie deficit and consult a qualified clinician for medical needs.",
    ),
    Rule(
        "eating_disorder_risk",
        "require_confirmation",
        ("催吐", "binge purge", "厌食", "吃了就吐", "低于500卡"),
        "The request may indicate eating-disorder risk.",
        "I can support safer meal structure and encourage professional support.",
    ),
    Rule(
        "supplement_abuse",
        "deny",
        ("滥用", "超剂量", "clenbuterol", "dnp", "类固醇", "steroid cycle"),
        "Supplement or drug abuse can cause serious harm.",
        "Use evidence-based nutrition and speak with a licensed medical professional.",
    ),
    Rule(
        "medical_condition",
        "warn",
        ("糖尿病", "高血压", "心脏病", "pregnant", "kidney disease"),
        "Medical conditions require individualized clinical guidance.",
        "I can offer general wellness information and recommend clinician input.",
    ),
    Rule(
        "underage_or_vulnerable",
        "require_confirmation",
        ("13岁", "14岁", "15岁", "under 16", "teen cutting"),
        "Minors and vulnerable users need extra caution.",
        "Use age-appropriate activity and involve a guardian or clinician.",
    ),
    Rule(
        "injury_training",
        "warn",
        ("膝盖疼", "膝盖痛", "shoulder injury", "肩伤", "腰伤", "lower back pain"),
        "Training with injury symptoms requires caution.",
        "Prefer pain-free movements and seek medical assessment for persistent symptoms.",
    ),
]

VERDICT_RANK = {"allow": 0, "warn": 1, "require_confirmation": 2, "deny": 3}


def apply_guardian_policy(message: str) -> GuardianVerdict:
    text = message.lower()
    matched = []
    for rule in RULES:
        if any(keyword.lower() in text for keyword in rule.keywords):
            matched.append(rule)
    if not matched:
        return GuardianVerdict(verdict="allow", reason="No high-risk health or prompt-injection pattern matched.")
    strongest = max(matched, key=lambda rule: VERDICT_RANK[rule.verdict])
    categories = []
    for rule in matched:
        if rule.category not in categories:
            categories.append(rule.category)
    return GuardianVerdict(
        verdict=strongest.verdict,  # type: ignore[arg-type]
        risk_categories=categories,  # type: ignore[arg-type]
        reason=strongest.reason,
        safe_alternative=strongest.safe_alternative,
        confidence=0.92 if strongest.verdict == "deny" else 0.78,
    )
