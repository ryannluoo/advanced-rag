"""Publish the completed embedding run."""

import json
from pathlib import Path


def write_manifest(destination: Path, payload: dict) -> None:
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(destination)
