import unittest

from scripts.check_save_backlog import blocking_prs


class SaveBacklogTests(unittest.TestCase):
    def test_no_open_save_pr_allows_intake(self):
        self.assertEqual(blocking_prs([]), [])

    def test_open_direct_chat_save_pr_blocks_intake(self):
        prs = [{"number": 12, "headRefName": "save/direct-chat-12", "state": "OPEN"}]
        self.assertEqual(blocking_prs(prs), prs)

    def test_open_currentize_pr_blocks_intake(self):
        prs = [{"number": 13, "headRefName": "save/currentize-13", "state": "OPEN"}]
        self.assertEqual(blocking_prs(prs), prs)

    def test_closed_save_pr_does_not_block_intake(self):
        prs = [{"number": 14, "headRefName": "save/direct-chat-14", "state": "CLOSED"}]
        self.assertEqual(blocking_prs(prs), [])

    def test_unrelated_open_pr_does_not_block_intake(self):
        prs = [{"number": 15, "headRefName": "work/docs-update", "state": "OPEN"}]
        self.assertEqual(blocking_prs(prs), [])

    def test_open_save_pr_beyond_default_page_is_detected(self):
        prs = [
            {"number": index, "headRefName": f"work/unrelated-{index}", "state": "OPEN"}
            for index in range(1, 65)
        ]
        stale = {"number": 999, "headRefName": "save/direct-chat-old", "state": "OPEN"}
        prs.append(stale)
        self.assertEqual(blocking_prs(prs), [stale])

if __name__ == "__main__":
    unittest.main()
