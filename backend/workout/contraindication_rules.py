from __future__ import annotations

from backend.workout.schemas import Exercise

INJURY_CONTRAINDICATIONS = {
    "knee": [
        "squat",
        "lunge",
        "jump",
        "run",
        "sprint",
        "air bike",
        "leg press",
        "step",
        "stairs",
        "burpee",
        "bound",
        "skip",
        "skating",
        "skater",
        "hop",
        "yoke",
        "atlas",
        "stone",
        "crawl",
        "sled",
    ],
    "shoulder": [
        "overhead press",
        "shoulder press",
        "bench press",
        "pull-up",
        "pull up",
        "lateral raise",
        "snatch",
        "clean",
        "handstand",
        "upright row",
    ],
    "lower_back": ["deadlift", "good morning", "sit-up", "sit up", "leg raise", "barbell row", "kettlebell swing"],
    "wrist": ["push-up", "push up", "handstand", "front rack", "bench press"],
    "ankle": ["jump", "run", "calf raise", "box jump"],
}


def _affected_parts(constraints: list[str]) -> list[str]:
    joined = " ".join(constraints).lower()
    parts = []
    if any(term in joined for term in ["knee", "膝", "膝盖"]):
        parts.append("knee")
    if any(term in joined for term in ["shoulder", "肩"]):
        parts.append("shoulder")
    if any(term in joined for term in ["lower back", "back pain", "腰", "背"]):
        parts.append("lower_back")
    if any(term in joined for term in ["wrist", "手腕"]):
        parts.append("wrist")
    if any(term in joined for term in ["ankle", "脚踝"]):
        parts.append("ankle")
    return parts


def exclusion_reason(exercise: Exercise, constraints: list[str]) -> str | None:
    text = " ".join(
        [
            exercise.name,
            " ".join(exercise.primaryMuscles),
            " ".join(exercise.secondaryMuscles),
            str(exercise.equipment or ""),
            " ".join(exercise.instructions),
        ]
    ).lower()
    name = exercise.name.lower()
    for part in _affected_parts(constraints):
        for banned in INJURY_CONTRAINDICATIONS[part]:
            if banned in name or banned in text:
                return f"{part} injury rule excludes {banned}"
    if "knee" in _affected_parts(constraints):
        if "quadriceps" in text and "barbell" in text:
            return "knee pain rule excludes quadriceps + barbell patterns"
    return None


def filter_contraindicated(
    exercises: list[Exercise], constraints: list[str], limit: int = 6
) -> tuple[list[Exercise], list[dict]]:
    kept: list[Exercise] = []
    excluded: list[dict] = []
    for exercise in exercises:
        reason = exclusion_reason(exercise, constraints)
        if reason:
            excluded.append({"name": exercise.name, "reason": reason})
            continue
        kept.append(exercise)
        if len(kept) >= limit:
            break
    return kept, excluded
