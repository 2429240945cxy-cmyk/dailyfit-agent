from __future__ import annotations

import json

from backend.runtime.config import ROOT_DIR


def load_mock_responses() -> dict:
    path = ROOT_DIR / "backend/runtime/fixtures/mock_responses.json"
    return json.loads(path.read_text(encoding="utf-8"))


def deterministic_embedding(text: str, dim: int = 1024) -> list[float]:
    values = [0.0] * dim
    for index, char in enumerate(text):
        values[index % dim] += (ord(char) % 97) / 97.0
    norm = sum(v * v for v in values) ** 0.5 or 1.0
    return [round(v / norm, 6) for v in values]
