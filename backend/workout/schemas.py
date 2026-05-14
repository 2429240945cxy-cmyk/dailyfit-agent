from __future__ import annotations

from pydantic import BaseModel, Field


class Exercise(BaseModel):
    id: str | None = None
    name: str
    primaryMuscles: list[str] = Field(default_factory=list)
    secondaryMuscles: list[str] = Field(default_factory=list)
    equipment: str | list[str] | None = None
    level: str | None = None
    instructions: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)


class WorkoutPlan(BaseModel):
    goal: str
    constraints: list[str] = Field(default_factory=list)
    exercises: list[Exercise] = Field(default_factory=list)
    excluded: list[dict] = Field(default_factory=list)
    source: str = "free-exercise-db"
    fallback_used: bool = False
    fallback_reason: str | None = None
