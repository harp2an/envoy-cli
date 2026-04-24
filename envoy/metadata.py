"""Project metadata: attach arbitrary key-value annotations to a project."""

import json
from pathlib import Path
from envoy.storage import get_store_dir, load_manifest


class MetadataError(Exception):
    pass


def _metadata_path(store_dir: Path) -> Path:
    return store_dir / "metadata.json"


def _load_metadata(store_dir: Path) -> dict:
    path = _metadata_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_metadata(store_dir: Path, data: dict) -> None:
    _metadata_path(store_dir).write_text(json.dumps(data, indent=2))


def set_metadata(project: str, key: str, value: str, store_dir: Path | None = None) -> None:
    """Attach a metadata annotation to *project*."""
    store_dir = store_dir or get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise MetadataError(f"Project '{project}' not found.")
    if not key:
        raise MetadataError("Metadata key must not be empty.")
    data = _load_metadata(store_dir)
    data.setdefault(project, {})[key] = value
    _save_metadata(store_dir, data)


def get_metadata(project: str, key: str, store_dir: Path | None = None) -> str | None:
    """Return the metadata value for *key* on *project*, or None."""
    store_dir = store_dir or get_store_dir()
    data = _load_metadata(store_dir)
    return data.get(project, {}).get(key)


def remove_metadata(project: str, key: str, store_dir: Path | None = None) -> None:
    """Remove a metadata annotation from *project*."""
    store_dir = store_dir or get_store_dir()
    data = _load_metadata(store_dir)
    project_meta = data.get(project, {})
    if key not in project_meta:
        raise MetadataError(f"Key '{key}' not found on project '{project}'.")
    del project_meta[key]
    data[project] = project_meta
    _save_metadata(store_dir, data)


def list_metadata(project: str, store_dir: Path | None = None) -> dict:
    """Return all metadata annotations for *project*."""
    store_dir = store_dir or get_store_dir()
    data = _load_metadata(store_dir)
    return dict(data.get(project, {}))


def clear_metadata(project: str, store_dir: Path | None = None) -> None:
    """Remove all metadata annotations for *project*."""
    store_dir = store_dir or get_store_dir()
    data = _load_metadata(store_dir)
    data.pop(project, None)
    _save_metadata(store_dir, data)
