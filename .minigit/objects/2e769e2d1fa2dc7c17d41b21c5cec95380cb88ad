import os
import json
import hashlib


def get_file_hash(file_path):

    with open(file_path, "rb") as file:
        data = file.read()

    return hashlib.sha1(data).hexdigest()

def status():

    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    index_path = os.path.join(repo_path, "index")

    with open(index_path, "r") as index_file:
        index = json.load(index_file)

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as head_file:
        head_content = head_file.read().strip()

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return

    branch_ref = head_content[5:]
    branch_name = os.path.basename(branch_ref)

    branch_path = os.path.join(repo_path, branch_ref)

    head_tree = {}

    if os.path.isfile(branch_path):
        with open(branch_path, "r") as branch_file:
            last_commit = branch_file.read().strip()

        if last_commit:
            commit_path = os.path.join(
                repo_path, "objects", last_commit
            )

            if not os.path.isfile(commit_path):
                print("Commit object not found.")
                return

            with open(commit_path, "r") as commit_file:
                commit_data = json.load(commit_file)

            head_tree = commit_data["tree"]

    working_files = set()

    for root, dirs, files in os.walk("."):

        dirs[:] = [
            d for d in dirs
            if d not in [".git", ".minigit", "__pycache__"]
        ]

        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, ".")
            working_files.add(relative_path)

    staged_new = []
    staged_modified = []
    modified = []
    deleted = []

    for file_path, staged_hash in index.items():

        if file_path not in working_files:
            deleted.append(file_path)
            continue

        current_hash = get_file_hash(file_path)

        if staged_hash != head_tree.get(file_path):
            if file_path not in head_tree:
                staged_new.append(file_path)
            else:
                staged_modified.append(file_path)

        if current_hash != staged_hash:
            modified.append(file_path)

    untracked = working_files - set(index.keys())

    print("On branch", branch_name)
    print()

    if staged_new or staged_modified:
        print("Changes to be committed:")

        for file_path in staged_new:
            print("    new file:", file_path)

        for file_path in staged_modified:
            print("    modified:", file_path)
        print()
    if modified or deleted:
        print("Changes not staged for commit:")
        for file_path in modified:
            print("    modified:", file_path)
        for file_path in deleted:
            print("    deleted:", file_path)
        print()
    if untracked:
        print("Untracked files:")
        for file_path in sorted(untracked):
            print("    ", file_path)
        print()
    if not (staged_new or staged_modified or modified or deleted or untracked):
        print("Nothing to commit, working tree clean.")


if __name__ == "__main__":
    status()
