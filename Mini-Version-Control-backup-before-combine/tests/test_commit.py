import unittest
import os
import tempfile
import json

from repository import Repository
from staging import Staging
from commit import Commit
from hashing import generate_hash


class TestCommit(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

        repo = Repository()
        repo.init()

        self.staging = Staging()
        self.commit = Commit()

        with open("hello.txt", "w") as file:
            file.write("Hello Mini Git")

        self.staging.add("hello.txt")

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def get_current_commit(self):

        with open(".mvc/branches/main", "r") as file:
            return file.read().strip()

    def test_commit_creation(self):

        self.commit.create_commit("First commit")

        commit_id = self.get_current_commit()

        self.assertTrue(commit_id)

        commit_path = ".mvc/commits/" + commit_id + ".json"

        self.assertTrue(os.path.isfile(commit_path))

    def test_staging_cleared_after_commit(self):

        self.commit.create_commit("First commit")

        with open(".mvc/staging.json", "r") as file:
            staged = json.load(file)

        self.assertEqual(staged, [])

    def test_file_hash_saved_in_commit(self):

        self.commit.create_commit("First commit")

        commit_id = self.get_current_commit()

        commit_path = ".mvc/commits/" + commit_id + ".json"

        with open(commit_path, "r") as file:
            data = json.load(file)

        with open("hello.txt", "rb") as file:
            expected_hash = generate_hash(file.read())

        self.assertEqual(
            data["files"]["hello.txt"],
            expected_hash
        )

    def test_parent_commit_preserved(self):

        self.commit.create_commit("First commit")

        first_commit = self.get_current_commit()

        with open("hello.txt", "a") as file:
            file.write("\nSecond line")

        self.staging.add("hello.txt")

        self.commit.create_commit("Second commit")

        second_commit = self.get_current_commit()

        path = ".mvc/commits/" + second_commit + ".json"

        with open(path, "r") as file:
            data = json.load(file)

        self.assertEqual(data["parent"], first_commit)


    def test_deleted_file_removed_from_commit_snapshot(self):

        # First commit the file
        self.commit.create_commit("Initial commit")

        # Delete and stage the file
        os.remove("hello.txt")
        self.staging.remove("hello.txt")

        # Commit the deletion
        self.commit.create_commit("Delete hello.txt")

        # Read the latest commit
        commit_id = self.get_current_commit()
        commit_path = ".mvc/commits/" + commit_id + ".json"

        with open(commit_path, "r") as file:
            data = json.load(file)

        # Deleted file should not exist in the latest snapshot
        self.assertNotIn("hello.txt", data["files"])

        # Staging area should be empty
        with open(".mvc/staging.json", "r") as file:
            staged = json.load(file)

        self.assertEqual(staged, [])


if __name__ == "__main__":
    unittest.main()
