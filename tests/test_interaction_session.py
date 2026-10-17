import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import interaction_session as session


class InteractionSessionTests(unittest.TestCase):
    def state(self):
        return {
            "execution_environment": {"active": "work_pc", "retired": ["vaio_p"]},
            "current_position": {"summary": "mutable prose"},
            "work_queue_source": "dropbox_board",
            "work_items": [],
        }

    def write_state(self, root, state):
        path = root / "state.json"
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        return path

    def write_board(self, path, content="board-state-1"):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")
            workbook.writestr("xl/board-state.json", json.dumps({"state": content}))

    def test_first_turn_records_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "private" / "history.json"
            fingerprint = session.record_turn(state, history, board_path=board)
            self.assertTrue(fingerprint)
            self.assertEqual(json.loads(history.read_text(encoding="utf-8")), [{"state_fingerprint": fingerprint}])

    def test_repeated_board_stops_and_does_not_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "history.json"
            session.record_turn(state, history, board_path=board)
            before = history.read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identical structured work state"):
                session.record_turn(state, history, board_path=board)
            self.assertEqual(history.read_text(encoding="utf-8"), before)

    def test_prose_only_change_does_not_change_board_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "history.json"
            session.record_turn(state, history, board_path=board)
            changed = self.state()
            changed["current_position"]["summary"] = "rewritten prose"
            state.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identical structured work state"):
                session.record_turn(state, history, board_path=board)

    def test_real_board_change_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board, "draft")
            history = root / "history.json"
            session.record_turn(state, history, board_path=board)
            self.write_board(board, "done")
            session.record_turn(state, history, board_path=board)
            self.assertEqual(len(json.loads(history.read_text(encoding="utf-8"))), 2)

    def test_legacy_queue_data_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_data = self.state()
            state_data["next_step"] = {"target": "old queue"}
            state = self.write_state(root, state_data)
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            with self.assertRaisesRegex(ValueError, "next_step field is retired"):
                session.record_turn(state, root / "history.json", board_path=board)

    def test_invalid_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = self.write_state(root, self.state())
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "history.json"
            history.write_text('{"not":"a list"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "history must be a JSON list"):
                session.record_turn(state, history, board_path=board)


if __name__ == "__main__":
    unittest.main()
