"""Launch the local development-pilot annotation screen.

From the repository root:

    python3 scripts/annotate_librispeech_pilot.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from annotation.pilot_server import serve  # noqa: E402
from annotation.pilot_workflow import PilotWorkflow  # noqa: E402


def main() -> None:
    workflow = PilotWorkflow(
        ROOT,
        ROOT / "data" / "librispeech" / "annotations" / "phase_1c_pilot_30.csv",
        ROOT / "data" / "librispeech" / "processed" / "dev-clean" / "sample-200.csv",
        ROOT / "data" / "librispeech" / "processed" / "test-clean" / "sample-200.csv",
    )
    if len(workflow) != 30:
        raise SystemExit(f"expected 30 pilot rows, found {len(workflow)}")
    server = serve(workflow)
    print(f"Annotation screen: http://{server.server_address[0]}:{server.server_address[1]}/")
    print("Phase 1C stays blocked until a person saves reviewed rows.")
    server.serve_forever()


if __name__ == "__main__":
    main()
