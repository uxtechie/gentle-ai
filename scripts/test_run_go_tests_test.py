import unittest

from run_go_tests import check_cli_coverage


class GoTestPartitionTest(unittest.TestCase):
    def test_each_cli_group_covers_tests_once(self):
        self.assertEqual(check_cli_coverage("TestAlpha\nTestNegotiated\nTestReview\nTestStatus\n"), 4)

    def test_new_test_shape_or_example_fails_closed(self):
        for listing in ("TestAlpha\nExampleReview\n", "TestReview\nTest_unmatched\n", ""):
            with self.subTest(listing=listing), self.assertRaises(ValueError):
                check_cli_coverage(listing)


if __name__ == "__main__":
    unittest.main()
