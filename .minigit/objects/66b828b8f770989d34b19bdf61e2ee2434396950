import os
import sys
import json
import difflib

def read_object(repo_path, file_hash):

    object_path = os.path.join(repo_path, "objects", file_hash)

    with open(object_path, "rb") as object_file:
        data = object_file.read()

    return data.decode("utf-8", errors="replace")


def diff(cached=False):

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
    branch_path = os.path.join(repo_path, branch_ref)

    head_tree = {}

    if os.path.isfile(branch_path):
        with open(branch_path, "r") as branch_file:
            commit_hash = branch_file.read().strip()

        if commit_hash:
            commit_path = os.path.join(
                repo_path, "objects", commit_hash
            )

            if not os.path.isfile(commit_path):
                print("Commit object not found.")
                return

            with open(commit_path, "r") as commit_file:
                commit_data = json.load(commit_file)

            head_tree = commit_data["tree"]

    found_difference = False

    for file_path, staged_hash in index.items():

        staged_content = read_object(repo_path, staged_hash)

        if cached:
            old_hash = head_tree.get(file_path)

            if old_hash is None:
                old_content = ""
            else:
                old_content = read_object(repo_path, old_hash)

            new_content = staged_content

        else:
            if not os.path.isfile(file_path):
                old_content = staged_content
                new_content = ""
            else:
                with open(file_path, "r", encoding="utf-8",
                          errors="replace") as file:
                    new_content = file.read()
                old_content = staged_content
   
        changes = list(difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile="a/" + file_path,
            tofile="b/" + file_path
        ))
        if changes:
            found_difference = True

            print("diff --", file_path)

            for line in changes:
                print(line, end="")
            print()
    if not found_difference:
        print("No differences found.")

if __name__ == "__main__":

    if len(sys.argv) == 1:
        diff()

    elif len(sys.argv) == 2 and sys.argv[1] == "--cached":
        diff(cached=True)

    else:
        print("Usage:")
        print("python3 diff.py")
        print("python3 diff.py --cached")
