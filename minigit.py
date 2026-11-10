import argparse
import difflib
import hashlib
import json
import os
import sys
import time

class MiniGit:
 
    def __init__(self):
        self.repo = ".minigit"
        self.objects_dir = os.path.join(self.repo, "objects")
        self.index_path = os.path.join(self.repo, "index")
        self.head_path = os.path.join(self.repo, "HEAD")
        self.heads_dir = os.path.join(self.repo, "refs", "heads")

    def require_repo(self):
        if not os.path.isdir(self.repo):
            sys.exit("Not a MiniGit repository. Run 'init' first.")
 
    def store_object(self, data):
        """Save bytes under their SHA-1 hash and return the hash."""
        h = hashlib.sha1(data).hexdigest()
        path = os.path.join(self.objects_dir, h)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data)
        return h
 
    def load_object(self, h):
        with open(os.path.join(self.objects_dir, h), "rb") as f:
            return f.read()
 
    def read_index(self):
        with open(self.index_path) as f:
            return json.load(f)
 
    def write_index(self, index):
        with open(self.index_path, "w") as f:
            json.dump(index, f, indent=4, sort_keys=True)
 
    def current_branch(self):
        with open(self.head_path) as f:
            ref = f.read().strip()          # "ref: refs/heads/master"
        return ref.split("refs/heads/")[1]
 
    def branch_file(self, name):
        return os.path.join(self.heads_dir, name)
 
    def head_commit(self):
        """Hash of the latest commit on the current branch (or None)."""
        path = self.branch_file(self.current_branch())
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return f.read().strip() or None
 
    def load_commit(self, h):
        return json.loads(self.load_object(h))
 
    def tree_of(self, commit_hash):
        return self.load_commit(commit_hash)["tree"] if commit_hash else {}
 
    def working_files(self):
        """{path: hash} for every file in the folder (ignoring .minigit)."""
        files = {}
        for root, dirs, names in os.walk("."):
            dirs[:] = [d for d in dirs if d != self.repo]
            for name in names:
                path = os.path.normpath(os.path.join(root, name))
                with open(path, "rb") as f:
                    files[path] = hashlib.sha1(f.read()).hexdigest()
        return files

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
 
    def add(self, path):
        """Stage a file (or every file inside a folder)."""
        self.require_repo()
        path = os.path.normpath(path)
 
        if os.path.isdir(path):
            targets = []
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs if d != self.repo]
                for name in names:
                    targets.append(os.path.normpath(os.path.join(root, name)))
        elif os.path.isfile(path):
            targets = [path]
        else:
            print(f"Error: '{path}' does not exist.")
            return
 
        index = self.read_index()
        for t in targets:
            with open(t, "rb") as f:
                index[t] = self.store_object(f.read())
            print(f"Added {t}")
        self.write_index(index)
 
    def commit(self, message):
        """Save the staged files as a new snapshot."""
        self.require_repo()
        index = self.read_index()
        parent = self.head_commit()
 
        if index == self.tree_of(parent):
            print("Nothing to commit (staging area matches last commit).")
            return
 
        commit = {
            "tree": index,
            "parent": parent,
            "message": message,
            "timestamp": int(time.time()),
        }
        h = self.store_object(json.dumps(commit, sort_keys=True).encode())
 
        with open(self.branch_file(self.current_branch()), "w") as f:
            f.write(h)
 
        print(f"[{self.current_branch()} {h[:7]}] {message}")
 
    def log(self):
        """Show commits from newest to oldest."""
        self.require_repo()
        h = self.head_commit()
        if not h:
            print("No commits yet.")
            return
 
        while h:
            c = self.load_commit(h)
            when = time.strftime("%a %b %d %H:%M:%S %Y",
                                 time.localtime(c["timestamp"]))
            print(f"commit {h}")
            print(f"Date:   {when}")
            print(f"\n    {c['message']}\n")
            h = c["parent"]
 
    def status(self):
        """Compare working folder, staging area and last commit."""
        self.require_repo()
        index = self.read_index()
        head = self.tree_of(self.head_commit())
        work = self.working_files()
 
        print(f"On branch {self.current_branch()}")
 
        staged = sorted(
            [(p, "new file") for p in index if p not in head]
            + [(p, "modified") for p in index
               if p in head and index[p] != head[p]]
            + [(p, "deleted") for p in head if p not in index]
        )
        unstaged = sorted(
            [(p, "modified") for p in index
             if p in work and work[p] != index[p]]
            + [(p, "deleted") for p in index if p not in work]
        )
        untracked = sorted(p for p in work if p not in index)
 
        if staged:
            print("\nChanges to be committed:")
            for p, s in staged:
                print(f"    {s}: {p}")
        if unstaged:
            print("\nChanges not staged for commit:")
            for p, s in unstaged:
                print(f"    {s}: {p}")
        if untracked:
            print("\nUntracked files:")
            for p in untracked:
                print(f"    {p}")
        if not (staged or unstaged or untracked):
            print("\nNothing to commit, working tree clean.")
 
    def diff(self, staged=False):
        """Line-by-line changes.
        default : working folder vs staging area
        --staged: staging area vs last commit
        """
        self.require_repo()
        index = self.read_index()
 
        if staged:
            old_tree, new_tree = self.tree_of(self.head_commit()), index
            read_new = lambda p: self.load_object(new_tree[p])
        else:
            old_tree, new_tree = index, self.working_files()
 
            def read_new(p):
                with open(p, "rb") as f:
                    return f.read()
 
        def lines(data):
            return data.decode("utf-8", errors="replace").splitlines(keepends=True)
 
        found = False
        for path in sorted(set(old_tree) | set(new_tree)):
            if staged is False and path not in old_tree:
                continue                      # untracked file: not part of diff
            old = lines(self.load_object(old_tree[path])) if path in old_tree else []
            new = lines(read_new(path)) if path in new_tree else []
            if old == new:
                continue
            found = True
            for line in difflib.unified_diff(
                    old, new, fromfile=f"a/{path}", tofile=f"b/{path}"):
                print(line.rstrip("\n"))
        if not found:
            print("No differences.")
 
    def branch(self, name=None):
        """No name: list branches. With name: create a new branch."""
        self.require_repo()
 
        if name is None:
            current = self.current_branch()
            for b in sorted(os.listdir(self.heads_dir)):
                print(("* " if b == current else "  ") + b)
            if not os.listdir(self.heads_dir):
                print(f"* {current}")
            return
 
        head = self.head_commit()
        if head is None:
            print("Error: make a commit before creating a branch.")
            return
        if os.path.exists(self.branch_file(name)):
            print(f"Error: branch '{name}' already exists.")
            return
        with open(self.branch_file(name), "w") as f:
            f.write(head)
        print(f"Created branch '{name}'")
 
    def checkout(self, name):
        """Switch to another branch and restore its files."""
        self.require_repo()
 
        if not os.path.exists(self.branch_file(name)):
            print(f"Error: branch '{name}' does not exist.")
            return
        if name == self.current_branch():
            print(f"Already on '{name}'")
            return
 
        index = self.read_index()
        head_tree = self.tree_of(self.head_commit())
        work = self.working_files()
 
        # Refuse to switch if it could lose uncommitted work
        dirty = index != head_tree or any(
            p not in work or work[p] != index[p] for p in index)
        if dirty:
            print("Error: you have uncommitted changes. Commit them first.")
            return
 
        with open(self.branch_file(name)) as f:
            target_tree = self.tree_of(f.read().strip())
 
        # Refuse to overwrite untracked files
        for p in target_tree:
            if p in work and p not in index:
                print(f"Error: untracked file '{p}' would be overwritten.")
                return
 
        # Remove files that exist here but not on the target branch
        for p in head_tree:
            if p not in target_tree and os.path.exists(p):
                os.remove(p)
 
        # Write the target branch's files into the working folder
        for p, h in target_tree.items():
            folder = os.path.dirname(p)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(p, "wb") as f:
                f.write(self.load_object(h))
 
        self.write_index(dict(target_tree))
        with open(self.head_path, "w") as f:
            f.write(f"ref: refs/heads/{name}\n")
        print(f"Switched to branch '{name}'")
 
 
def main():
 
    parser = argparse.ArgumentParser(
        description="Mini Version Control System"
    )
    sub = parser.add_subparsers(dest="command", required=True)
 
    sub.add_parser("init", help="create a repository")
 
    p = sub.add_parser("add", help="stage a file or folder")
    p.add_argument("path")
 
    p = sub.add_parser("commit", help="save a snapshot")
    p.add_argument("-m", "--message", required=True)
 
    sub.add_parser("log", help="show commit history")
    sub.add_parser("status", help="show what changed")
 
    p = sub.add_parser("diff", help="show line-by-line changes")
    p.add_argument("--staged", action="store_true")
 
    p = sub.add_parser("branch", help="list or create branches")
    p.add_argument("name", nargs="?")
 
    p = sub.add_parser("checkout", help="switch branch")
    p.add_argument("name")
 
    args = parser.parse_args()
    git = MiniGit()
 
    if args.command == "init":
        git.init()
    elif args.command == "add":
        git.add(args.path)
    elif args.command == "commit":
        git.commit(args.message)
    elif args.command == "log":
        git.log()
    elif args.command == "status":
        git.status()
    elif args.command == "diff":
        git.diff(args.staged)
    elif args.command == "branch":
        git.branch(args.name)
    elif args.command == "checkout":
        git.checkout(args.name)
 
 
if __name__ == "__main__":
    main()


