import io
import unittest
import os
import tempfile

from contextlib import redirect_stdout
from repository import Repository
from staging import Staging
from commit import Commit
from status import Status


class TestStatus(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

        Repository().init()

        self.staging = Staging()
        self.commit = Commit()
        self.status = Status()

        with open("hello.txt", "w") as file:
            file.write("Original content")

        self.staging.add("hello.txt")
        self.commit.create_commit("First commit")

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def test_untracked_file_detection(self):

        with open("new.txt", "w") as file:
            file.write("New file")

        self.status.show_status()

        self.assertTrue(os.path.isfile("new.txt"))

    def test_modified_file_detection(self):

        with open("hello.txt", "w") as file:
            file.write("Modified content")

        self.status.show_status()

        self.assertTrue(os.path.isfile("hello.txt"))

    def test_staged_file_detection(self):

        with open("hello.txt", "w") as file:
            file.write("Staged content")

        self.staging.add("hello.txt")

        self.status.show_status()

        self.assertTrue(os.path.isfile(".mvc/staging.json"))


    def test_nested_file_detection(self):

        os.makedirs("docs/src")

        with open("docs/src/example.py", "w") as file:
            file.write("print('Hello')")

        output = io.StringIO()

        with redirect_stdout(output):
            self.status.show_status()

        self.assertIn("docs/src/example.py", output.getvalue())



if __name__ == "__main__":
    unittest.main()
