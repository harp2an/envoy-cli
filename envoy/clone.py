"""Clone a project's env to a new project name."""

from envoy.storage import load_env, store_env, load_manifest
from envoy.audit import record_event


class CloneError(Exception):
    pass


def clone_project(src: str, dst: str, password: str, new_password: str | None = None) -> None:
    """Clone src project env into dst project.

    Args:
        src: source project name
        dst: destination project name
        password: password for the source project
        new_password: password for the destination project (defaults to same as src)
    """
    manifest = load_manifest()
    if src not in manifest:
        raise CloneError(f"Source project '{src}' not found")
    if dst in manifest:
        raise CloneError(f"Destination project '{dst}' already exists")

    plaintext = load_env(src, password)
    store_env(dst, plaintext, new_password or password)

    record_event("clone", {"src": src, "dst": dst})


def clone_with_rename(src: str, dst: str, password: str, new_password: str | None = None, prefix: str = "", suffix: str = "") -> None:
    """Clone and optionally prefix/suffix all keys in the env."""
    from envoy.diff import parse_pairs

    manifest = load_manifest()
    if src not in manifest:
        raise CloneError(f"Source project '{src}' not found")
    if dst in manifest:
        raise CloneError(f"Destination project '{dst}' already exists")

    plaintext = load_env(src, password)
    if prefix or suffix:
        pairs = parse_pairs(plaintext)
        lines = [f"{prefix}{k}{suffix}={v}" for k, v in pairs.items()]
        plaintext = "\n".join(lines)

    store_env(dst, plaintext, new_password or password)
    record_event("clone", {"src": src, "dst": dst, "prefix": prefix, "suffix": suffix})
