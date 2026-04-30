"""Compliance checking for env projects against defined standards."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envoy.storage import get_store_dir, load_manifest


class ComplianceError(Exception):
    pass


STANDARDS = {
    "basic": {"required_keys": [], "forbidden_keys": [], "max_keys": 100},
    "strict": {"required_keys": [], "forbidden_keys": ["DEBUG", "SECRET_KEY"], "max_keys": 50},
    "minimal": {"required_keys": [], "forbidden_keys": [], "max_keys": 20},
}


@dataclass
class ComplianceResult:
    project: str
    standard: str
    passed: bool
    violations: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "project": self.project,
            "standard": self.standard,
            "passed": self.passed,
            "violations": self.violations,
        }


def _compliance_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / "compliance.json"


def _load_compliance(store_dir: Optional[Path] = None) -> Dict:
    p = _compliance_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_compliance(data: Dict, store_dir: Optional[Path] = None) -> None:
    _compliance_path(store_dir).write_text(json.dumps(data, indent=2))


def check_compliance(
    project: str,
    standard: str,
    key_count: int,
    present_keys: List[str],
    store_dir: Optional[Path] = None,
) -> ComplianceResult:
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise ComplianceError(f"Project '{project}' not found")
    if standard not in STANDARDS:
        raise ComplianceError(f"Unknown standard '{standard}'. Choose from: {list(STANDARDS)}")

    rules = STANDARDS[standard]
    violations: List[str] = []

    if key_count > rules["max_keys"]:
        violations.append(f"Key count {key_count} exceeds max {rules['max_keys']}")

    for k in rules["required_keys"]:
        if k not in present_keys:
            violations.append(f"Required key '{k}' is missing")

    for k in rules["forbidden_keys"]:
        if k in present_keys:
            violations.append(f"Forbidden key '{k}' is present")

    result = ComplianceResult(
        project=project,
        standard=standard,
        passed=len(violations) == 0,
        violations=violations,
    )

    data = _load_compliance(store_dir)
    data[project] = result.as_dict()
    _save_compliance(data, store_dir)
    return result


def get_compliance(project: str, store_dir: Optional[Path] = None) -> Optional[Dict]:
    return _load_compliance(store_dir).get(project)


def list_compliance(store_dir: Optional[Path] = None) -> Dict:
    return _load_compliance(store_dir)


def remove_compliance(project: str, store_dir: Optional[Path] = None) -> None:
    data = _load_compliance(store_dir)
    if project not in data:
        raise ComplianceError(f"No compliance record for '{project}'")
    del data[project]
    _save_compliance(data, store_dir)
