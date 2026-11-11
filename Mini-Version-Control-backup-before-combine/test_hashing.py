import unittest
from version_control import generate_hash

class TestHashing(unittest.TestCase):

    def test_same_content_same_hash(self):
        content = b"Hello Mini Git"

        hash1 = generate_hash(content)
        hash2 = generate_hash(content)

        self.assertEqual(hash1, hash2)

    def test_different_content_different_hash(self):
        content1 = b"Hello"
        content2 = b"Hello World"

        hash1 = generate_hash(content1)
        hash2 = generate_hash(content2)

        self.assertNotEqual(hash1, hash2)

    def test_hash_length(self):
        content = b"Mini Git Project"

        result = generate_hash(content)

        self.assertEqual(len(result), 64)


if __name__ == "__main__":
    unittest.main()
