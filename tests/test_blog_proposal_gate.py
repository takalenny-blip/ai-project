import unittest
from scripts.blog_proposal_gate import check

class T(unittest.TestCase):
    def test_pending_blocks_payload(self):
        r=check({"review":{"decision":"pending"}})
        self.assertFalse(r["payload_ready"])
        self.assertIsNotNone(r["blocked_reason"])

    def test_approved_allows_payload(self):
        r=check({"review":{"decision":"approved"}})
        self.assertTrue(r["payload_ready"])
        self.assertIsNone(r["blocked_reason"])

if __name__ == "__main__":
    unittest.main()
