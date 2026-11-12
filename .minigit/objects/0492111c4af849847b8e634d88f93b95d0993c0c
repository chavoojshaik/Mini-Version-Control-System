import argparse
import difflib
import hashlib
import json
import os
import sys
import time
from abc import ABC, abstractmethod
 
 
class GitObject(ABC):
    @abstractmethod
    def to_bytes(self):
        pass
 
    def get_hash(self):
        return hashlib.sha1(self.to_bytes()).hexdigest()
 
 
class Blob(GitObject):
    def __init__(self, content):
        self.content = content
 
    def to_bytes(self):
        return self.content
 
 
class Commit(GitObject):
    def __init__(self, tree, parent, message, timestamp=None):
        self.tree = tree
        self.parent = parent
        self.message = message
        self.timestamp = timestamp or int(time.time())
 
    def to_bytes(self):
        data = {"tree": self.tree, "parent": self.parent,
                "message": self.message, "timestamp": self.timestamp}
        return json.dumps(data, sort_keys=True).encode()
 
    @classmethod
    def from_bytes(cls, raw):
        return cls(**json.loads(raw))
 
    def __str__(self):
        date = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(self.timestamp))
        return f"commit {self.get_hash()}\nDate:   {date}\n\n    {self.message}\n"
 
 
class Repository:
    def __init__(self):
        self.__root = ".minigit"
        self.__objects = os.path.join(self.__root, "objects")
        self.__heads = os.path.join(self.__root, "refs", "heads")
        self.__index = os.path.join(self.__root, "index")
        self.__head = os.path.join(self.__root, "HEAD")
 
    def exists(self):
        return os.path.isdir(self.__root)
 
    def create(self):
        os.makedirs(self.__objects)
        os.makedirs(self.__heads)
        with open(self.__head, "w") as f:
            f.write("ref: refs/heads/master\n")
        self.write_index({})
 
    # objects
    def save_object(self, obj):
        h = obj.get_hash()
        path = os.path.join(self.__objects, h)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(obj.to_bytes())
        return h
 
    def read_object(self, h):
        with open(os.path.join(self.__objects, h), "rb") as f:
            return f.read()
 
    def load_commit(self, h):
        return Commit.from_bytes(self.read_object(h))
 
    # index
    def read_index(self):
        with open(self.__index) as f:
            return json.load(f)
 
    def write_index(self, index):
        with open(self.__index, "w") as f:
            json.dump(index, f, indent=4, sort_keys=True)
 
    # branches
    def current_branch(self):
        with open(self.__head) as f:
            return f.read().strip().split("refs/heads/")[1]
 
    def set_current_branch(self, name):
        with open(self.__head, "w") as f:
            f.write(f"ref: refs/heads/{name}\n")
 
    def branch_names(self):
        return sorted(os.listdir(self.__heads))
 
    def branch_exists(self, name):
        return os.path.exists(os.path.join(self.__heads, name))
 
    def read_branch(self, name):
        path = os.path.join(self.__heads, name)
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return f.read().strip() or None
 
    def write_branch(self, name, commit_hash):
        with open(os.path.join(self.__heads, name), "w") as f:
            f.write(commit_hash)
 
    def head_commit(self):
        return self.read_branch(self.current_branch())
 
    def tree_of(self, commit_hash):
        if commit_hash is None:
            return {}
        return self.load_commit(commit_hash).tree
 
    def head_tree(self):
        return self.tree_of(self.head_commit())
 
    # files in the project folder
    def working_files(self):
        files = {}
        for root, dirs, names in os.walk("."):
            dirs[:] = [d for d in dirs if d != self.__root]
            for name in names:
                path = os.path.normpath(os.path.join(root, name))
                with open(path, "rb") as f:
                    files[path] = Blob(f.read()).get_hash()
        return files
 
 
class Command(ABC):
    name = ""
    needs_repo = True
 
    def __init__(self, repo):
        self.repo = repo
 
    @classmethod
    def add_arguments(cls, parser):
        pass
 
    @abstractmethod
    def execute(self, args):
        pass
 
 
class InitCommand(Command):
    name = "init"
    needs_repo = False
 
    def execute(self, args):
        if self.repo.exists():
            print("Repository already exists!")
            return
        self.repo.create()
        print("Initialized empty MiniGit repository!")
 
 
class AddCommand(Command):
    name = "add"
 
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("path")
 
    def execute(self, args):
        path = os.path.normpath(args.path)
        files = self.repo.working_files()
 
        if path in files:
            targets = [path]
        elif path == ".":
            targets = list(files)
        else:
            targets = [p for p in files if p.startswith(path + os.sep)]
 
        if not targets:
            print(f"Error: '{path}' does not exist.")
            return
 
        index = self.repo.read_index()
        for p in targets:
            with open(p, "rb") as f:
                index[p] = self.repo.save_object(Blob(f.read()))
            print(f"Added {p}")
        self.repo.write_index(index)
 
 
class CommitCommand(Command):
    name = "commit"
 
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-m", "--message", required=True)
 
    def execute(self, args):
        index = self.repo.read_index()
        parent = self.repo.head_commit()
 
        if index == self.repo.tree_of(parent):
            print("Nothing to commit.")
            return
 
        commit = Commit(index, parent, args.message)
        h = self.repo.save_object(commit)
        branch = self.repo.current_branch()
        self.repo.write_branch(branch, h)
        print(f"[{branch} {h[:7]}] {args.message}")
 
 
class LogCommand(Command):
    name = "log"
 
    def execute(self, args):
        h = self.repo.head_commit()
        if h is None:
            print("No commits yet.")
            return
        while h:
            commit = self.repo.load_commit(h)
            print(commit)
            h = commit.parent
 
 
class StatusCommand(Command):
    name = "status"
 
    def show(self, title, entries):
        if entries:
            print(f"\n{title}")
            for label, path in sorted(entries, key=lambda e: e[1]):
                print(f"    {label}: {path}")
 
    def execute(self, args):
        index = self.repo.read_index()
        head = self.repo.head_tree()
        work = self.repo.working_files()
 
        in_index, in_head, in_work = set(index), set(head), set(work)
 
        staged = [("new file", p) for p in in_index - in_head]
        staged += [("modified", p) for p in in_index & in_head if index[p] != head[p]]
        staged += [("deleted", p) for p in in_head - in_index]
 
        unstaged = [("modified", p) for p in in_index & in_work if index[p] != work[p]]
        unstaged += [("deleted", p) for p in in_index - in_work]
 
        untracked = [("untracked", p) for p in in_work - in_index]
 
        print(f"On branch {self.repo.current_branch()}")
        self.show("Changes to be committed:", staged)
        self.show("Changes not staged for commit:", unstaged)
        self.show("Untracked files:", untracked)
        if not (staged or unstaged or untracked):
            print("\nNothing to commit, working tree clean.")
 
 
class DiffCommand(Command):
    name = "diff"
 
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("--staged", action="store_true")
 
    def get_lines(self, data):
        return data.decode(errors="replace").splitlines(keepends=True)
 
    def execute(self, args):
        index = self.repo.read_index()
 
        if args.staged:
            old, new = self.repo.head_tree(), index
            read_new = lambda p: self.repo.read_object(new[p])
        else:
            old, new = index, self.repo.working_files()
            read_new = lambda p: open(p, "rb").read()
 
        found = False
        for path in sorted(set(old) | set(new)):
            if not args.staged and path not in old:
                continue
            old_lines = self.get_lines(self.repo.read_object(old[path])) if path in old else []
            new_lines = self.get_lines(read_new(path)) if path in new else []
            if old_lines != new_lines:
                found = True
                for line in difflib.unified_diff(old_lines, new_lines,
                                                 fromfile="a/" + path, tofile="b/" + path):
                    print(line.rstrip("\n"))
        if not found:
            print("No differences.")
 
 
class BranchCommand(Command):
    name = "branch"
 
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("branch_name", nargs="?")
 
    def execute(self, args):
        name = args.branch_name
 
        if name is None:
            current = self.repo.current_branch()
            for b in self.repo.branch_names() or [current]:
                print(("* " if b == current else "  ") + b)
            return
 
        head = self.repo.head_commit()
        if head is None:
            print("Error: make a commit before creating a branch.")
        elif self.repo.branch_exists(name):
            print(f"Error: branch '{name}' already exists.")
        else:
            self.repo.write_branch(name, head)
            print(f"Created branch '{name}'")
 
 
class CheckoutCommand(Command):
    name = "checkout"
 
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("branch_name")
 
    def execute(self, args):
        name = args.branch_name
        if not self.repo.branch_exists(name):
            print(f"Error: branch '{name}' does not exist.")
            return
        if name == self.repo.current_branch():
            print(f"Already on '{name}'")
            return
 
        index = self.repo.read_index()
        head_tree = self.repo.head_tree()
        work = self.repo.working_files()
 
        changed = [p for p in index if p not in work or work[p] != index[p]]
        if index != head_tree or changed:
            print("Error: you have uncommitted changes. Commit them first.")
            return
 
        target = self.repo.tree_of(self.repo.read_branch(name))
 
        for p in target:
            if p in work and p not in index:
                print(f"Error: untracked file '{p}' would be overwritten.")
                return
 
        for p in set(head_tree) - set(target):
            os.remove(p)
 
        for p, h in target.items():
            folder = os.path.dirname(p)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(p, "wb") as f:
                f.write(self.repo.read_object(h))
 
        self.repo.write_index(dict(target))
        self.repo.set_current_branch(name)
        print(f"Switched to branch '{name}'")
 
 
COMMANDS = {c.name: c for c in [InitCommand, AddCommand, CommitCommand, LogCommand,
                                StatusCommand, DiffCommand, BranchCommand, CheckoutCommand]}
 
 
def main():
    parser = argparse.ArgumentParser(description="Mini Version Control System")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, cls in COMMANDS.items():
        cls.add_arguments(sub.add_parser(name))
 
    args = parser.parse_args()
    repo = Repository()
    command = COMMANDS[args.command](repo)
 
    if command.needs_repo and not repo.exists():
        sys.exit("Not a MiniGit repository. Run 'init' first.")
 
    command.execute(args)
 
 
if __name__ == "__main__":
    main()

