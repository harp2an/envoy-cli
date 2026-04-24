"""Project status reporting: summarise key metadata for a project in one call."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envoy.storage import get_store_dir, load_manifest
from envoy.lock import is_locked
from envoy.pin import get_pin
from envoy.ttl import get_ttl, is_expired
from envoy.tag import list_tags


class StatusError(Exception):
    """Raised when status cannot be determined."""


@dataclass
class ProjectStatus:
    project: str
    exists: bool
    locked: bool
    pinned_version: Optional[str]
    tags: list[str] = field(default_factory=list)
    ttl_expiry: Optional[str] = None
    ttl_expired: bool = False

    def as_dict(self) -> dict:
        return {
            "project": self.project,
            "exists": self.exists,
            "locked": self.locked,
            "pinned_version": self.pinned_version,
            "tags": self.tags,
            "ttl_expiry": self.ttl_expiry,
            "ttl_expired": self.ttl_expired,
        }


def get_status(project: str, store_dir: Optional[str] = None) -> ProjectStatus:
    """Return a :class:`ProjectStatus` for *project*."""
    base = get_store_dir() if store_dir is None else store_dir
    manifest = load_manifest(base)

    exists = project in manifest

    locked = False
    pinned = None
    tags: list[str] = []
    expiry: Optional[str] = None
    expired = False

    if exists:
        try:
            locked = is_locked(project, base)
        except Exception:
            locked = False

        try:
            pin = get_pin(project, base)
            pinned = pin.get("version") if pin else None
        except Exception:
            pinned = None

        try:
            tags = list_tags(manifest, project)
        except Exception:
            tags = []

        try:
            ttl_info = get_ttl(project, base)
            if ttl_info:
                expiry = ttl_info.get("expires_at")
                expired = is_expired(project, base)
        except Exception:
            expiry = None
            expired = False

    return ProjectStatus(
        project=project,
        exists=exists,
        locked=locked,
        pinned_version=pinned,
        tags=tags,
        ttl_expiry=expiry,
        ttl_expired=expired,
    )
