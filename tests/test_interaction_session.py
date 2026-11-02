import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import interaction_session as session


class InteractionSessionTests(unittest.TestCase):
    def write_board(self, path, content="board-state-1"):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")
            workbook.writestr("xl/board-state.json", json.dumps({"state": content}))

    def test_first_turn_records_board_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "private" / "history.json"
            fingerprint = session.record_turn(history, board_path=board)
            self.assertTrue(fingerprint)
            self.assertEqual(json.loads(history.read_text(encoding="utf-8")), [{"state_fingerprint": fingerprint}])

    def test_repeated_board_stops_and_does_not_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "history.json"
            session.record_turn(history, board_path=board)
            before = history.read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identical structured work state"):
                session.record_turn(history, board_path=board)
            self.assertEqual(history.read_text(encoding="utf-8"), before)

    def test_real_board_change_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board, "draft")
            history = root / "history.json"
            session.record_turn(history, board_path=board)
            self.write_board(board, "done")
            session.record_turn(history, board_path=board)
            self.assertEqual(len(json.loads(history.read_text(encoding="utf-8"))), 2)

    def test_invalid_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            board = root / "Dropbox作業管理統合ボード.xlsx"
            self.write_board(board)
            history = root / "history.json"
            history.write_text('{"not":"a list"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "history must be a JSON list"):
                session.record_turn(history, board_path=board)


if __name__ == "__main__":
    unittest.main()
