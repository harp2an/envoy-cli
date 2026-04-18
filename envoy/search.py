"""Search across stored env projects for keys or values."""

from envoy.storage import load_manifest, load_env
from envoy.crypto import decrypt


class SearchError(Exception):
    pass


def _parse_pairs(text):
    pairs = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def search_key(key, password, store_dir=None):
    """Return {project: value} for every project containing key."""
    manifest = load_manifest(store_dir)
    results = {}
    for project in manifest.get("projects", {}):
        try:
            ciphertext = load_env(project, store_dir)
            plaintext = decrypt(ciphertext, password)
            pairs = _parse_pairs(plaintext)
            if key in pairs:
                results[project] = pairs[key]
        except Exception:
            continue
    return results


def search_value(pattern, password, store_dir=None):
    """Return {project: {key: value}} for entries whose value contains pattern."""
    manifest = load_manifest(store_dir)
    results = {}
    for project in manifest.get("projects", {}):
        try:
            ciphertext = load_env(project, store_dir)
            plaintext = decrypt(ciphertext, password)
            pairs = _parse_pairs(plaintext)
            matches = {k: v for k, v in pairs.items() if pattern in v}
            if matches:
                results[project] = matches
        except Exception:
            continue
    return results
