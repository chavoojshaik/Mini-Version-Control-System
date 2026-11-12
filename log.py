import os
import json
import heapq
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def log():

    repo_path = ".minigit"

    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    ist = ZoneInfo("Asia/Kolkata")

    head_path = os.path.join(repo_path, "HEAD")

    with open(head_path, "r") as file:
        head_content = file.read().strip()

    if not head_content.startswith("ref: "):
        print("Invalid HEAD reference.")
        return

    branch_ref = head_content[5:]
    branch_path = os.path.join(repo_path, branch_ref)

    if not os.path.isfile(branch_path):
        print("No commits yet.")
        return

    with open(branch_path, "r") as file:
        start_hash = file.read().strip()

    if not start_hash:
        print("No commits yet.")
        return

    heap = []
    visited = set()

    def add_commit(commit_hash):

        if not commit_hash or commit_hash in visited:
            return

        object_path = os.path.join(
            repo_path, "objects", commit_hash
        )

        if not os.path.isfile(object_path):
            print("Commit object not found:", commit_hash)
            return

        with open(object_path, "r") as file:
            commit_data = json.load(file)

        timestamp = commit_data.get("timestamp", 0)

        heapq.heappush(
            heap,
            (-timestamp, commit_hash, commit_data)
        )

        visited.add(commit_hash)

    add_commit(start_hash)

    while heap:

        _, commit_hash, commit_data = heapq.heappop(heap)

        parent = commit_data.get("parent")
        second_parent = commit_data.get("second_parent")

        print("commit", commit_hash)

        if second_parent:
            print(
                "Merge:",
                parent[:7] if parent else "None",
                second_parent[:7]
            )

        print("Author: MiniGit User")

        timestamp = commit_data.get("timestamp", 0)

        commit_time = datetime.fromtimestamp(
            timestamp, tz=timezone.utc
        ).astimezone(ist)

        print(
            "Date:  ",
            commit_time.strftime("%a %b %d %H:%M:%S %Y")
        )

        print()
        print("    " + commit_data.get("message", ""))
        print()

        add_commit(parent)
        add_commit(second_parent)


if __name__ == "__main__":
    log()
