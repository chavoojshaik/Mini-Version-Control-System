
import sys

from repository import Repository
from staging import Staging
from commit import Commit
from status import Status
from log import Log
from diff import Diff
from restore import Restore
from branch import Branch


def main():

    if len(sys.argv) < 2:
        print("Usage: python3 main.py <command>")
        return

    command = sys.argv[1]

    # Initialize repository
    if command == "init":

        repo = Repository()
        repo.init()

    # Add file to staging
    elif command == "add":

        if len(sys.argv) < 3:
            print("Usage: python3 main.py add <filename>")
            return

        staging = Staging()
        staging.add(sys.argv[2])


    # Remove file and stage its deletion
    elif command == "remove":

        if len(sys.argv) < 3:
            print("Usage: python3 main.py remove <filename>")
            return

        staging = Staging()
        staging.remove(sys.argv[2])



    # Create commit
    elif command == "commit":

        if len(sys.argv) < 4 or sys.argv[2] != "-m":
            print('Usage: python3 main.py commit -m "message"')
            return

        message = " ".join(sys.argv[3:])

        commit = Commit()
        commit.create_commit(message)

    # Show status
    elif command == "status":

        status = Status()
        status.show_status()

    # Show commit history
    elif command == "log":

        log = Log()
        log.show_log()

    # Show file differences
    elif command == "diff":

        if len(sys.argv) < 3:
            print("Usage: python3 main.py diff <filename>")
            return

        difference = Diff()
        difference.show_diff(sys.argv[2])

    # Restore committed file
    elif command == "restore":

        if len(sys.argv) < 3:
            print("Usage: python3 main.py restore <filename>")
            return

        restore = Restore()
        restore.restore_file(sys.argv[2])

    # Branch operations
    elif command == "branch":

        branch = Branch()

        if len(sys.argv) == 2:
            branch.list_branches()

        elif len(sys.argv) == 4 and sys.argv[2] == "create":
            branch.create_branch(sys.argv[3])

        elif len(sys.argv) == 4 and sys.argv[2] == "checkout":
            branch.checkout_branch(sys.argv[3])

        else:
            print("Usage:")
            print("python3 main.py branch")
            print("python3 main.py branch create <branch_name>")
            print("python3 main.py branch checkout <branch_name>")

    # Merge branches
    elif command == "merge":

        if len(sys.argv) < 3:
            print("Usage: python3 main.py merge <branch_name>")
            return

        branch = Branch()
        branch.merge_branch(sys.argv[2])

    # Unknown command
    else:

        print("Unknown command!")


if __name__ == "__main__":
    main()

