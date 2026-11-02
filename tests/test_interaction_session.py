import json, tempfile, unittest, zipfile
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import interaction_session as session

class InteractionSessionTests(unittest.TestCase):
    def write_board(self, path, marker="one"):
        with zipfile.ZipFile(path, "w") as workbook:
            workbook.writestr("[Content_Types].xml", "<Types></Types>")
            workbook.writestr("xl/workbook.xml", "<workbook></workbook>")
            workbook.writestr("xl/marker.txt", marker)

    def test_first_turn_records_rules_and_board_fingerprint(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); rules=ROOT/"rules"/"運用ルール.md"; board=root/"board.xlsx"; self.write_board(board)
            history=root/"private"/"history.json"
            fingerprint=session.record_turn(rules,history,board_path=board)
            self.assertTrue(fingerprint)
            self.assertEqual(json.loads(history.read_text(encoding="utf-8")),[{"state_fingerprint":fingerprint}])

    def test_repeated_state_stops_without_append(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); rules=ROOT/"rules"/"運用ルール.md"; board=root/"board.xlsx"; self.write_board(board)
            history=root/"history.json"; session.record_turn(rules,history,board_path=board)
            before=history.read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"identical structured work state"):
                session.record_turn(rules,history,board_path=board)
            self.assertEqual(history.read_text(encoding="utf-8"),before)

    def test_board_change_is_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); rules=ROOT/"rules"/"運用ルール.md"; board=root/"board.xlsx"; self.write_board(board,"draft")
            history=root/"history.json"; session.record_turn(rules,history,board_path=board)
            self.write_board(board,"done"); session.record_turn(rules,history,board_path=board)
            self.assertEqual(len(json.loads(history.read_text(encoding="utf-8"))),2)

    def test_missing_board_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(ValueError,"missing or unavailable"):
                session.record_turn(ROOT/"rules"/"運用ルール.md",root/"history.json",board_path=root/"missing.xlsx")

if __name__ == "__main__":
    unittest.main()
