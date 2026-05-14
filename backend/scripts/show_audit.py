from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.runtime.audit_logger import AuditLogger


def main() -> None:
    trace_id = sys.argv[1] if len(sys.argv) > 1 else ""
    logger = AuditLogger()
    record = logger.read(trace_id) if trace_id else logger.list_recent(1)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
