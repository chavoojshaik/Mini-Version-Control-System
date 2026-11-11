
import os
import json


class Log:

    def show_log(self):

        if not os.path.exists(".mvc"):
            print("Repository not initialized!")
            return

        # Read current branch
        with open(".mvc/HEAD", "r") as file:
            branch_name = file.read().strip()

        branch_file = ".mvc/branches/" + branch_name

        if not os.path.exists(branch_file):
            print("Error: Branch does not exist!")
            return

        with open(branch_file, "r") as file:
            commit_id = file.read().strip()

        if not commit_id:
            print("No commits yet!")
            return

        print("\nCommit History")
        print("====================")

        # Traverse commits from newest to oldest
        while commit_id:

            commit_path = (
                ".mvc/commits/" + commit_id + ".json"
            )

            if not os.path.exists(commit_path):
                print("Error: Commit not found:", commit_id)
                return

            with open(commit_path, "r") as file:
                commit_data = json.load(file)

            print("\nCommit:", commit_id)
            print("Message:", commit_data["message"])
            print("Date:", commit_data["timestamp"])
            print("Parent:", commit_data["parent"])

            commit_id = commit_data["parent"]
