import os
import unittest

from unittest.mock import patch

from run_go_tests import check_cli_coverage, test_environment


class GoTestPartitionTest(unittest.TestCase):
    def test_each_cli_group_covers_tests_once(self):
        self.assertEqual(check_cli_coverage("TestAlpha\nTestNegotiated\nTestReview\nTestStatus\n"), 4)

    def test_new_test_shape_or_example_fails_closed(self):
        for listing in ("TestAlpha\nExampleReview\n", "TestReview\nTest_unmatched\n", ""):
            with self.subTest(listing=listing), self.assertRaises(ValueError):
                check_cli_coverage(listing)

    def test_child_config_is_isolated_without_changing_parent(self):
        with patch.dict("os.environ", {
            "XDG_CONFIG_HOME": "/real/config",
            "OPENCODE_CONFIG_DIR": "/real/opencode",
            "OPENCODE_CONFIG": "/real/opencode.json",
            "PI_CODING_AGENT_DIR": "/real/pi",
        }):
            child = test_environment("/temporary/config")
            self.assertEqual(child["XDG_CONFIG_HOME"], "/temporary/config")
            self.assertNotIn("OPENCODE_CONFIG_DIR", child)
            self.assertNotIn("OPENCODE_CONFIG", child)
            self.assertNotIn("PI_CODING_AGENT_DIR", child)
            self.assertEqual(os.environ["XDG_CONFIG_HOME"], "/real/config")


if __name__ == "__main__":
    unittest.main()
