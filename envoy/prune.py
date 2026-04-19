"""Prune stale or orphaned project data from the store."""

from __future__ import annotations

from typing import List

from envoy.storage import get_store_dir, load_manifest, save_manifest


class PruneError(Exception):
    pass


def list_orphaned(store_dir: str | None = None) -> List[str]:
    """Return project names whose env file is missing but appear in manifest."""
    base = get_store_dir(store_dir)
    manifest = load_manifest(store_dir)
    orphaned = []
    for project in list(manifest.keys()):
        env_path = base / f"{project}.env"
        if not env_path.exists():
            orphaned.append(project)
    return orphaned


def prune_orphaned(store_dir: str | None = None) -> List[str]:
    """Remove manifest entries whose env files are missing. Returns pruned names."""
    orphaned = list_orphaned(store_dir)
    if not orphaned:
        return []
    manifest = load_manifest(store_dir)
    for project in orphaned:
        del manifest[project]
    save_manifest(manifest, store_dir)
    return orphaned


def prune_project(project: str, store_dir: str | None = None) -> None:
    """Forcibly remove a project's env file and manifest entry."""
    base = get_store_dir(store_dir)
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise PruneError(f"Project '{project}' not found in manifest.")
    env_path = base / f"{project}.env"
    if env_path.exists():
        env_path.unlink()
    del manifest[project]
    save_manifest(manifest, store_dir)
