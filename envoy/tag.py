"""Tag/label management for env projects."""

from __future__ import annotations

from envoy.storage import load_manifest, save_manifest


class TagError(Exception):
    pass


def add_tag(project: str, tag: str) -> None:
    """Add a tag to a project."""
    manifest = load_manifest()
    if project not in manifest:
        raise TagError(f"Project '{project}' not found")
    tags: list = manifest[project].setdefault("tags", [])
    if tag in tags:
        raise TagError(f"Tag '{tag}' already exists on project '{project}'")
    tags.append(tag)
    save_manifest(manifest)


def remove_tag(project: str, tag: str) -> None:
    """Remove a tag from a project."""
    manifest = load_manifest()
    if project not in manifest:
        raise TagError(f"Project '{project}' not found")
    tags: list = manifest[project].get("tags", [])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on project '{project}'")
    tags.remove(tag)
    manifest[project]["tags"] = tags
    save_manifest(manifest)


def list_tags(project: str) -> list[str]:
    """Return tags for a project."""
    manifest = load_manifest()
    if project not in manifest:
        raise TagError(f"Project '{project}' not found")
    return list(manifest[project].get("tags", []))


def find_by_tag(tag: str) -> list[str]:
    """Return all projects that have the given tag."""
    manifest = load_manifest()
    return [p for p, meta in manifest.items() if tag in meta.get("tags", [])]
