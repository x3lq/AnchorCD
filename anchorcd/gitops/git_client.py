from git import Repo
from pathlib import Path
import shutil

def ensure_repo(local_path: str, remote_url: str, branch: str = "main") -> Repo:
    p = Path(local_path)
    if not p.exists():
        repo = Repo.clone_from(remote_url, p)
    else:
        repo = Repo(p)
        repo.git.fetch("--all", "--prune")
    repo.git.checkout(branch)
    repo.git.pull("origin", branch)
    return repo

def create_branch_and_commit(repo: Repo, new_branch: str, files_to_add: list, message: str):
    if new_branch in repo.heads:
        repo.git.branch("-D", new_branch)
    repo.git.checkout("-b", new_branch)
    repo.index.add(files_to_add)
    repo.index.commit(message)