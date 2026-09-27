import unittest

from go_test_timings import format_summary


class GoTestTimingsTest(unittest.TestCase):
    def test_timeout_names_unfinished_tests_without_blame(self):
        events = [
            '{"Time":"2026-09-27T12:00:00Z","Action":"run","Package":"pkg","Test":"TestFast"}\n',
            '{"Time":"2026-09-27T12:00:01Z","Action":"pass","Package":"pkg","Test":"TestFast","Elapsed":1.0}\n',
            '{"Time":"2026-09-27T12:00:02Z","Action":"run","Package":"pkg","Test":"TestWaiting"}\n',
            'panic: test timed out after 10m0s\n',
            '{"Time":"2026-09-27T12:00:05Z","Action":"fail","Package":"pkg","Elapsed":5.0}\n',
        ]
        summary = format_summary(events)
        self.assertIn("1.00s pkg TestFast", summary)
        self.assertIn("Failed tests/packages: pkg", summary)
        self.assertIn("3.0s pkg TestWaiting", summary)
        self.assertIn("not necessarily the cause", summary)

    def test_skips_finished_subtests_and_reports_slowest(self):
        events = [
            '{"Action":"run","Package":"pkg","Test":"TestParent"}\n',
            '{"Action":"run","Package":"pkg","Test":"TestParent/child"}\n',
            '{"Action":"pass","Package":"pkg","Test":"TestParent/child","Elapsed":2.0}\n',
            '{"Action":"pass","Package":"pkg","Test":"TestParent","Elapsed":3.0}\n',
        ]
        summary = format_summary(events)
        self.assertLess(summary.index("3.00s pkg TestParent\n"), summary.index("2.00s pkg TestParent/child"))
        self.assertNotIn("Still running", summary)


if __name__ == "__main__":
    unittest.main()
