
import os
import json
import argparse


class MiniGit:

    def __init__(self):
        self.repo = ".minigit"

    def init(self):

        if os.path.exists(self.repo):
            print("Repository already exists!")
            return

        os.makedirs(self.repo)

        os.makedirs(self.repo + "/objects")

        os.makedirs(self.repo + "/refs/heads")

        with open(self.repo + "/HEAD", "w") as f:
            f.write("ref: refs/heads/master\n")

        with open(self.repo + "/index", "w") as f:
            json.dump({}, f, indent=4)

        print("Initialized empty MiniGit repository!")


def main():

    parser = argparse.ArgumentParser(
        description="Mini Version Control System"
    )

    parser.add_argument(
        "command",
        choices=["init"],
        help="VCS command"
    )

    args = parser.parse_args()

    git = MiniGit()

    if args.command == "init":
        git.init()


if __name__ == "__main__":
    main()
