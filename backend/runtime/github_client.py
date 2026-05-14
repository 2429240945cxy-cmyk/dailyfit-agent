from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class GitHubClient:
    repo_name: str = "dailyfit-agent"

    @property
    def available(self) -> bool:
        return shutil.which("gh") is not None

    def auth_ok(self) -> bool:
        if not self.available:
            return False
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
        return result.returncode == 0

    def create_issue(self, title: str, body: str, labels: list[str] | None = None) -> dict:
        if not self.auth_ok():
            return {
                "created": False,
                "manual_mode": True,
                "command": f"gh issue create --title {json.dumps(title)} --body {json.dumps(body)}",
            }
        command = ["gh", "issue", "create", "--title", title, "--body", body]
        for label in labels or []:
            command.extend(["--label", label])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return {"created": result.returncode == 0, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
