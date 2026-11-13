import os
import sys
import json
import hashlib
import shutil

def get_file_hash(file_path):
    with open(file_path, "rb") as file:
        data = file.read()

    return hashlib.sha1(data).hexdigest()

def get_commit_tree(repo_path, commit_hash):

    if not commit_hash:
        return {}

    commit_path = os.path.join(
        repo_path, "objects", commit_hash
    )

    if not os.path.isfile(commit_path):
        raise FileNotFoundError("Commit object not found.")

    with open(commit_path, "r") as file:
        commit_data = json.load(file)

    tree = commit_data["tree"]

    if not isinstance(tree, dict):
        raise ValueError("Invalid commit tree.")

    return tree

def is_safe_path(file_path):

    if not isinstance(file_path, str) or not file_path:
        return False

    if os.path.isabs(file_path):
        return False

    normalized_path = os.path.normpath(file_path)

    if normalized_path in [".", ".."]:
        return False

    if normalized_path.startswith(".." + os.sep):
        return False

    if normalized_path == ".minigit":
        return False

    if normalized_path.startswith(".minigit" + os.sep):
        return False

    if normalized_path == ".git":
        return False

    if normalized_path.startswith(".git" + os.sep):
        return False

    return True

def checkout(branch_name):

    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    if (
        not branch_name
        or branch_name in [".", ".."]
        or "/" in branch_name
        or "\\" in branch_name
        or branch_name.startswith("-")
        or branch_name.strip() != branch_name
    ):
        print("Invalid branch name.")
        return

    branch_path = os.path.join(
        repo_path, "refs", "heads", branch_name
    )

    if not os.path.isfile(branch_path):
        print("Branch does not exist.")
        return

    with open(branch_path, "r") as file:
        target_commit = file.read().strip()

    try:
        target_tree = get_commit_tree(
            repo_path, target_commit
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Cannot read target branch:", error)
        return

    for file_path, file_hash in target_tree.items():

        if not is_safe_path(file_path):
            print("Unsafe file path:", file_path)
            return

        if not isinstance(file_hash, str) or len(file_hash) != 40:
            print("Invalid file hash:", file_path)
            return

        object_path = os.path.join(
            repo_path, "objects", file_hash
        )

        if not os.path.isfile(object_path):
            print("File object not found:", file_path)
            return

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as file:
        head_content = file.read().strip()

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return

    current_ref = head_content[5:]

    if (
        current_ref != "refs/heads/" + os.path.basename(current_ref)
        or current_ref.startswith("/")
        or "\\" in current_ref
    ):
        print("Invalid HEAD reference.")
        return

    current_branch = os.path.basename(current_ref)

    if current_branch == branch_name:
        print("Already on branch '" + branch_name + "'")
        return

    current_branch_path = os.path.join(
        repo_path, current_ref
    )

    current_commit = ""

    if os.path.isfile(current_branch_path):
        with open(current_branch_path, "r") as file:
            current_commit = file.read().strip()

    try:
        current_tree = get_commit_tree(
            repo_path, current_commit
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Cannot read current branch:", error)
        return

    for file_path in current_tree:

        if not is_safe_path(file_path):
            print("Unsafe current file path:", file_path)
            return

    index_path = os.path.join(repo_path, "index")

    try:
        with open(index_path, "r") as file:
            current_index = json.load(file)
    except (OSError, ValueError, json.JSONDecodeError):
        print("Cannot read index.")
        return

    if current_index != current_tree:
        print("Staged changes found.")
        print("Commit or discard your changes before switching.")
        return

    for file_path, old_hash in current_tree.items():

        if not os.path.isfile(file_path):
            print("Uncommitted changes found:", file_path)
            return

        if get_file_hash(file_path) != old_hash:
            print("Uncommitted changes found:", file_path)
            return

    for file_path in target_tree:

        if (
            os.path.exists(file_path)
            and file_path not in current_tree
        ):
            print("Untracked file would be overwritten:", file_path)
            return

    for file_path in target_tree:

        parent = os.path.dirname(file_path)

        while parent:
            if os.path.isfile(parent):
                print("Directory conflict:", parent)
                return

            parent = os.path.dirname(parent)

        if os.path.isdir(file_path):
            print("File conflicts with existing directory:", file_path)
            return

    target_files = {}

    try:
        for file_path, file_hash in target_tree.items():

            object_path = os.path.join(
                repo_path, "objects", file_hash
            )

            with open(object_path, "rb") as source:
                target_files[file_path] = source.read()

    except OSError as error:
        print("Cannot read target files:", error)
        return

    backup_files = {}

    try:
        for file_path in current_tree:

            with open(file_path, "rb") as source:
                backup_files[file_path] = source.read()

    except OSError as error:
        print("Cannot back up current files:", error)
        return

    try:

        for file_path in current_tree:

            if file_path not in target_tree:

                if os.path.isfile(file_path):
                    os.remove(file_path)

        for file_path, data in target_files.items():

            parent_dir = os.path.dirname(file_path)

            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(file_path, "wb") as destination:
                destination.write(data)

        with open(index_path, "w") as file:
            json.dump(target_tree, file, indent=4)

        with open(head_path, "w") as file:
            file.write(
                "ref: refs/heads/" + branch_name + "\n"
            )

    except OSError as error:

        print("Switch failed:", error)
        print("Attempting to restore previous files.")

        for file_path in target_tree:

            if file_path not in current_tree:
                if os.path.isfile(file_path):
                    os.remove(file_path)

        for file_path, data in backup_files.items():

            parent_dir = os.path.dirname(file_path)

            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(file_path, "wb") as destination:
                destination.write(data)
        with open(index_path, "w") as file:
            json.dump(current_tree, file, indent=4)
        with open(head_path, "w") as file:
            file.write(head_content + "\n")
        return
    print("Switched to branch '" + branch_name + "'")

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python3 switch.py <branch_name>")
    else:
        checkout(sys.argv[1])
