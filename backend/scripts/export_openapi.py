"""Write the OpenAPI contract to contracts/openapi.json (or check it is up to date).

Usage:
    uv run python scripts/export_openapi.py          # write
    uv run python scripts/export_openapi.py --check  # CI: fail if outdated
"""

import json
import sys
from pathlib import Path

from ups_kulka.main import create_app

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "openapi.json"


def main() -> int:
    spec = json.dumps(create_app().openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        current = CONTRACT.read_text(encoding="utf-8") if CONTRACT.exists() else ""
        if current != spec:
            sys.stderr.write("contracts/openapi.json is outdated: run `make openapi`\n")
            return 1
        return 0
    CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT.write_text(spec, encoding="utf-8")
    sys.stdout.write(f"written {CONTRACT}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
