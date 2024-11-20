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

def get_diffs(repo, amount, file:str):
    commits = list(repo.iter_commits('HEAD', max_count=10))
    commits = list(repo.iter_commits('HEAD', paths=[file], max_count=amount))

    # Iterate through the commits and print their diffs
    diff_list = []

    for i, commit in enumerate(commits, 1):
        diff = repo.git.show(commit.hexsha, pretty='', patch=True)
        diff_list.insert(0, f"# Diff {i}:\n\n```\n{diff}\n```") 
    return diff_list





if __name__ == "__main__":
    repo = create_repo("C:\\Users\\aschaerer\\Documents\\BPAS-Enveritus2")
    print("\n\n".join(get_diffs(repo, 4, "C:\\Users\\aschaerer\\Documents\\BPAS-Enveritus2\\Enveritus2\\Services\\SessionService.cs")))
    


