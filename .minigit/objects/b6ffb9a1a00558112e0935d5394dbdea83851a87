import os
import sys
import json
import hashlib
import time

def commit (message):
    repo_path = ".minigit"
    if not os.path.isdir(repo_path):
       print("MiniGit repository not found")
       return

    index_path= os.path.join(repo_path,"index")
     
    with open (index_path, "r")as index_file:
        index=json.load(index_file)
    if not index:
       print ("Nothing to commit.")
       return
    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as head_file:
        head_content = head_file.read().strip()
    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return
    branch_ref = head_content[5:]
    branch_path = os.path.join(repo_path, branch_ref)
    parent = None
    if os.path.isfile(branch_path):
        with open(branch_path, "r") as branch_file:
            parent = branch_file.read().strip() or None
    commit_data = {
        "tree": index.copy(),
        "parent": parent,
        "message": message,
        "timestamp": int(time.time())
    }
    commit_bytes = json.dumps(
        commit_data,
        sort_keys=True
    ).encode("utf-8")
    commit_hash = hashlib.sha1(commit_bytes).hexdigest()
    object_path = os.path.join(
        repo_path, "objects", commit_hash
    )
    with open(object_path, "wb") as object_file:
        object_file.write(commit_bytes)
    os.makedirs(os.path.dirname(branch_path), exist_ok=True)
    with open(branch_path, "w") as branch_file:
        branch_file.write(commit_hash)
    print("Committed successfully!")
    print("Commit:", commit_hash)
    print("Message:", message)

if __name__ == "__main__":

    if len(sys.argv) < 3 or sys.argv[1] != "-m":
        print('Usage: python3 commit.py -m "commit message"')

    else:
        message = " ".join(sys.argv[2:])
        commit(message)

