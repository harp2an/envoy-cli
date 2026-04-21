"""Pipeline: chain multiple envoy operations into a named, reusable sequence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir


class PipelineError(Exception):
    pass


VALID_STEPS = {"push", "pull", "rotate", "snapshot", "lint", "validate"}


def _pipeline_path(store_dir: Path) -> Path:
    return store_dir / "pipelines.json"


def _load_pipelines(store_dir: Path) -> dict[str, Any]:
    p = _pipeline_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pipelines(store_dir: Path, data: dict[str, Any]) -> None:
    _pipeline_path(store_dir).write_text(json.dumps(data, indent=2))


def create_pipeline(name: str, steps: list[str], store_dir: Path | None = None) -> None:
    """Register a named pipeline with an ordered list of step names."""
    store_dir = store_dir or get_store_dir()
    if not name.strip():
        raise PipelineError("Pipeline name must not be empty.")
    invalid = [s for s in steps if s not in VALID_STEPS]
    if invalid:
        raise PipelineError(f"Unknown step(s): {', '.join(invalid)}. Valid: {', '.join(sorted(VALID_STEPS))}")
    if not steps:
        raise PipelineError("Pipeline must contain at least one step.")
    pipelines = _load_pipelines(store_dir)
    pipelines[name] = {"steps": steps}
    _save_pipelines(store_dir, pipelines)


def get_pipeline(name: str, store_dir: Path | None = None) -> list[str]:
    """Return the steps for a named pipeline, raising PipelineError if not found."""
    store_dir = store_dir or get_store_dir()
    pipelines = _load_pipelines(store_dir)
    if name not in pipelines:
        raise PipelineError(f"Pipeline '{name}' not found.")
    return pipelines[name]["steps"]


def delete_pipeline(name: str, store_dir: Path | None = None) -> None:
    """Remove a named pipeline."""
    store_dir = store_dir or get_store_dir()
    pipelines = _load_pipelines(store_dir)
    if name not in pipelines:
        raise PipelineError(f"Pipeline '{name}' not found.")
    del pipelines[name]
    _save_pipelines(store_dir, pipelines)


def list_pipelines(store_dir: Path | None = None) -> dict[str, list[str]]:
    """Return all pipelines as {name: [steps]}."""
    store_dir = store_dir or get_store_dir()
    raw = _load_pipelines(store_dir)
    return {name: info["steps"] for name, info in raw.items()}
