import semver
from typing import List, Optional

def choose_tag(tags: List[str], policy: str) -> Optional[str]:
    mode, _, rule = policy.partition(":")
    if mode == "latest":
        return tags[-1] if tags else None
    if mode == "tag":
        # best-effort: pick highest tag that startswith rule or exact?
        preferred = [t for t in tags if t == rule or t.startswith(rule)]
        return sorted(preferred)[-1] if preferred else None
    if mode == "semver":
        vers = []
        for t in tags:
            try:
                vers.append((semver.Version.parse(t.lstrip("v")), t))
            except Exception:
                pass
        if not vers: return None
        rng = semver.Range(rule) if rule else semver.Range(">=0.0.0")
        candidates = [t for v, t in vers if rng.test(v)]
        if not candidates: return None
        # pick highest version among candidates
        top = sorted([(semver.Version.parse(t.lstrip("v")), t) for t in candidates])[-1][1]
        return top
    return None