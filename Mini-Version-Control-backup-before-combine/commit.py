
import os
import json
import hashlib
from datetime import datetime

from hashing import generate_hash


class Commit:

    def __init__(self):
        self.staging_file = ".mvc/staging.json"
        self.objects_dir = ".mvc/objects"
        self.commits_dir = ".mvc/commits"

    def create_commit(self, message):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        with open(self.staging_file, "r") as file:
            staged_files = json.load(file)

        if not staged_files:
            print("Nothing to commit!")
            return

        # Read current branch name from HEAD
        with open(".mvc/HEAD", "r") as file:
            branch_name = file.read().strip()

        branch_file = ".mvc/branches/" + branch_name

        if not os.path.exists(branch_file):
            print("Error: Current branch does not exist!")
            return

        # Get parent commit ID
        with open(branch_file, "r") as file:
            parent_commit = file.read().strip()

        # Start with previous commit's complete snapshot
        files_data = {}

        if parent_commit:
            parent_path = (
                self.commits_dir + "/" + parent_commit + ".json"
            )

            with open(parent_path, "r") as file:
                parent_data = json.load(file)

            files_data = parent_data["files"].copy()


        # Add, update, or delete staged files
        for filename in staged_files:

            # If file does not exist, treat it as a deletion
            if not os.path.isfile(filename):

                if filename in files_data:
                    del files_data[filename]
                    print(f"File '{filename}' deleted from snapshot!")
                    continue

                print(f"Error: Staged file '{filename}' does not exist!")
                return

            # Read file content
            with open(filename, "rb") as file:
                content = file.read()

            file_hash = generate_hash(content)

            object_path = os.path.join(
                self.objects_dir, file_hash
            )

            if not os.path.exists(object_path):
                with open(object_path, "wb") as file:
                    file.write(content)

            files_data[filename] = file_hash

        # Prepare commit information
        commit_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "parent": parent_commit or None,
            "files": files_data
        }

        commit_content = json.dumps(
            commit_data, sort_keys=True
        ).encode()

        commit_id = hashlib.sha256(
            commit_content
        ).hexdigest()

        commit_path = os.path.join(
            self.commits_dir, commit_id + ".json"
        )

        with open(commit_path, "w") as file:
            json.dump(commit_data, file, indent=4)

        # Update current branch pointer
        with open(branch_file, "w") as file:
            file.write(commit_id)

        # Clear staging area
        with open(self.staging_file, "w") as file:
            json.dump([], file, indent=4)

        print("Commit created successfully!")
        print("Commit ID:", commit_id)
        print("Message:", message)
