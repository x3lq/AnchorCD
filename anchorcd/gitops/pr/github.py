from github import Github

class GitHubPR:
    def __init__(self, token: str, repo_fullname: str):
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo_fullname)

    def open_pr(self, head_branch: str, base_branch: str, title: str, body: str, labels=None, reviewers=None):
        pr = self.repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
        if labels: pr.add_to_labels(*labels)
        if reviewers:
            try:
                pr.create_review_request(reviewers=reviewers)
            except Exception:
                pass
        return pr.html_url