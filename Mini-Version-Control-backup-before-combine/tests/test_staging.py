import unittest
import os
import tempfile
import json

from commit import Commit
from repository import Repository
from staging import Staging


class TestStaging(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

        repo = Repository()
        repo.init()

        self.staging = Staging()

        with open("hello.txt", "w") as file:
            file.write("Hello Mini Git")

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def test_add_existing_file(self):

        self.staging.add("hello.txt")

        with open(".mvc/staging.json", "r") as file:
            staged = json.load(file)

        self.assertIn("hello.txt", staged)

    def test_duplicate_file_not_added(self):

        self.staging.add("hello.txt")
        self.staging.add("hello.txt")

        with open(".mvc/staging.json", "r") as file:
            staged = json.load(file)

        self.assertEqual(staged.count("hello.txt"), 1)

    def test_missing_file_not_added(self):

        self.staging.add("missing.txt")

        with open(".mvc/staging.json", "r") as file:
            staged = json.load(file)

        self.assertNotIn("missing.txt", staged)

    def test_remove_committed_file(self):

        # First commit the file
        self.staging.add("hello.txt")

        commit = Commit()
        commit.create_commit("Initial commit")

        # Remove the committed file
        self.staging.remove("hello.txt")

        # Check that the file is deleted
        self.assertFalse(os.path.exists("hello.txt"))

        # Check that deletion is staged
        with open(".mvc/staging.json", "r") as file:
            staged = json.load(file)

        self.assertIn("hello.txt", staged)


if __name__ == "__main__":
    unittest.main()
