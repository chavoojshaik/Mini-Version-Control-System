import unittest
import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO

from repository import Repository
from staging import Staging
from commit import Commit
from diff import Diff


class TestDiff(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

        Repository().init()

        self.staging = Staging()
        self.commit = Commit()
        self.diff = Diff()

        with open("hello.txt", "w") as file:
            file.write("Original content\n")

        self.staging.add("hello.txt")
        self.commit.create_commit("First commit")

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def capture_diff(self, filename):

        output = StringIO()

        with redirect_stdout(output):
            self.diff.show_diff(filename)

        return output.getvalue()

    def test_no_changes(self):

        output = self.capture_diff("hello.txt")

        self.assertIn("No changes found!", output)

    def test_modified_file(self):

        with open("hello.txt", "w") as file:
            file.write("Modified content\n")

        output = self.capture_diff("hello.txt")

        self.assertIn("-Original content", output)
        self.assertIn("+Modified content", output)

    def test_untracked_file(self):

        with open("new.txt", "w") as file:
            file.write("New file")

        output = self.capture_diff("new.txt")

        self.assertIn("File is not tracked", output)


if __name__ == "__main__":
    unittest.main()
