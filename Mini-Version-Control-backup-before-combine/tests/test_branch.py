import unittest
import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO

from repository import Repository
from staging import Staging
from commit import Commit
from branch import Branch


class TestBranch(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

        Repository().init()

        self.staging = Staging()
        self.commit = Commit()
        self.branch = Branch()

        with open("hello.txt", "w") as file:
            file.write("Original content")

        self.staging.add("hello.txt")
        self.commit.create_commit("Initial commit")

        self.branch.create_branch("feature")

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def capture_output(self, function, *args):

        output = StringIO()

        with redirect_stdout(output):
            function(*args)

        return output.getvalue()

    def get_branch_commit(self, branch_name):

        with open(".mvc/branches/" + branch_name, "r") as file:
            return file.read().strip()

    def get_current_branch(self):

        with open(".mvc/HEAD", "r") as file:
            return file.read().strip()

    def test_create_branch(self):

        self.branch.create_branch("development")

        self.assertTrue(
            os.path.isfile(".mvc/branches/development")
        )

        self.assertEqual(
            self.get_branch_commit("development"),
            self.get_branch_commit("main")
        )

    def test_checkout_branch(self):

        self.branch.checkout_branch("feature")

        self.assertEqual(
            self.get_current_branch(),
            "feature"
        )

    def test_fast_forward_merge(self):

        # Switch to feature branch
        self.branch.checkout_branch("feature")

        # Modify file
        with open("hello.txt", "w") as file:
            file.write("Feature branch content")

        # Stage and commit
        self.staging.add("hello.txt")
        self.commit.create_commit("Feature update")

        feature_commit = self.get_branch_commit("feature")

        # Switch back to main
        self.branch.checkout_branch("main")

        # Merge feature into main
        output = self.capture_output(
            self.branch.merge_branch,
            "feature"
        )

        main_commit = self.get_branch_commit("main")

        self.assertEqual(main_commit, feature_commit)

        self.assertIn(
            "Fast-forward merge successful!",
            output
        )

        with open("hello.txt", "r") as file:
            content = file.read()

        self.assertEqual(content, "Feature branch content")

    def test_divergent_merge_rejected(self):

        # Create a separate commit on feature
        self.branch.checkout_branch("feature")

        with open("hello.txt", "w") as file:
            file.write("Feature change")

        self.staging.add("hello.txt")
        self.commit.create_commit("Feature commit")

        # Switch to main
        self.branch.checkout_branch("main")

        # Create an independent commit on main
        with open("hello.txt", "w") as file:
            file.write("Main change")

        self.staging.add("hello.txt")
        self.commit.create_commit("Main commit")

        main_commit_before = self.get_branch_commit("main")

        # Try merging divergent histories
        output = self.capture_output(
            self.branch.merge_branch,
            "feature"
        )

        main_commit_after = self.get_branch_commit("main")

        self.assertIn(
            "Fast-forward merge not possible!",
            output
        )

        self.assertEqual(
            main_commit_before,
            main_commit_after
        )


if __name__ == "__main__":
    unittest.main()
