"""Export the current FastAPI OpenAPI schema to versioned docs."""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app


def main() -> None:
    version = app.version or "1.0.0"
    target_dir = Path("docs/api/openapi") / f"v{version}"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "openapi.json"
    schema = app.openapi()
    target_file.write_text(json.dumps(schema, indent=2, sort_keys=True))
    print(f"OpenAPI schema exported to {target_file}")


if __name__ == "__main__":
    main()
