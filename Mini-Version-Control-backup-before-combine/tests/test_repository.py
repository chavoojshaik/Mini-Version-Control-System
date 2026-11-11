import unittest
import os
import tempfile
import json

from repository import Repository


class TestRepository(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_dir = os.getcwd()

        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()

    def test_repository_initialization(self):

        repo = Repository()
        repo.init()

        self.assertTrue(os.path.isdir(".mvc"))
        self.assertTrue(os.path.isdir(".mvc/objects"))
        self.assertTrue(os.path.isdir(".mvc/commits"))
        self.assertTrue(os.path.isdir(".mvc/branches"))

        self.assertTrue(os.path.isfile(".mvc/HEAD"))
        self.assertTrue(os.path.isfile(".mvc/staging.json"))

    def test_head_contains_main(self):

        repo = Repository()
        repo.init()

        with open(".mvc/HEAD", "r") as file:
            branch = file.read()

        self.assertEqual(branch, "main")

    def test_staging_area_is_empty(self):

        repo = Repository()
        repo.init()

        with open(".mvc/staging.json", "r") as file:
            staged_files = json.load(file)

        self.assertEqual(staged_files, [])


if __name__ == "__main__":
    unittest.main()
