from github import Github, Auth
from git import Repo
import os
from typing import List, Optional

class GitHubManager:
    def __init__(self, directory_to_repo: str, github_token: Optional[str] = None):
        self.directory_to_repo = directory_to_repo
        self.github_token = github_token or os.getenv("GITHUB_PAT")
        if not self.github_token:
            raise ValueError("GitHub token is required")
        self.repo = Repo(os.path.abspath(self.directory_to_repo))
        self.github = None

    def get_repo(self) -> Repo:
        """Initialize repository connection"""
        return self.repo

    def get_github_client(self) -> Github:
        """Get authenticated GitHub client"""
        if not self.github:
            auth = Auth.Token(self.github_token)
            self.github = Github(auth=auth)
        return self.github

    def get_or_create_branch(self, branchname: str):
        """Create and return a new branch"""
        branchname = branchname.replace('\\', '/')
        return (self.repo.heads[branchname] 
                if branchname in self.repo.heads 
                else self.repo.create_head(branchname))

    def stage_and_commit(self, filenames: List[str], commit_message: str) -> None:
        """Stage and commit files"""
        self.repo.index.add(filenames)
        self.repo.index.commit(commit_message)

    def checkout_branch(self, branch) -> None:
        branch.checkout()

    def push_to_origin(self, branch, retries: int = 3) -> None:
        """Push changes to origin with retry logic"""
        for attempt in range(retries):
            try:
                origin = self.repo.remote(name='origin')
                origin.push([branch.name], set_upstream=True)
                return
            except Exception as e:
                if attempt == retries - 1:
                    raise

    def create_pull_request(self, title: str, description: str, 
                          head: str, base: str, repo_name: str) -> dict:
        """Create a pull request"""
        try:
            github = self.get_github_client()
            github_repo = github.get_repo(repo_name)
            return github_repo.create_pull(
                title=title,
                body=description,
                head=head.replace('\\', '/'),
                base=base
            )
        finally:
            if self.github:
                self.github.close()

    def get_diffs(self, filename: str, amount: int = 1) -> List[str]:
        """Get diffs for a specific file"""
        commits = list(self.repo.iter_commits('HEAD', paths=[filename], max_count=amount))
        return [
            f"# Diff {len(commits) - i}:\n\n```\n{self.repo.git.show(commit.hexsha, pretty='', patch=True)}\n```"
            for i, commit in enumerate(commits)
        ]

