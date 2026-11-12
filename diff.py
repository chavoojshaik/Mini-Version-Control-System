import os
import sys
import json
import difflib
import hashlib

def read_object(repo_path, file_hash):

    object_path = os.path.join(
        repo_path, "objects", file_hash
    )
    if not os.path.isfile(object_path):
        return None
    with open(object_path, "rb") as file:
        return file.read().decode("utf-8", errors="replace")

def get_file_content(file_path):

    if not os.path.isfile(file_path):
        return None

    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
        return file.read()

def get_commit_tree(repo_path):

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as file:
        head = file.read().strip()

    if not head.startswith("ref: "):
        return {}

    branch_path = os.path.join(repo_path, head[5:])

    if not os.path.isfile(branch_path):
        return {}

    with open(branch_path, "r") as file:
        commit_hash = file.read().strip()

    if not commit_hash:
        return {}
    commit_path = os.path.join(repo_path, "objects", commit_hash)

    with open(commit_path, "r") as file:
        commit_data = json.load(file)

    return commit_data["tree"]

def show_diff(file_path, old_content, new_content):

    if old_content == new_content:
        return

    old_lines = (
        old_content.splitlines(keepends=True)
        if old_content is not None else []
    )

    new_lines = (
        new_content.splitlines(keepends=True)
        if new_content is not None else []
    )
    old_hash = (
        hashlib.sha1(old_content.encode()).hexdigest()[:7]
        if old_content is not None else "0000000"
    )
    new_hash = (
        hashlib.sha1(new_content.encode()).hexdigest()[:7]
        if new_content is not None else "0000000"
    )
    print(f"diff --git a/{file_path} b/{file_path}")

    if old_content is None:
        print("new file mode 100644")

    elif new_content is None:
        print("deleted file mode 100644")

    print(f"index {old_hash}..{new_hash} 100644")

    old_name = (
        "/dev/null" if old_content is None
        else f"a/{file_path}"
    )

    new_name = (
        "/dev/null" if new_content is None
        else f"b/{file_path}"
    )
    print(f"--- {old_name}")
    print(f"+++ {new_name}")

    diff_lines = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="",
        tofile="",
        lineterm=""
    )

    for line in diff_lines:

        if line.startswith("---") or line.startswith("+++"):
            continue
        print(line)

def diff(cached=False):
    repo_path = ".minigit"
    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return
    index_path = os.path.join(repo_path, "index")

    with open(index_path, "r") as file:
        index = json.load(file)
    if cached:
        old_tree = get_commit_tree(repo_path)
        new_tree = index

    else:
        old_tree = index
        new_tree = {}

        for file_path in index:
            if os.path.isfile(file_path):

                data = get_file_content(file_path)

                new_tree[file_path] = hashlib.sha1(
                    data.encode()
                ).hexdigest()
    all_files = sorted(set(old_tree) | set(new_tree))

    for file_path in all_files:
        old_hash = old_tree.get(file_path)
        new_hash = new_tree.get(file_path)

        if old_hash == new_hash:
            continue
        old_content = (
            read_object(repo_path, old_hash)
            if old_hash else None
        )
        if cached:
            new_content = (
                read_object(repo_path, new_hash)
                if new_hash else None
            )
        else:
            new_content = get_file_content(file_path)
        show_diff(
            file_path,
            old_content,
            new_content
        )

if __name__ == "__main__":
    if len(sys.argv) == 1:
        diff()

    elif len(sys.argv) == 2 and sys.argv[1] == "--cached":
        diff(cached=True)

    else:
        print("Usage:")
        print("python3 diff.py")
        print("python3 diff.py --cached")
