import os
import json


class Staging:

    def __init__(self):
        self.staging_file = ".mvc/staging.json"

    def add(self, filename):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        if not os.path.isfile(filename):
            print("Error: File does not exist!")
            return

        filename = os.path.normpath(filename)

        if filename.startswith(".mvc/") or filename == ".mvc":
            print("Error: Cannot stage repository files!")
            return

        with open(self.staging_file, "r") as file:
            staged_files = json.load(file)

        if filename in staged_files:
            print("File already staged!")
            return

        staged_files.append(filename)

        with open(self.staging_file, "w") as file:
            json.dump(staged_files, file, indent=4)

        print(f"File '{filename}' added to staging area!")


    def remove(self, filename):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        filename = os.path.normpath(filename)

        if filename.startswith(".mvc/") or filename == ".mvc":
            print("Error: Cannot remove repository files!")
            return

        with open(self.staging_file, "r") as file:
            staged_files = json.load(file)

        # Check whether the file is tracked
        with open(".mvc/HEAD", "r") as file:
            branch_name = file.read().strip()

        branch_file = ".mvc/branches/" + branch_name

        with open(branch_file, "r") as file:
            commit_id = file.read().strip()

        if not commit_id:
            print("Error: No committed files available!")
            return

        commit_path = ".mvc/commits/" + commit_id + ".json"

        with open(commit_path, "r") as file:
            commit_data = json.load(file)

        if filename not in commit_data["files"]:
            print("Error: File is not tracked!")
            return

        # Remove file from working directory
        if os.path.isfile(filename):
            os.remove(filename)

        if filename not in staged_files:
            staged_files.append(filename)

        with open(self.staging_file, "w") as file:
            json.dump(staged_files, file, indent=4)

        print(f"File '{filename}' marked for deletion!")
