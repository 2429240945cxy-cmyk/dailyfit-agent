from __future__ import annotations

from backend.workout.schemas import Exercise


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
    joined = " ".join(constraints).lower()
    if any(term in joined for term in ["knee", "膝盖", "膝痛"]):
        if any(term in text for term in ["heavy squat", "barbell squat", "jump", "lunge"]):
            return "knee pain rule excludes heavy squat, lunge, and high-impact jump patterns"
        if "quadriceps" in text and "barbell" in text:
            return "knee pain rule excludes quadriceps + barbell patterns"
    if any(term in joined for term in ["shoulder", "肩"]):
        if any(term in text for term in ["overhead press", "shoulder press", "snatch", "upright row"]):
            return "shoulder injury rule excludes overhead or shoulder-heavy movements"
    if any(term in joined for term in ["lower back", "腰", "back pain", "腰伤"]):
        if any(term in text for term in ["deadlift", "good morning", "axial", "barbell row"]):
            return "lower back pain rule excludes deadlift-heavy or axial loading movements"
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
