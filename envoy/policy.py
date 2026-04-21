"""Policy enforcement for env projects — define and check rules on keys/values."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.storage import get_store_dir, load_manifest


class PolicyError(Exception):
    pass


def _policy_path(store_dir: Path) -> Path:
    return store_dir / "policies.json"


def _load_policies(store_dir: Path) -> dict[str, Any]:
    p = _policy_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(store_dir: Path, data: dict[str, Any]) -> None:
    _policy_path(store_dir).write_text(json.dumps(data, indent=2))


def set_policy(store_dir: Path, project: str, rules: dict[str, Any]) -> None:
    """Attach a policy rule-set to *project*.

    Supported rule keys:
      - required_keys: list[str]
      - forbidden_keys: list[str]
      - max_keys: int
    """
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise PolicyError(f"Project '{project}' not found.")
    allowed = {"required_keys", "forbidden_keys", "max_keys"}
    unknown = set(rules) - allowed
    if unknown:
        raise PolicyError(f"Unknown policy rule(s): {', '.join(sorted(unknown))}")
    data = _load_policies(store_dir)
    data[project] = rules
    _save_policies(store_dir, data)


def get_policy(store_dir: Path, project: str) -> dict[str, Any] | None:
    return _load_policies(store_dir).get(project)


def remove_policy(store_dir: Path, project: str) -> None:
    data = _load_policies(store_dir)
    if project not in data:
        raise PolicyError(f"No policy set for '{project}'.")
    del data[project]
    _save_policies(store_dir, data)


def check_policy(store_dir: Path, project: str, pairs: dict[str, str]) -> list[str]:
    """Return a list of violation messages (empty list means compliant)."""
    policy = get_policy(store_dir, project)
    if policy is None:
        return []
    violations: list[str] = []
    for key in policy.get("required_keys", []):
        if key not in pairs:
            violations.append(f"Missing required key: {key}")
    for key in policy.get("forbidden_keys", []):
        if key in pairs:
            violations.append(f"Forbidden key present: {key}")
    max_keys = policy.get("max_keys")
    if max_keys is not None and len(pairs) > max_keys:
        violations.append(f"Too many keys: {len(pairs)} > {max_keys}")
    return violations
