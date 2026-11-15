import os
import sys
import json
import hashlib

def restore(file_path):

    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    file_path = os.path.normpath(file_path)

    if (
        os.path.isabs(file_path)
        or file_path == ".."
        or file_path.startswith(".." + os.sep)
        or file_path == "."
        or file_path.split(os.sep)[0] in (".minigit", ".git")
    ):
        print("Invalid file path.")
        return

    if os.path.exists(file_path):
        print("File already exists. Restore cancelled.")
        return

    head_path = os.path.join(repo_path, "HEAD")

    if not os.path.isfile(head_path):
        print("HEAD file not found.")
        return

    with open(head_path, "r") as file:
        head = file.read().strip()

    if not head.startswith("ref: refs/heads/"):
        print("Invalid HEAD reference.")
        return

    branch_ref = head[5:]

    if ".." in branch_ref.split("/"):
        print("Invalid branch reference.")
        return

    branch_path = os.path.join(repo_path, branch_ref)

    if not os.path.isfile(branch_path):
        print("Current branch has no commits.")
        return

    with open(branch_path, "r") as file:
        commit_hash = file.read().strip()

    if not commit_hash:
        print("No commits found.")
        return

    commit_path = os.path.join(
        repo_path, "objects", commit_hash
    )

    if not os.path.isfile(commit_path):
        print("Commit object not found.")
        return

    with open(commit_path, "r") as file:
        commit_data = json.load(file)

    tree = commit_data.get("tree", {})

    if file_path not in tree:
        print("File not found in the latest commit.")
        return

    file_hash = tree[file_path]

    object_path = os.path.join(
        repo_path, "objects", file_hash
    )

    if not os.path.isfile(object_path):
        print("File object not found.")
        return

    with open(object_path, "rb") as file:
        content = file.read()

    calculated_hash = hashlib.sha1(content).hexdigest()

    if calculated_hash != file_hash:
        print("File object is corrupted.")
        return

    parent_directory = os.path.dirname(file_path)

    if parent_directory:
        os.makedirs(parent_directory, exist_ok=True)

    with open(file_path, "wb") as file:
        file.write(content)

    print("Restored:", file_path)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python3 restore.py <file_path>")
    else:
        try:
            restore(sys.argv[1])
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            print("Restore error:", error)
