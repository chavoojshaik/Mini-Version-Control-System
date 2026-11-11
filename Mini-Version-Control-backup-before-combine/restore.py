
import os
import json


class Restore:

    def restore_file(self, filename):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        filename = os.path.normpath(filename)

        if os.path.exists(filename) and not os.path.isfile(filename):
            print("Error: Path is not a regular file!")
            return
        # Read current branch
        with open(".mvc/HEAD", "r") as file:
            branch_name = file.read().strip()

        branch_file = ".mvc/branches/" + branch_name

        with open(branch_file, "r") as file:
            commit_id = file.read().strip()

        if not commit_id:
            print("Error: No commits available!")
            return


        # Search current commit and its previous commits
        file_hash = None
        current_commit = commit_id

        while current_commit:

            commit_path = (
                ".mvc/commits/" + current_commit + ".json"
            )

            if not os.path.exists(commit_path):
                print("Error: Commit history is incomplete!")
                return

            with open(commit_path, "r") as file:
                commit_data = json.load(file)

            committed_files = commit_data["files"]

            if filename in committed_files:
                file_hash = committed_files[filename]
                break

            current_commit = commit_data.get("parent")

        if file_hash is None:

            if not os.path.exists(filename):
                print("Error: File does not exist!")
            else:
                print("Error: File is not tracked!")

            return

        # Find saved object

        # Find saved object
        file_hash = committed_files[filename]
        object_path = ".mvc/objects/" + file_hash

        if not os.path.exists(object_path):
            print("Error: Saved file object not found!")
            return

        # Restore original content
        with open(object_path, "rb") as file:
            content = file.read()

        # Create parent directories if they do not exist
        parent_dir = os.path.dirname(filename)

        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # Restore original content
        with open(filename, "wb") as file:
            file.write(content)
        print(f"File '{filename}' restored successfully!")
