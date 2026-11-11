import unittest
import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO

from repository import Repository
from staging import Staging
from commit import Commit
from restore import Restore


class TestRestore(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

        Repository().init()

        self.staging = Staging()
        self.commit = Commit()
        self.restore = Restore()

        with open("hello.txt", "w") as file:
            file.write("Original content")

        self.staging.add("hello.txt")
        self.commit.create_commit("First commit")

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def capture_restore(self, filename):

        output = StringIO()

        with redirect_stdout(output):
            self.restore.restore_file(filename)

        return output.getvalue()

    def test_restore_modified_file(self):

        with open("hello.txt", "w") as file:
            file.write("Modified content")

        self.restore.restore_file("hello.txt")

        with open("hello.txt", "r") as file:
            content = file.read()

        self.assertEqual(content, "Original content")

    def test_restore_untracked_file(self):

        with open("new.txt", "w") as file:
            file.write("New content")

        output = self.capture_restore("new.txt")

        self.assertIn("File is not tracked", output)

    def test_restore_missing_file(self):

        output = self.capture_restore("missing.txt")

        self.assertIn("File does not exist", output)


    def test_restore_deleted_file(self):

        # Delete the previously committed file
        self.staging.remove("hello.txt")

        # Commit the deletion
        self.commit.create_commit("Delete hello.txt")

        # Restore the deleted file
        self.restore.restore_file("hello.txt")

        # Check that the file exists again
        self.assertTrue(os.path.isfile("hello.txt"))

        # Verify original content
        with open("hello.txt", "r") as file:
            content = file.read()

        self.assertEqual(content, "Original content")


if __name__ == "__main__":
    unittest.main()
