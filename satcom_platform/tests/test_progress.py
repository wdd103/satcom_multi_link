import unittest
from unittest.mock import Mock

from satcom_platform.simulation.progress import RunProgress


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.status = {"state": "RUNNING", "run_id": "test-run"}
        self.persist = Mock()
        self.now = 0.0
        self.progress = RunProgress(self.status, self.persist, clock=lambda: self.now)

    def test_real_counts_throttle_and_completion(self):
        self.progress.stage("COMMUNICATIONS", 100)
        self.progress.update(10, "U1 / SAT1")
        self.assertEqual(self.persist.call_count, 1)
        self.now = 1.1
        self.progress.update(20, "U1 / SAT2")
        self.assertEqual(self.persist.call_count, 2)
        self.assertEqual(self.status["progress"]["completed"], 20)
        self.assertEqual(self.status["progress"]["percent"], 61)
        self.progress.update(100)
        self.assertEqual(self.status["progress"]["percent"], 85)
        self.progress.stage("EXPORTING", 3)
        self.progress.update(3)
        self.assertEqual(self.status["progress"]["percent"], 99)
        self.progress.complete()
        self.assertEqual(self.status["progress"]["percent"], 100)
        self.assertEqual(self.status["state"], "COMPLETE")

    def test_failure_keeps_last_progress_and_reports_error(self):
        root = Mock()
        self.progress.stage("COMPUTING", 10)
        self.progress.attach_stk(root)
        self.progress.update(5, force=True)
        percent = self.status["progress"]["percent"]
        self.progress.fail('Cannot compute "SAT1"\nprovider')
        self.assertEqual(self.status["state"], "FAILED")
        self.assertEqual(self.status["progress"]["percent"], percent)
        self.assertEqual(self.status["progress"]["label"], "运行失败")
        command = root.ExecuteCommand.call_args.args[0]
        self.assertTrue(command.startswith('Message / 4 "'))
        self.assertNotIn("\n", command)
        self.assertIn("'SAT1'", command)

    def test_stk_display_failure_still_persists_web_progress(self):
        self.progress.stage("BUILDING", 2)
        root = Mock()
        root.ExecuteCommand.side_effect = RuntimeError("Message Viewer unavailable")
        self.progress.attach_stk(root)
        self.progress.update(1, "SAT1", force=True)
        self.assertIn("unavailable", self.status["stk_progress_error"])
        self.assertEqual(self.status["progress"]["completed"], 1)
        self.assertEqual(self.status["state"], "RUNNING")
        self.assertEqual(self.persist.call_count, 3)


if __name__ == "__main__":
    unittest.main()
