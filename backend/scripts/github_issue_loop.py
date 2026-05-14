from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.runtime.github_client import GitHubClient


def main() -> None:
    client = GitHubClient()
    title = sys.argv[1] if len(sys.argv) > 1 else "DailyFit Agent maintenance task"
    body = sys.argv[2] if len(sys.argv) > 2 else "Created by DailyFit Agent issue loop."
    print(json.dumps(client.create_issue(title, body), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
