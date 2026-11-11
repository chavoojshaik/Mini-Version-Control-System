import os
import json
import sys
import hashlib
import time

def read_commit(repo_path, commit_hash):

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
    stack = [(commit_hash, 0)]

    while stack:

        current_hash, distance = stack.pop()

        if current_hash in ancestors:
            continue

        ancestors[current_hash] = distance
        commit_data = read_commit(repo_path, current_hash)
        if commit_data is None:
            continue

        parent = commit_data.get("parent")
        second_parent = commit_data.get("second_parent")

        if parent:
            stack.append((parent, distance + 1))

        if second_parent:
            stack.append((second_parent, distance + 1))
    return ancestors

def find_common_ancestor(repo_path, current_hash, target_hash):
    current_ancestors = get_ancestors(repo_path, current_hash)
    target_ancestors = get_ancestors(repo_path, target_hash)
    common = set(current_ancestors) & set(target_ancestors)
    if not common:
        return None

    return min(
        common,
        key=lambda commit: (
            current_ancestors[commit] + target_ancestors[commit]
        )
    )
