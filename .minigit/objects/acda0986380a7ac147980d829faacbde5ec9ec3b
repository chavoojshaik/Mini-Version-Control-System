import os
import sys
import json
import hashlib

def get_file_hash(file_path):
    with open(file_path, "rb") as file:
        data = file.read()
    return hashlib.sha1(data).hexdigest()

def collect_files(directory):
    files_to_add = []
    for root, dirs, files in os.walk(directory):

        # Ignore internal directories
        dirs[:] = [
            d for d in dirs
            if d not in [".minigit", ".git", "__pycache__"]
        ]
        for filename in files:

            full_path = os.path.normpath(
                os.path.join(root, filename)
            )
            files_to_add.append(full_path)
    return files_to_add

def add(paths):
    repo_path = ".minigit"
    if not os.path.isdir(repo_path):
        print("MiniGit repository not found.")
        return

    index_path = os.path.join(repo_path, "index")

    with open(index_path, "r") as file:
        index = json.load(file)

    files_to_add = []
    stage_all = False

    for path in paths:

        path = os.path.normpath(path)

        if path == ".":

            stage_all = True
            files_to_add.extend(collect_files("."))

        elif (
            path == ".minigit"
            or path.startswith(".minigit" + os.sep)
            or path == ".git"
            or path.startswith(".git" + os.sep)
        ):

            print("Cannot stage repository metadata:", path)
            continue

        elif os.path.isfile(path):
            files_to_add.append(path)

        elif os.path.isdir(path):
            files_to_add.extend(collect_files(path))
        else:
            print("File or directory does not exist:", path)

    files_to_add = sorted(set(files_to_add))

    for file_path in files_to_add:

        file_hash = get_file_hash(file_path)

        object_path = os.path.join(
            repo_path, "objects", file_hash
        )

        if not os.path.exists(object_path):

            with open(file_path, "rb") as source:
                data = source.read()
            with open(object_path, "wb") as destination:
                destination.write(data)

        index[file_path] = file_hash

        print("Staged:", file_path)

    if stage_all:

        for tracked_file in list(index.keys()):

            if not os.path.exists(tracked_file):

                del index[tracked_file]

                print("Staged deletion:", tracked_file)

    with open(index_path, "w") as file:
        json.dump(index, file, indent=4)

    print("Add operation completed.")

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python3 add.py .")
        print("python3 add.py <file1> <file2> ...")
        print("python3 add.py <folder>")

    else:
        add(sys.argv[1:])
