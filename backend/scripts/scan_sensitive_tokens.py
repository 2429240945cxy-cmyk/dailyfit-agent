from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"^\s*DASHSCOPE_API_KEY[ \t]*=[ \t]*[^#\s]+", re.MULTILINE),
    re.compile(r"^\s*GITHUB_TOKEN[ \t]*=[ \t]*gh[pousr]_[A-Za-z0-9_]+", re.MULTILINE),
]

SKIP_DIRS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", "data/cache"}
SKIP_SUFFIXES = {".db", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip"}
ALLOW_EMPTY_ASSIGNMENTS = {"DASHSCOPE_API_KEY=", "GITHUB_TOKEN=", "USDA_API_KEY="}
ALLOW_PLACEHOLDERS = {"your_local_key", "<local-value>", "<your-key>", "your_key"}


def should_skip(path: Path) -> bool:
    if path.name == "scan_sensitive_tokens.py":
        return True
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    return path.suffix.lower() in SKIP_SUFFIXES


def scan() -> list[str]:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                token = match.group(0)
                if token in ALLOW_EMPTY_ASSIGNMENTS:
                    continue
                if any(placeholder in token for placeholder in ALLOW_PLACEHOLDERS):
                    continue
                findings.append(f"{path.relative_to(ROOT)}: sensitive token pattern {pattern.pattern}")
    return findings


def main() -> None:
    findings = scan()
    if findings:
        print("\n".join(findings))
        raise SystemExit(1)
    print("sensitive token scan passed")


if __name__ == "__main__":
    main()
