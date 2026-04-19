"""Archive (export to zip) and unarchive (import from zip) projects."""

import io
import json
import zipfile
from pathlib import Path

from envoy.storage import get_store_dir, load_manifest, store_env, load_env


class ArchiveError(Exception):
    pass


def archive_project(project: str, password: str, dest: Path) -> Path:
    """Write an encrypted project blob into a zip archive at dest."""
    store_dir = get_store_dir()
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ArchiveError(f"Project '{project}' not found")

    ciphertext = load_env(store_dir, project, password)

    meta = {"project": project, "manifest_entry": manifest[project]}
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("env.enc", ciphertext)
        zf.writestr("meta.json", json.dumps(meta))

    dest.write_bytes(zip_buf.getvalue())
    return dest


def archive_all(password: str, dest: Path) -> list[str]:
    """Archive every project into a single zip. Returns list of project names."""
    store_dir = get_store_dir()
    manifest = load_manifest(store_dir)
    if not manifest:
        raise ArchiveError("No projects to archive")

    archived = []
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for project in manifest:
            try:
                ciphertext = load_env(store_dir, project, password)
                meta = {"project": project, "manifest_entry": manifest[project]}
                zf.writestr(f"{project}/env.enc", ciphertext)
                zf.writestr(f"{project}/meta.json", json.dumps(meta))
                archived.append(project)
            except Exception as exc:
                raise ArchiveError(f"Failed to archive '{project}': {exc}") from exc
    return archived


def unarchive_project(src: Path, password: str, overwrite: bool = False) -> str:
    """Restore a single-project archive. Returns project name."""
    if not src.exists():
        raise ArchiveError(f"Archive not found: {src}")

    store_dir = get_store_dir()
    manifest = load_manifest(store_dir)

    with zipfile.ZipFile(src, "r") as zf:
        names = zf.namelist()
        if "env.enc" not in names or "meta.json" not in names:
            raise ArchiveError("Invalid archive: missing env.enc or meta.json")
        meta = json.loads(zf.read("meta.json"))
        project = meta["project"]
        if project in manifest and not overwrite:
            raise ArchiveError(f"Project '{project}' already exists; use overwrite=True")
        ciphertext = zf.read("env.enc").decode()

    store_env(store_dir, project, password, ciphertext)
    return project
