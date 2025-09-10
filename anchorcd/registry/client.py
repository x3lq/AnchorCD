import requests
from typing import List, Tuple, Optional

class RegistryClient:
    def __init__(self, registry="registry-1.docker.io", username=None, password=None):
        self.registry = registry
        self.username = username
        self.password = password

    def _repo_url(self, repo: str) -> str:
        # docker hub: library/nginx needs special namespace if no "/"
        if self.registry.endswith("docker.io") and "/" not in repo:
            repo = f"library/{repo}"
        return f"https://{self.registry}/v2/{repo}"

    def list_tags(self, repo: str) -> List[str]:
        r = requests.get(self._repo_url(repo) + "/tags/list")
        r.raise_for_status()
        return (r.json().get("tags") or [])

    def get_manifest_digest(self, repo: str, reference: str) -> Optional[str]:
        headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
        r = requests.get(self._repo_url(repo) + f"/manifests/{reference}", headers=headers)
        r.raise_for_status()
        return r.headers.get("Docker-Content-Digest")