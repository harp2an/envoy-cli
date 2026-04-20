"""Project alias management — map short names to project identifiers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy.storage import get_store_dir


class AliasError(Exception):
    pass


def _alias_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / "aliases.json"


def _load_aliases(store_dir: Optional[Path] = None) -> Dict[str, str]:
    path = _alias_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(aliases: Dict[str, str], store_dir: Optional[Path] = None) -> None:
    path = _alias_path(store_dir)
    path.write_text(json.dumps(aliases, indent=2))


def add_alias(alias: str, project: str, store_dir: Optional[Path] = None) -> None:
    """Map *alias* to *project*. Raises AliasError if alias already exists."""
    aliases = _load_aliases(store_dir)
    if alias in aliases:
        raise AliasError(f"Alias '{alias}' already exists (points to '{aliases[alias]}'). Use update to overwrite.")
    aliases[alias] = project
    _save_aliases(aliases, store_dir)


def update_alias(alias: str, project: str, store_dir: Optional[Path] = None) -> None:
    """Create or overwrite *alias* to point to *project*."""
    aliases = _load_aliases(store_dir)
    aliases[alias] = project
    _save_aliases(aliases, store_dir)


def remove_alias(alias: str, store_dir: Optional[Path] = None) -> None:
    """Remove *alias*. Raises AliasError if it does not exist."""
    aliases = _load_aliases(store_dir)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(aliases, store_dir)


def resolve_alias(alias: str, store_dir: Optional[Path] = None) -> Optional[str]:
    """Return the project name for *alias*, or None if not found."""
    return _load_aliases(store_dir).get(alias)


def list_aliases(store_dir: Optional[Path] = None) -> Dict[str, str]:
    """Return all alias -> project mappings."""
    return _load_aliases(store_dir)
