"""Merge two project envs, with conflict resolution strategies."""

from envoy.storage import load_env, store_env


class MergeError(Exception):
    pass


STRATEGIES = ("ours", "theirs", "union")


def _parse_pairs(raw: str) -> dict:
    pairs = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def merge_envs(base: dict, other: dict, strategy: str = "ours") -> dict:
    """Merge two env dicts. Conflict resolution via strategy."""
    if strategy not in STRATEGIES:
        raise MergeError(f"Unknown strategy '{strategy}'. Choose from: {STRATEGIES}")

    merged = dict(base)
    for key, value in other.items():
        if key not in merged:
            merged[key] = value
        else:
            if strategy == "theirs":
                merged[key] = value
            elif strategy == "union":
                if merged[key] != value:
                    merged[key] = merged[key]  # keep base on conflict, note conflict
            # "ours": keep base value — no action needed
    return merged


def merge_projects(
    src: str,
    dst: str,
    src_password: str,
    dst_password: str,
    strategy: str = "ours",
    store_dir=None,
) -> dict:
    """Load two projects, merge, and save back to dst."""
    src_raw = load_env(src, src_password, store_dir=store_dir)
    dst_raw = load_env(dst, dst_password, store_dir=store_dir)

    src_pairs = _parse_pairs(src_raw)
    dst_pairs = _parse_pairs(dst_raw)

    merged = merge_envs(dst_pairs, src_pairs, strategy=strategy)

    rendered = "\n".join(f"{k}={v}" for k, v in sorted(merged.items()))
    store_env(dst, rendered, dst_password, store_dir=store_dir)
    return merged
