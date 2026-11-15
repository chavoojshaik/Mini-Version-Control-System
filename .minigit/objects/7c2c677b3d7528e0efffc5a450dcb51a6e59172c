import os
import sys

def branch(branch_name=None):

    repo_path = ".minigit"
    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return
    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as head_file:
        head_content = head_file.read().strip()

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return

    current_ref = head_content[5:]
    current_branch = os.path.basename(current_ref)

    branches_path = os.path.join(
        repo_path, "refs", "heads"
    )

    os.makedirs(branches_path, exist_ok=True)

    if branch_name is None:

        branches = sorted(os.listdir(branches_path))

        if not branches:
            print("No branches found.")
            return

        for name in branches:
            if name == current_branch:
                print("*", name)
            else:
                print(" ", name)
        return

    if (
        branch_name.startswith("-")
        or "/" in branch_name
        or "\\" in branch_name
        or branch_name in [".", ".."]
        or branch_name.strip() != branch_name
    ):
        print("Invalid branch name.")
        return

    new_branch_path = os.path.join(
        branches_path, branch_name
    )

    if os.path.exists(new_branch_path):
        print("Branch already exists.")
        return

    current_branch_path = os.path.join(
        repo_path, current_ref
    )

    if os.path.isfile(current_branch_path):
        with open(current_branch_path, "r") as file:
            current_commit = file.read().strip()
    else:
        current_commit = ""

    with open(new_branch_path, "w") as file:
        file.write(current_commit)

    print("Branch created:", branch_name)

if __name__ == "__main__":

    if len(sys.argv) == 1:
        branch()

    elif len(sys.argv) == 2:
        branch(sys.argv[1])

    else:
        print("Usage:")
        print("python3 branch.py")
        print("python3 branch.py <branch_name>")
