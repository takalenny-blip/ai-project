import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import blog_work_state


def valid_state():
    return {
        "schema_version": 1,
        "proposal_id": "EXP-TEST",
        "status": "active",
        "current_stage": "interview",
        "current_position": {"summary": "interview completed"},
        "confirmed_timeline": ["origin", "automation"],
        "taka_statements": [{"text": "AIと一緒に考えるのが面白かった"}],
        "completed_interviews": [{"question": "何が面白かった？", "answer": "共同作業そのもの"}],
        "unresolved_items": ["記事の締め方"],
        "grounding": [{"kind": "experience_log", "path": "経験ログ/EXP-TEST.md"}],
        "state_changes": [{"before": "draft", "after": "collaboration"}],
        "operation_history": [{"action": "interview", "progress": True}],
        "save_boundary": {"direct_chat_path": "直チャット/example.md"},
    }


class BlogWorkStateTests(unittest.TestCase):
    def test_valid_state_is_accepted(self):
        blog_work_state.validate(valid_state())

    def test_completed_interview_is_required_as_persistent_state(self):
        state = valid_state()
        state["completed_interviews"] = []
        blog_work_state.validate(state)

    def test_missing_state_field_is_rejected(self):
        state = valid_state()
        del state["grounding"]
        with self.assertRaises(ValueError):
            blog_work_state.validate(state)

    def test_save_boundary_requires_direct_chat_path(self):
        state = valid_state()
        state["save_boundary"] = {}
        with self.assertRaises(ValueError):
            blog_work_state.validate(state)

    def test_invalid_status_is_rejected(self):
        state = valid_state()
        state["status"] = "unknown"
        with self.assertRaises(ValueError):
            blog_work_state.validate(state)

    def test_round_trip_preserves_interview_answer(self):
        state = valid_state()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            loaded = blog_work_state.load(path)
            self.assertEqual(
                loaded["completed_interviews"][0]["answer"],
                "共同作業そのもの",
            )


if __name__ == "__main__":
    unittest.main()
