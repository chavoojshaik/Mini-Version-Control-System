import os
import sys
import json
import hashlib
import time

def commit(message, second_parent=None):
    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return None

    index_path = os.path.join(repo_path, "index")

    try:
        with open(index_path, "r") as file:
            index = json.load(file)
    except (OSError, ValueError):
        print("Cannot read index.")
        return None

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as file:
        head_content = file.read().strip()

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return None

    branch_ref = head_content[5:]

    if (
        not branch_ref.startswith("refs/heads/")
        or ".." in branch_ref.split("/")
        or "\\" in branch_ref
    ):
        print("Invalid branch reference.")
        return None

    branch_path = os.path.join(repo_path, branch_ref)

    parent = None

    if os.path.isfile(branch_path):
        with open(branch_path, "r") as file:
            parent = file.read().strip() or None

    previous_tree = {}

    if parent:

        parent_path = os.path.join(
            repo_path, "objects", parent
        )

        if not os.path.isfile(parent_path):
            print("Parent commit not found.")
            return None

        with open(parent_path, "r") as file:
            parent_data = json.load(file)

        previous_tree = parent_data.get("tree", {})

    if index == previous_tree and not second_parent:
        print("Nothing to commit.")
        return None

    commit_data = {
        "tree": index.copy(),
        "parent": parent,
        "second_parent": second_parent,
        "message": message,
        "timestamp": int(time.time())
    }

    commit_bytes = json.dumps(
        commit_data,
        sort_keys=True
    ).encode("utf-8")

    commit_hash = hashlib.sha1(
        commit_bytes
    ).hexdigest()

    object_path = os.path.join(
        repo_path, "objects", commit_hash
    )
    with open(object_path, "wb") as file:
        file.write(commit_bytes)
    os.makedirs(
        os.path.dirname(branch_path),
        exist_ok=True
    )
    with open(branch_path, "w") as file:
        file.write(commit_hash)
    print("Committed successfully!")
    print("Commit:", commit_hash)
    print("Message:", message)

    if second_parent:
        print("Second parent:", second_parent)

    return commit_hash


if __name__ == "__main__":

    if len(sys.argv) < 3 or sys.argv[1] != "-m":
        print('Usage: python3 commit.py -m "commit message"')

    else:
        message = " ".join(sys.argv[2:])
        commit(message)
