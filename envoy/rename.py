"""Rename a project in the local store."""

from envoy.storage import load_manifest, save_manifest, get_store_dir
import os


class RenameError(Exception):
    pass


def rename_project(old_name: str, new_name: str) -> None:
    """Rename a project entry and its backing file in the store."""
    if not old_name or not new_name:
        raise RenameError("Project names must not be empty.")
    if old_name == new_name:
        raise RenameError("Old and new names are identical.")

    manifest = load_manifest()
    if old_name not in manifest:
        raise RenameError(f"Project '{old_name}' does not exist.")
    if new_name in manifest:
        raise RenameError(f"Project '{new_name}' already exists.")

    store_dir = get_store_dir()
    old_path = os.path.join(store_dir, manifest[old_name]["file"])
    new_filename = f"{new_name}.env.enc"
    new_path = os.path.join(store_dir, new_filename)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    entry = dict(manifest[old_name])
    entry["file"] = new_filename
    manifest[new_name] = entry
    del manifest[old_name]
    save_manifest(manifest)
