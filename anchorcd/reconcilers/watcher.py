from anchorcd.compose.parser import list_images
from anchorcd.registry.client import RegistryClient
from anchorcd.registry.policies import choose_tag
from anchorcd.gitops.git_client import ensure_repo, create_branch_and_commit
from anchorcd.gitops.pr.github import GitHubPR
from anchorcd.compose.deployer import deploy
from pathlib import Path
import re, time, yaml

IMG_RE = re.compile(r"^(?P<repo>[^@:]+)(?::(?P<tag>[^@]+))?(?:@(?P<digest>sha256:[0-9a-f]+))?$")

def parse_image(ref: str):
    m = IMG_RE.match(ref)
    if not m: return None
    return m.group("repo"), m.group("tag"), m.group("digest")

def pin_image(ref_repo: str, tag: str, digest: str) -> str:
    return f"{ref_repo}:{tag}@{digest}"

def discover_updates(compose_path: str, default_policy: str, overrides: list[dict]):
    images = list_images(compose_path)
    updates = []
    for svc, ref in images:
        repo, tag, digest = parse_image(ref)
        if not repo: continue
        policy = default_policy
        for o in overrides or []:
            if o.get("image") == repo.split("/")[-1] or o.get("image") == repo:
                policy = o.get("policy", policy)
        rc = RegistryClient()
        tags = rc.list_tags(repo)
        new_tag = choose_tag(tags, policy)
        if not new_tag: continue
        new_digest = rc.get_manifest_digest(repo, new_tag)
        if not new_digest: continue
        # if already pinned to same digest, skip
        if digest == new_digest: continue
        updates.append({"service": svc, "repo": repo, "current": ref, "tag": new_tag, "digest": new_digest})
    return updates

def apply_updates_to_compose(compose_path: str, updates: list[dict]) -> None:
    data = yaml.safe_load(Path(compose_path).read_text())
    for u in updates:
        svc = u["service"]
        data["services"][svc]["image"] = pin_image(u["repo"], u["tag"], u["digest"])
    Path(compose_path).write_text(yaml.safe_dump(data, sort_keys=False))

def reconcile_on_merge(compose_path: str) -> tuple[bool, str]:
    ok, logs = deploy(compose_path)
    return ok, logs

def run_cycle(repo_cfg, secrets):
    # 1) sync repo
    remote_url = f"https://github.com/{repo_cfg.repo}.git" if repo_cfg.provider == "github" else repo_cfg.repo
    repo = ensure_repo(repo_cfg.working_dir, remote_url, repo_cfg.branch)
    compose_path = str(Path(repo_cfg.working_dir) / repo_cfg.compose_path)

    # 2) discover updates
    default = (repo_cfg.update_policy or {}).get("default", "semver:^0")
    overrides = (repo_cfg.update_policy or {}).get("overrides", [])
    ups = discover_updates(compose_path, default, overrides)

    if not ups:
        return {"status": "noop"}

    # 3) create PR
    apply_updates_to_compose(compose_path, ups)
    branch = f"anchorcd/update-{int(time.time())}"
    create_branch_and_commit(repo, branch, [repo_cfg.compose_path],
                             f"chore(images): update {len(ups)} service(s)")
    repo.git.push("origin", branch)

    # PR body
    lines = [f"| service | image | new tag | digest |",
             f"|---|---|---|---|"]
    for u in ups:
        lines.append(f"| {u['service']} | {u['repo']} | {u['tag']} | `{u['digest'][:20]}…` |")
    body = "\n".join(lines)

    if repo_cfg.provider == "github":
        gh = GitHubPR(secrets.github_token, repo_cfg.repo)
        pr_url = gh.open_pr(branch, repo_cfg.branch, "chore(images): propose updates", body,
                            labels=repo_cfg.pr.labels, reviewers=repo_cfg.pr.reviewers)
    else:
        pr_url = "(PR created)"
    return {"status": "pr_opened", "pr_url": pr_url, "updates": ups}