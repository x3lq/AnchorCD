from git import Repo
from pathlib import Path
import shutil

def ensure_repo(repo_name: str, local_path: str, remote_url: str, branch: str = "main", ssh_key: str = None) -> Repo:
    p = Path(local_path)
    p = p.joinpath(repo_name)

    if not p.exists() and ssh_key:
        print("Cloning with SSH key", ssh_key)
        repo = Repo.clone_from(remote_url, p, branch=branch,
                env={"GIT_SSH_COMMAND": f"ssh -i {ssh_key} -o IdentitiesOnly=yes"}
                )
    elif not p.exists():
        repo = Repo.clone_from(remote_url, p, branch=branch)
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