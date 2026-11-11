import os


class Branch:

    def list_branches(self):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        branch_dir = ".mvc/branches"

        branches = os.listdir(branch_dir)

        with open(".mvc/HEAD", "r") as file:
            current_branch = file.read().strip()

        print("\nAvailable Branches:")

        for branch in sorted(branches):

            if branch == current_branch:
                print("*", branch)
            else:
                print(" ", branch)

    def create_branch(self, branch_name):

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        branch_file = ".mvc/branches/" + branch_name

        if os.path.exists(branch_file):
            print("Branch already exists!")
            return

        with open(".mvc/HEAD", "r") as file:
            current_branch = file.read().strip()

        current_file = ".mvc/branches/" + current_branch

        with open(current_file, "r") as file:
            current_commit = file.read().strip()

        with open(branch_file, "w") as file:
            file.write(current_commit)

        print(f"Branch '{branch_name}' created successfully!")

    def checkout_branch(self, branch_name):

        import json
        from hashing import generate_hash

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        branch_file = ".mvc/branches/" + branch_name

        if not os.path.isfile(branch_file):
            print("Error: Branch does not exist!")
            return

        with open(".mvc/HEAD", "r") as file:
            current_branch = file.read().strip()

        if current_branch == branch_name:
            print("Already on this branch!")
            return

        # Check staging area
        with open(".mvc/staging.json", "r") as file:
            staged_files = json.load(file)

        if staged_files:
            print("Error: Commit or unstage your changes first!")
            return

        # Read current and target commits
        with open(".mvc/branches/" + current_branch, "r") as file:
            current_commit = file.read().strip()

        with open(branch_file, "r") as file:
            target_commit = file.read().strip()

        current_files = {}
        target_files = {}

        if current_commit:
            with open(".mvc/commits/" + current_commit + ".json") as file:
                current_files = json.load(file)["files"]

        if target_commit:
            with open(".mvc/commits/" + target_commit + ".json") as file:
                target_files = json.load(file)["files"]

        # Check for uncommitted modifications and deletions
        for filename, old_hash in current_files.items():

            if not os.path.isfile(filename):
                print("Error: Tracked file is missing:", filename)
                return

            with open(filename, "rb") as file:
                current_hash = generate_hash(file.read())

            if current_hash != old_hash:
                print("Error: Commit or restore changes first:", filename)
                return

        # Avoid overwriting untracked files
        for filename in target_files:

            if filename not in current_files and os.path.exists(filename):
                print("Error: Untracked file would be overwritten:", filename)
                return

        # Restore target branch snapshot
        for filename, file_hash in target_files.items():

            object_path = ".mvc/objects/" + file_hash

            with open(object_path, "rb") as file:
                content = file.read()

            with open(filename, "wb") as file:
                file.write(content)

        # Remove files tracked only in the old branch
        for filename in current_files:

            if filename not in target_files and os.path.isfile(filename):
                os.remove(filename)

        # Update HEAD
        with open(".mvc/HEAD", "w") as file:
            file.write(branch_name)

        print("Switched to branch:", branch_name)


    def merge_branch(self, target_branch):

        import json
        from hashing import generate_hash

        if not os.path.exists(".mvc"):
            print("Error: Repository not initialized!")
            return

        target_file = ".mvc/branches/" + target_branch

        if not os.path.isfile(target_file):
            print("Error: Target branch does not exist!")
            return

        with open(".mvc/HEAD", "r") as file:
            current_branch = file.read().strip()

        if current_branch == target_branch:
            print("Error: Cannot merge a branch into itself!")
            return

        current_file = ".mvc/branches/" + current_branch

        with open(current_file, "r") as file:
            current_commit = file.read().strip()

        with open(target_file, "r") as file:
            target_commit = file.read().strip()

        if current_commit == target_commit:
            print("Already up to date!")
            return

        # Check staging area
        with open(".mvc/staging.json", "r") as file:
            staged_files = json.load(file)

        if staged_files:
            print("Error: Commit staged changes first!")
            return

        current_files = {}
        target_files = {}

        # Load current branch snapshot
        if current_commit:
            path = ".mvc/commits/" + current_commit + ".json"

            with open(path, "r") as file:
                current_files = json.load(file)["files"]

        # Load target branch snapshot
        if target_commit:
            path = ".mvc/commits/" + target_commit + ".json"

            with open(path, "r") as file:
                target_files = json.load(file)["files"]

        # Check whether current commit is an ancestor
        # of the target commit
        ancestor = target_commit

        while ancestor and ancestor != current_commit:

            path = ".mvc/commits/" + ancestor + ".json"

            with open(path, "r") as file:
                data = json.load(file)

            ancestor = data["parent"]

        if ancestor != current_commit:
            print("Error: Fast-forward merge not possible!")
            print("Divergent histories need a merge commit.")
            return

        # Check for modified or missing current files
        for filename, old_hash in current_files.items():

            if not os.path.isfile(filename):
                print("Error: Tracked file is missing:", filename)
                return

            with open(filename, "rb") as file:
                current_hash = generate_hash(file.read())

            if current_hash != old_hash:
                print("Error: Commit or restore changes first:", filename)
                return

        # Check for untracked files that may be overwritten
        for filename in target_files:

            if filename not in current_files and os.path.exists(filename):
                print("Error: Untracked file would be overwritten:", filename)
                return

        # Verify all target objects exist before changing files
        for file_hash in target_files.values():

            object_path = ".mvc/objects/" + file_hash

            if not os.path.isfile(object_path):
                print("Error: Object not found:", file_hash)
                return

        # Restore target branch snapshot
        for filename, file_hash in target_files.items():

            object_path = ".mvc/objects/" + file_hash

            with open(object_path, "rb") as file:
                content = file.read()

            with open(filename, "wb") as file:
                file.write(content)

        # Remove files no longer present in target snapshot
        for filename in current_files:

            if filename not in target_files and os.path.isfile(filename):
                os.remove(filename)

        # Move current branch pointer forward
        with open(current_file, "w") as file:
            file.write(target_commit)

        print("Fast-forward merge successful!")
        print("Merged branch:", target_branch)
