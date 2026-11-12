import os
import sys
import json
import hashlib
from collections import deque
from commit import commit as create_commit

def read_commit(repo_path, commit_hash):

    if not commit_hash:
        return None

    object_path = os.path.join(
        repo_path, "objects", commit_hash
    )

    if not os.path.isfile(object_path):
        return None

    with open(object_path, "r") as file:
        return json.load(file)


def get_branch_head(repo_path, branch_name):

    branch_path = os.path.join(
        repo_path, "refs", "heads", branch_name
    )

    if not os.path.isfile(branch_path):
        return None

    with open(branch_path, "r") as file:
        return file.read().strip() or None


def get_ancestors(repo_path, commit_hash):

    ancestors = {}
    queue = deque([(commit_hash, 0)])

    while queue:

        current_hash, distance = queue.popleft()

        if current_hash in ancestors:
            continue

        ancestors[current_hash] = distance

        commit_data = read_commit(
            repo_path, current_hash
        )

        if commit_data is None:
            continue

        parent = commit_data.get("parent")
        second_parent = commit_data.get("second_parent")

        if parent:
            queue.append((parent, distance + 1))

        if second_parent:
            queue.append((second_parent, distance + 1))

    return ancestors


def find_common_ancestor(
    repo_path, current_hash, target_hash
):

    current_ancestors = get_ancestors(
        repo_path, current_hash
    )

    target_ancestors = get_ancestors(
        repo_path, target_hash
    )

    common = set(current_ancestors) & set(target_ancestors)

    if not common:
        return None

    return min(
        common,
        key=lambda commit_hash: (
            current_ancestors[commit_hash]
            + target_ancestors[commit_hash]
        )
    )


def get_tree(repo_path, commit_hash):

    commit_data = read_commit(
        repo_path, commit_hash
    )

    if commit_data is None:
        raise ValueError("Commit object not found.")

    tree = commit_data.get("tree")

    if not isinstance(tree, dict):
        raise ValueError("Invalid commit tree.")

    return tree


def is_safe_path(file_path):

    if not isinstance(file_path, str) or not file_path:
        return False

    if os.path.isabs(file_path) or "\\" in file_path:
        return False

    parts = file_path.split("/")

    if any(part in ["", ".", ".."] for part in parts):
        return False

    if parts[0] in [".minigit", ".git"]:
        return False

    return True


def get_file_hash(file_path):

    with open(file_path, "rb") as file:
        data = file.read()

    return hashlib.sha1(data).hexdigest()


def merge(branch_name):

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

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as file:
        head_content = file.read().strip()

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return

    current_ref = head_content[5:]

    if (
        not current_ref.startswith("refs/heads/")
        or "\\" in current_ref
    ):
        print("Invalid HEAD reference.")
        return

    current_branch = current_ref[len("refs/heads/"):]

    if (
        not current_branch
        or "/" in current_branch
        or current_branch in [".", ".."]
    ):
        print("Invalid HEAD reference.")
        return

    if current_branch == branch_name:
        print("Cannot merge a branch into itself.")
        return

    current_hash = get_branch_head(
        repo_path, current_branch
    )

    target_hash = get_branch_head(
        repo_path, branch_name
    )

    if target_hash is None:
        print("Target branch does not exist or has no commits.")
        return

    if current_hash is None:
        print("Current branch has no commits.")
        return

    if current_hash == target_hash:
        print("Already up to date.")
        return

    try:

        current_tree = get_tree(
            repo_path, current_hash
        )

        target_tree = get_tree(
            repo_path, target_hash
        )

        base_hash = find_common_ancestor(
            repo_path, current_hash, target_hash
        )

        if base_hash is None:
            print("No common ancestor found.")
            return

        base_tree = get_tree(
            repo_path, base_hash
        )

    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:

        print("Cannot read commit history:", error)
        return

    for tree in [base_tree, current_tree, target_tree]:

        for file_path in tree:

            if not is_safe_path(file_path):
                print("Unsafe file path:", file_path)
                return

    index_path = os.path.join(repo_path, "index")

    try:

        with open(index_path, "r") as file:
            current_index = json.load(file)

    except (OSError, ValueError, json.JSONDecodeError):

        print("Cannot read index.")
        return

    if current_index != current_tree:
        print("Staged changes found. Commit before merging.")
        return

    for file_path, old_hash in current_tree.items():

        if not os.path.isfile(file_path):
            print("Uncommitted changes found:", file_path)
            return

        if get_file_hash(file_path) != old_hash:
            print("Uncommitted changes found:", file_path)
            return

    merged_tree = {}
    conflicts = []
    missing = object()

    all_paths = (
        set(base_tree)
        | set(current_tree)
        | set(target_tree)
    )

    for file_path in sorted(all_paths):

        base = base_tree.get(file_path, missing)
        ours = current_tree.get(file_path, missing)
        theirs = target_tree.get(file_path, missing)

        if ours == theirs:
            result = ours

        elif ours == base:
            result = theirs

        elif theirs == base:
            result = ours

        else:
            conflicts.append(file_path)
            continue

        if result is not missing:
            merged_tree[file_path] = result

    if conflicts:

        print("Merge conflicts detected:")

        for file_path in conflicts:
            print("  ", file_path)

        print("Resolve conflicts before merging.")
        return

    for file_path, file_hash in merged_tree.items():

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

    for file_path in merged_tree:

        if (
            os.path.lexists(file_path)
            and file_path not in current_tree
        ):
            print("Untracked file would be overwritten:", file_path)
            return

    for file_path in merged_tree:

        parent = os.path.dirname(file_path)

        while parent:

            if os.path.isfile(parent):
                print("Directory conflict:", parent)
                return

            parent = os.path.dirname(parent)

        if os.path.isdir(file_path):
            print("File conflicts with directory:", file_path)
            return

    merged_files = {}

    try:

        for file_path, file_hash in merged_tree.items():

            object_path = os.path.join(
                repo_path, "objects", file_hash
            )

            with open(object_path, "rb") as file:
                merged_files[file_path] = file.read()

    except OSError as error:

        print("Cannot read merged files:", error)
        return

    backup_files = {}

    try:
        for file_path in current_tree:

            with open(file_path, "rb") as file:
                backup_files[file_path] = file.read()

    except OSError as error:

        print("Cannot back up current files:", error)
        return

    def rollback():

        for file_path in current_tree:

            if file_path not in merged_tree:

                if os.path.isfile(file_path):
                    os.remove(file_path)

        for file_path, data in backup_files.items():

            parent = os.path.dirname(file_path)

            if parent:
                os.makedirs(parent, exist_ok=True)

            with open(file_path, "wb") as file:
                file.write(data)

        with open(index_path, "w") as file:
            json.dump(current_tree, file, indent=4)

    try:

        for file_path in current_tree:

            if file_path not in merged_tree:

                if os.path.isfile(file_path):
                    os.remove(file_path)

        for file_path, data in merged_files.items():

            parent = os.path.dirname(file_path)

            if parent:
                os.makedirs(parent, exist_ok=True)

            with open(file_path, "wb") as file:
                file.write(data)

        with open(index_path, "w") as file:
            json.dump(merged_tree, file, indent=4)

    except OSError as error:

        print("Merge failed:", error)

        try:
            rollback()
        except OSError:
            print("Warning: rollback was incomplete.")

        return

    try:

        result = create_commit(
            "Merge branch " + branch_name,
            second_parent=target_hash
        )

        if not result:
            print("Merge commit failed.")
            rollback()
            return

    except (OSError, ValueError, KeyError) as error:

        print("Merge commit failed:", error)

        try:
            rollback()
        except OSError:
            print("Warning: rollback was incomplete.")

        return

    print("Merge completed successfully!")
    print("Merged branch:", branch_name)
    print("Merge base:", base_hash)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python3 merge.py <branch_name>")

    else:
        merge(sys.argv[1])
