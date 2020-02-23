import unittest


class MyTestCase(unittest.TestCase):
    # Dummy test for TravisCI
    def test_something(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
