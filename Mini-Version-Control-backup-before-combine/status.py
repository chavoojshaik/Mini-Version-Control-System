
import os
import json

from hashing import generate_hash


class Status:

    def __init__(self):
        self.staging_file = ".mvc/staging.json"

        # Directories that should not be scanned
        self.ignored_dirs = {
            ".mvc",
            ".git",
            "venv",
            "__pycache__",
            ".pytest_cache"
        }

    def show_status(self):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        with open(self.staging_file, "r") as file:
            staged_files = json.load(file)

        # Read current branch
        with open(".mvc/HEAD", "r") as file:
            branch_name = file.read().strip()

        branch_file = ".mvc/branches/" + branch_name

        with open(branch_file, "r") as file:
            commit_id = file.read().strip()

        committed_files = {}

        if commit_id:
            commit_path = (
                ".mvc/commits/" + commit_id + ".json"
            )

            with open(commit_path, "r") as file:
                commit_data = json.load(file)

            committed_files = commit_data["files"]

        modified = []
        untracked = []

        # Recursively scan all directories
        for root, dirs, files in os.walk("."):

            # Skip internal and unnecessary directories
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in self.ignored_dirs
            ]

            for filename in files:

                file_path = os.path.join(root, filename)

                # Convert path into relative format
                relative_path = os.path.relpath(
                    file_path, "."
                ).replace(os.sep, "/")

                # Ignore staged files
                if relative_path in staged_files:
                    continue

                # Check untracked files
                if relative_path not in committed_files:
                    untracked.append(relative_path)
                    continue

                # Read current file content
                with open(file_path, "rb") as file:
                    content = file.read()

                current_hash = generate_hash(content)

                # Check modified files
                if current_hash != committed_files[relative_path]:
                    modified.append(relative_path)

        print("\nOn branch:", branch_name)

        print("\nChanges to be committed:")
        for filename in staged_files:
            print("   ", filename)

        print("\nChanges not staged:")
        for filename in modified:
            print("   ", filename)

        print("\nUntracked files:")
        for filename in untracked:
            print("   ", filename)
