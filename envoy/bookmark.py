"""Bookmark support: save named references to project+key pairs."""

import json
from pathlib import Path
from envoy.storage import get_store_dir, load_manifest


class BookmarkError(Exception):
    pass


def _bookmark_path(store_dir: Path) -> Path:
    return store_dir / "bookmarks.json"


def _load_bookmarks(store_dir: Path) -> dict:
    path = _bookmark_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_bookmarks(store_dir: Path, data: dict) -> None:
    _bookmark_path(store_dir).write_text(json.dumps(data, indent=2))


def add_bookmark(store_dir: Path, name: str, project: str, key: str) -> None:
    """Create or overwrite a named bookmark pointing to project:key."""
    if not name:
        raise BookmarkError("Bookmark name must not be empty")
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise BookmarkError(f"Project '{project}' not found")
    bookmarks = _load_bookmarks(store_dir)
    bookmarks[name] = {"project": project, "key": key}
    _save_bookmarks(store_dir, bookmarks)


def remove_bookmark(store_dir: Path, name: str) -> None:
    """Remove a bookmark by name."""
    bookmarks = _load_bookmarks(store_dir)
    if name not in bookmarks:
        raise BookmarkError(f"Bookmark '{name}' not found")
    del bookmarks[name]
    _save_bookmarks(store_dir, bookmarks)


def get_bookmark(store_dir: Path, name: str) -> dict | None:
    """Return the bookmark dict or None if not found."""
    return _load_bookmarks(store_dir).get(name)


def list_bookmarks(store_dir: Path) -> list[dict]:
    """Return all bookmarks as a list of dicts with name, project, key."""
    bookmarks = _load_bookmarks(store_dir)
    return [
        {"name": n, "project": v["project"], "key": v["key"]}
        for n, v in sorted(bookmarks.items())
    ]
