import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import interaction_session as session


class InteractionSessionTests(unittest.TestCase):
    def state(self, step_status="in_progress"):
        return {
            "current_position": {"summary": "mutable prose"},
            "next_step": {"target": "mutable prose too"},
            "work_items": [{
                "id": "BLOG-0001",
                "status": "in_progress",
                "readiness": "ready",
                "execution_state": "actionable",
                "progress": {
                    "current_step": "draft",
                    "steps": [{"id": "draft", "status": step_status}],
                },
            }],
        }

    def write_state(self, root, state):
        path = root / "state.json"
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        return path

    def test_first_turn_records_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            history = root / "private" / "history.json"
            fingerprint = session.record_turn(state, history)
            self.assertTrue(fingerprint)
            self.assertEqual(json.loads(history.read_text(encoding="utf-8")), [
                {"state_fingerprint": fingerprint}
            ])

    def test_repeated_state_stops_and_does_not_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            history = root / "history.json"
            session.record_turn(state, history)
            before = history.read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identical structured work state"):
                session.record_turn(state, history)
            self.assertEqual(history.read_text(encoding="utf-8"), before)

    def test_prose_only_change_is_stopped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            history = root / "history.json"
            session.record_turn(state, history)
            changed = self.state()
            changed["current_position"]["summary"] = "rewritten prose"
            state.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                session.record_turn(state, history)

    def test_real_step_transition_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            history = root / "history.json"
            session.record_turn(state, history)
            state.write_text(json.dumps(self.state("done"), ensure_ascii=False), encoding="utf-8")
            session.record_turn(state, history)
            self.assertEqual(len(json.loads(history.read_text(encoding="utf-8"))), 2)

    def test_invalid_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            history = root / "history.json"
            history.write_text('{"not":"a list"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "history must be a JSON list"):
                session.record_turn(state, history)


if __name__ == "__main__":
    unittest.main()
