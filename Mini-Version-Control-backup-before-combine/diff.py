
import os
import json
import difflib


class Diff:

    def show_diff(self, filename):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        if not os.path.isfile(filename):
            print("Error: File does not exist!")
            return

        # Read current branch
        with open(".mvc/HEAD", "r") as file:
            branch_name = file.read().strip()

        branch_file = ".mvc/branches/" + branch_name

        with open(branch_file, "r") as file:
            commit_id = file.read().strip()

        if not commit_id:
            print("No commits available!")
            return

        # Read latest commit
        commit_path = ".mvc/commits/" + commit_id + ".json"

        with open(commit_path, "r") as file:
            commit_data = json.load(file)

        committed_files = commit_data["files"]

        if filename not in committed_files:
            print("File is not tracked in the latest commit!")
            return

        # Read old committed version
        file_hash = committed_files[filename]
        object_path = ".mvc/objects/" + file_hash

        with open(object_path, "r", errors="replace") as file:
            old_content = file.readlines()

        # Read current version
        with open(filename, "r", errors="replace") as file:
            new_content = file.readlines()

        # Generate difference
        differences = difflib.unified_diff(
            old_content,
            new_content,
            fromfile="Committed Version",
            tofile="Current Version"
        )

        result = list(differences)

        if not result:
            print("No changes found!")
        else:
            print("".join(result))
