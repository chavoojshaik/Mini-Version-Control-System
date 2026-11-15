
import os
import sys
import json
import hashlib
import time


def commit(message, second_parent=None):

    repo_path = ".minigit"

    # Check repository
    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return None

    # Read index
    index_path = os.path.join(repo_path, "index")

    try:
        with open(index_path, "r") as file:
            index = json.load(file)

    except (OSError, ValueError):
        print("Cannot read index.")
        return None

    if not isinstance(index, dict):
        print("Invalid index format.")
        return None

    # Read HEAD to identify the active branch
    head_path = os.path.join(repo_path, "HEAD")

    try:
        with open(head_path, "r") as file:
            head_content = file.read().strip()

    except OSError:
        print("Cannot read HEAD.")
        return None

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return None

    branch_ref = head_content[5:]

    # Validate branch reference
    if (
        not branch_ref.startswith("refs/heads/")
        or "/" in branch_ref[len("refs/heads/"):]
        or "\\" in branch_ref
        or not branch_ref[len("refs/heads/"):]
    ):
        print("Invalid branch reference.")
        return None

    branch_path = os.path.join(repo_path, branch_ref)

    # Get previous commit from the active branch
    parent = None

    if os.path.isfile(branch_path):

        try:
            with open(branch_path, "r") as file:
                parent = file.read().strip() or None

        except OSError:
            print("Cannot read parent commit.")
            return None

    # Read previous commit tree
    previous_tree = {}

    if parent:

        if (
            len(parent) != 40
            or any(c not in "0123456789abcdef" for c in parent)
        ):
            print("Invalid parent commit hash.")
            return None

        parent_path = os.path.join(
            repo_path, "objects", parent
        )

        try:
            with open(parent_path, "r") as file:
                parent_data = json.load(file)

        except (OSError, ValueError):
            print("Parent commit not found or invalid.")
            return None

        previous_tree = parent_data.get("tree", {})

        if not isinstance(previous_tree, dict):
            print("Invalid parent commit tree.")
            return None

    # Validate staged file hashes
    for file_path, file_hash in index.items():

        if (
            not isinstance(file_path, str)
            or not isinstance(file_hash, str)
            or len(file_hash) != 40
            or any(c not in "0123456789abcdef" for c in file_hash)
        ):
            print("Invalid staged file entry:", file_path)
            return None

    # Check whether there are changes
    if index == previous_tree and not second_parent:
        print("Nothing to commit.")
        return None

    # Validate second parent for merge commits
    if second_parent:

        if (
            len(second_parent) != 40
            or any(c not in "0123456789abcdef" for c in second_parent)
        ):
            print("Invalid second parent hash.")
            return None

        second_parent_path = os.path.join(
            repo_path, "objects", second_parent
        )

        if not os.path.isfile(second_parent_path):
            print("Second parent commit not found.")
            return None

    # Create commit data
    commit_data = {
        "tree": index.copy(),
        "parent": parent,
        "second_parent": second_parent,
        "message": message,
        "timestamp": int(time.time())
    }

    # Convert commit data into bytes
    commit_bytes = json.dumps(
        commit_data,
        sort_keys=True
    ).encode("utf-8")

    # Generate commit hash
    commit_hash = hashlib.sha1(
        commit_bytes
    ).hexdigest()

    # Store commit object
    object_path = os.path.join(
        repo_path, "objects", commit_hash
    )

    try:
        with open(object_path, "wb") as file:
            file.write(commit_bytes)

        # Ensure branch directory exists
        os.makedirs(
            os.path.dirname(branch_path),
            exist_ok=True
        )

        # Update the currently active branch
        with open(branch_path, "w") as file:
            file.write(commit_hash)

    except OSError as error:
        print("Commit failed:", error)
        return None

    # Display commit details
    print("Committed successfully!")
    print("Branch:", branch_ref[len("refs/heads/"):])
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
