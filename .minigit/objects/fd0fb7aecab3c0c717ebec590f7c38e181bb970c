
import os
import sys
import json
import hashlib


def get_file_hash(file_path):
    with open(file_path, "rb") as file:
        return hashlib.sha1(file.read()).hexdigest()


def is_safe_path(file_path):

    if not isinstance(file_path, str) or not file_path:
        return False

    if "\0" in file_path or "\\" in file_path:
        return False

    if os.path.isabs(file_path):
        return False

    normalized = os.path.normpath(file_path)

    if normalized in [".", ".."]:
        return False

    if normalized.startswith(".." + os.sep):
        return False

    first_part = normalized.split(os.sep)[0]

    if first_part in [".minigit", ".git"]:
        return False

    return True


def get_commit_tree(repo_path, commit_hash):

    if not commit_hash:
        return {}

    if (
        len(commit_hash) != 40
        or any(c not in "0123456789abcdef" for c in commit_hash)
    ):
        raise ValueError("Invalid commit hash.")

    commit_path = os.path.join(
        repo_path, "objects", commit_hash
    )

    if not os.path.isfile(commit_path):
        raise FileNotFoundError("Commit object not found.")

    with open(commit_path, "r") as file:
        commit_data = json.load(file)

    tree = commit_data.get("tree")

    if not isinstance(tree, dict):
        raise ValueError("Invalid commit tree.")

    return tree


def checkout(branch_name):

    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    # Validate branch name
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

    try:
        with open(branch_path, "r") as file:
            target_commit = file.read().strip()

        if not target_commit:
            print("Branch has no commits yet.")
            return

        target_tree = get_commit_tree(
            repo_path, target_commit
        )

    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Cannot read target branch:", error)
        return

    # Validate target tree and blob objects
    for file_path, file_hash in target_tree.items():

        if not is_safe_path(file_path):
            print("Unsafe file path:", file_path)
            return

        if (
            not isinstance(file_hash, str)
            or len(file_hash) != 40
            or any(c not in "0123456789abcdef" for c in file_hash)
        ):
            print("Invalid file hash:", file_path)
            return

        object_path = os.path.join(
            repo_path, "objects", file_hash
        )

        if not os.path.isfile(object_path):
            print("File object not found:", file_path)
            return

    # Read HEAD
    head_path = os.path.join(repo_path, "HEAD")

    try:
        with open(head_path, "r") as file:
            head_content = file.read().strip()

    except OSError:
        print("Cannot read HEAD.")
        return

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return

    current_ref = head_content[5:]

    if (
        not current_ref.startswith("refs/heads/")
        or "/" in current_ref[len("refs/heads/"):]
        or "\\" in current_ref
    ):
        print("Invalid HEAD reference.")
        return

    current_branch = current_ref[len("refs/heads/"):]

    if current_branch == branch_name:
        print("Already on branch '" + branch_name + "'")
        return

    current_branch_path = os.path.join(
        repo_path, current_ref
    )

    if not os.path.isfile(current_branch_path):
        print("Current branch reference not found.")
        return

    try:
        with open(current_branch_path, "r") as file:
            current_commit = file.read().strip()

        current_tree = get_commit_tree(
            repo_path, current_commit
        )

    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Cannot read current branch:", error)
        return

    # Validate current tree paths
    for file_path in current_tree:

        if not is_safe_path(file_path):
            print("Unsafe current file path:", file_path)
            return

    # Read index
    index_path = os.path.join(repo_path, "index")

    try:
        with open(index_path, "r") as file:
            current_index = json.load(file)

    except (OSError, ValueError, json.JSONDecodeError):
        print("Cannot read index.")
        return

    if not isinstance(current_index, dict):
        print("Invalid index.")
        return

    if current_index != current_tree:
        print("Staged changes found.")
        print("Commit or discard your changes before switching.")
        return

    # Check working directory changes
    for file_path, old_hash in current_tree.items():

        if not os.path.isfile(file_path):
            print("Tracked file is missing:", file_path)
            return

        if get_file_hash(file_path) != old_hash:
            print("Uncommitted changes found:", file_path)
            return

    # Check untracked file conflicts
    for file_path in target_tree:

        if (
            os.path.lexists(file_path)
            and file_path not in current_tree
        ):
            print("Untracked file would be overwritten:", file_path)
            return

        if os.path.isdir(file_path):
            print("Directory conflicts with target file:", file_path)
            return

    # Check parent directory conflicts
    for file_path in target_tree:

        parent = os.path.dirname(file_path)

        while parent:

            if (
                os.path.isfile(parent)
                and parent not in current_tree
            ):
                print("Directory conflict:", parent)
                return

            parent = os.path.dirname(parent)

    # Read only new or modified target files
    target_files = {}

    try:
        for file_path, file_hash in target_tree.items():

            # Skip identical files
            if current_tree.get(file_path) == file_hash:
                continue

            object_path = os.path.join(
                repo_path, "objects", file_hash
            )

            with open(object_path, "rb") as file:
                data = file.read()

            # Verify blob integrity
            if hashlib.sha1(data).hexdigest() != file_hash:
                print("File object hash mismatch:", file_path)
                return

            target_files[file_path] = data

    except OSError as error:
        print("Cannot read target files:", error)
        return

    # Back up only files that will change or be removed
    backup_files = {}

    try:
        for file_path in current_tree:

            if (
                file_path not in target_tree
                or current_tree[file_path] != target_tree[file_path]
            ):
                with open(file_path, "rb") as file:
                    backup_files[file_path] = file.read()

    except OSError as error:
        print("Cannot back up current files:", error)
        return

    # Save old index
    try:
        with open(index_path, "r") as file:
            old_index_content = file.read()

    except OSError:
        print("Cannot save old index.")
        return

    try:

        # Remove files not present in target branch
        for file_path in current_tree:

            if file_path not in target_tree:
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Restore new and modified target files
        for file_path, data in target_files.items():

            parent_dir = os.path.dirname(file_path)

            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(file_path, "wb") as file:
                file.write(data)

        # Update index
        with open(index_path, "w") as file:
            json.dump(target_tree, file, indent=4)

        # Update HEAD
        with open(head_path, "w") as file:
            file.write(
                "ref: refs/heads/" + branch_name + "\n"
            )

    except OSError as error:

        print("Switch failed:", error)
        print("Restoring previous state.")

        # Remove newly created target files
        for file_path in target_tree:

            if file_path not in current_tree:
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Restore changed and removed files
        for file_path, data in backup_files.items():

            parent_dir = os.path.dirname(file_path)

            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(file_path, "wb") as file:
                file.write(data)

        # Restore index
        with open(index_path, "w") as file:
            file.write(old_index_content)

        # Restore HEAD
        with open(head_path, "w") as file:
            file.write(head_content + "\n")

        return

    print("Switched to branch '" + branch_name + "'")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python3 switch.py <branch_name>")

    else:
        checkout(sys.argv[1])
