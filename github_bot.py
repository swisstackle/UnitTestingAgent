from github import Github

from github import Auth
from git import Repo
import random

def create_repo(root_directory):
    return Repo(root_directory)

def create_branch(repo, branchname):
    # First replace backslashes with forward slashes for consistency
    branchname = branchname.replace('\\', '/')
    
    # Check if branch exists in repo.heads
    try:
        if branchname in repo.heads:
            return repo.heads[branchname]
        return repo.create_head(branchname)
    except Exception as e:
        print(f"Error handling branch {branchname}: {str(e)}")
        raise

def checkout_branch(branch):
    branch.checkout()

def stage_and_commit(repo, filenames : list[str], commitmessage : str):
    repo.index.add(filenames)
    repo.index.commit(commitmessage)

def push_to_origin(repo, branch):
    origin = repo.remote(name='origin')
    origin.push([branch.name], set_upstream=True)

def create_pr(title, description, head, base, repo):
    auth = Auth.Token("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")
    g = Github(auth=auth)

    head = head.replace('\\', '/')
    repo = g.get_repo(repo)
    pr = repo.create_pull(base=base, head=head, title=title, body=description)
    g.close()


def create_pr_to_master_on_lean(title, description, head):
    create_pr(title, description, head, "master", "swisstackle/Lean")

def get_random_input():
    print("Please enter any random input:")
    user_input = input()
    print(f"You entered: {user_input}")

if __name__ == "__main__":
    print("This is a test line.")
    get_random_input()


