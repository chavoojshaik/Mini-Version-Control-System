import os
import json
from datetime import datetime

def log():

    repo_path = ".minigit"
    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    head_path = os.path.join(repo_path, "HEAD")
    with open(head_path, "r") as head_file:
        head_content = head_file.read().strip()
    branch_ref = head_content[5:]
    branch_path = os.path.join(repo_path, branch_ref)

    if not os.path.isfile(branch_path):
        print("No commits yet.")
        return

    with open(branch_path, "r") as branch_file:
        current_hash = branch_file.read().strip()

    while current_hash:

        object_path = os.path.join(
            repo_path, "objects", current_hash
        )

        if not os.path.isfile(object_path):
            print("Commit object not found:", current_hash)
            return

        with open(object_path, "r") as object_file:
            commit_data = json.load(object_file)

        commit_time = datetime.fromtimestamp(
            commit_data["timestamp"]
        )
        print("commit", current_hash)
        print("Date:", commit_time)
        print()
        print("    " + commit_data["message"])
        print()
        current_hash = commit_data["parent"]

if __name__ == "__main__":
    log()
