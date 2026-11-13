import os
import sys
import json
import shutil

def checkout(branch_name):

    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    branch_path = os.path.join(
        repo_path, "refs", "heads", branch_name
    )

    if not os.path.isfile(branch_path):
        print("Branch does not exist.")
        return

    with open(branch_path, "r") as file:
        commit_hash = file.read().strip()

    if not commit_hash:
        print("Branch has no commits yet.")
        return

    commit_path = os.path.join(
        repo_path, "objects", commit_hash
    )

    if not os.path.isfile(commit_path):
        print("Commit object not found.")
        return

    with open(commit_path, "r") as file:
        commit_data = json.load(file)

    target_tree = commit_data["tree"]

    index_path = os.path.join(repo_path, "index")

    with open(index_path, "r") as file:
        current_index = json.load(file)
        
    for file_path, old_hash in current_index.items():

        if not os.path.isfile(file_path):
            continue

        with open(file_path, "rb") as file:
            current_data = file.read()

        import hashlib
        current_hash = hashlib.sha1(current_data).hexdigest()

        if current_hash != old_hash:
            print("Uncommitted changes found.")
            print("Please commit or save your changes first.")
            return

    for file_path, file_hash in target_tree.items():

        object_path = os.path.join(
            repo_path, "objects", file_hash
        )

        if not os.path.isfile(object_path):
            print("File object not found:", file_path)
            return

    for file_path, file_hash in target_tree.items():

        object_path = os.path.join(
            repo_path, "objects", file_hash
        )

        parent_dir = os.path.dirname(file_path)

        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(object_path, "rb") as source:
            data = source.read()

        with open(file_path, "wb") as destination:
            destination.write(data)

    with open(index_path, "w") as file:
        json.dump(target_tree, file, indent=4)

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "w") as file:
        file.write("ref: refs/heads/" + branch_name + "\n")
    print("Switched to branch '" + branch_name + "'")

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python3 checkout.py <branch_name>")
    else:
        checkout(sys.argv[1])
