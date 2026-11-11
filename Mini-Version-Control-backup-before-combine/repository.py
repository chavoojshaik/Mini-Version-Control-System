import os
import json


class Repository:

    def __init__(self):
        self.repo_path = ".mvc"

    def init(self):

        if os.path.exists(self.repo_path):
            print("Repository already exists!")
            return

        os.makedirs(self.repo_path)

        os.makedirs(".mvc/objects")
        os.makedirs(".mvc/commits")
        os.makedirs(".mvc/branches")

        with open(".mvc/staging.json", "w") as file:
            json.dump([], file)

        with open(".mvc/HEAD", "w") as file:
            file.write("main")

        with open(".mvc/branches/main", "w") as file:
            file.write("")

        print("Mini Version Control Repository Initialized!")
