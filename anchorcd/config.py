from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import yaml, os

class PolicyOverride(BaseModel):
    image: str
    policy: str  # e.g. "semver:^1.27" or "tag:alpine" or "latest"

class PRConfig(BaseModel):
    labels: List[str] = []
    reviewers: List[str] = []

class WebhookCfg(BaseModel):
    outbound_url: Optional[str] = None
    hmac_secret: Optional[str] = None

class RepoCfg(BaseModel):
    name: str
    provider: Literal["github","gitlab"] = "github"
    repo: str                 # org/name or group/name
    branch: str = "main"
    compose_path: str
    working_dir: str
    deploy_host: str = "local"
    webhooks: WebhookCfg = WebhookCfg()
    update_policy: dict = Field(default_factory=dict)  # { default: str, overrides: [PolicyOverride] }
    pr: PRConfig = PRConfig()

class Secrets(BaseModel):
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None

class AppCfg(BaseModel):
    repos: List[RepoCfg]
    secrets: Secrets

def load_config(path: str) -> AppCfg:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    # expand ${ENV}
    def expand(val):
        return os.path.expandvars(val) if isinstance(val, str) else val
    def recurse(obj):
        if isinstance(obj, dict): return {k: recurse(v) for k, v in obj.items()}
        if isinstance(obj, list): return [recurse(v) for v in obj]
        return expand(obj)
    return AppCfg.model_validate(recurse(raw))