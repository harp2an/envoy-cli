"""Key rotation: re-encrypt stored envs with a new password."""

from __future__ import annotations

from typing import List

from envoy.crypto import decrypt, encrypt
from envoy.storage import list_projects, load_env, store_env


class RotationError(Exception):
    pass


def rotate_project(project: str, old_password: str, new_password: str) -> None:
    """Re-encrypt a single project's env with a new password."""
    try:
        plaintext = load_env(project, old_password)
    except Exception as exc:
        raise RotationError(f"Failed to decrypt '{project}' with old password: {exc}") from exc

    try:
        store_env(project, plaintext, new_password)
    except Exception as exc:
        raise RotationError(f"Failed to re-encrypt '{project}': {exc}") from exc


def rotate_all(old_password: str, new_password: str) -> List[str]:
    """Rotate all projects. Returns list of rotated project names."""
    projects = list_projects()
    if not projects:
        return []

    rotated = []
    errors = []
    for project in projects:
        try:
            rotate_project(project, old_password, new_password)
            rotated.append(project)
        except RotationError as exc:
            errors.append(str(exc))

    if errors:
        raise RotationError("Some projects failed rotation:\n" + "\n".join(errors))

    return rotated
