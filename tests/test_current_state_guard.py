#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import current_state_guard as guard

class SingleSourceRulesGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "rules" / "運用ルール.md").read_text(encoding="utf-8")

    def test_current_operating_rules_pass(self):
        guard.validate_rules(self.text)

    def test_missing_single_source_contract_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing required current-state content"):
            guard.validate_rules(self.text.replace("現在状態・共通運用ルールの唯一の正本", "現在状態の参照先"))

    def test_wordpress_as_production_lane_is_rejected(self):
        bad = self.text + "\nWordPress本番公開を再開する。\n"
        with self.assertRaisesRegex(ValueError, "retired active instruction"):
            guard.validate_rules(bad)

    def test_vaio_as_active_environment_is_rejected(self):
        bad = self.text + "\nvaio_p は現行環境として使用する。\n"
        with self.assertRaisesRegex(ValueError, "retired active instruction"):
            guard.validate_rules(bad)

    def test_pending_external_proposal_requires_five_fields(self):
        bad = self.text.replace("状態：clear（未処理の外部提案なし）", "状態：pending")
        with self.assertRaisesRegex(ValueError, "pending external proposal status missing"):
            guard.validate_rules(bad)

    def test_direct_chat_record_requires_path_and_hash(self):
        bad = self.text.replace("- 内容SHA：", "- 内容ハッシュ：")
        with self.assertRaisesRegex(ValueError, "direct-chat save record missing 内容SHA"):
            guard.validate_rules(bad)

if __name__ == "__main__":
    unittest.main()
