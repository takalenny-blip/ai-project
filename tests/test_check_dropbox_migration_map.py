import unittest

from check_dropbox_migration_map import (
    REQUIRED_NO_REWORK_STATEMENTS,
    REQUIRED_PATHS,
    REQUIRED_SAFETY_STATEMENTS,
    validate_map,
    validate_no_002_rework,
    validate_design_status,
)


class DropboxMigrationMapTests(unittest.TestCase):
    def test_valid_map_passes(self):
        content = "\n".join(
            [f"`{path}`" for path in REQUIRED_PATHS]
            + list(REQUIRED_SAFETY_STATEMENTS)
            + ["優先度1〜5、既定値3"]
        )
        self.assertEqual(validate_map(content), [])

    def test_missing_dependency_is_reported(self):
        content = "\n".join(
            [f"`{path}`" for path in REQUIRED_PATHS if path != "scripts/resume_check.py"]
            + list(REQUIRED_SAFETY_STATEMENTS)
            + ["優先度は1〜5の数値で管理し、既定値は3"]
        )
        errors = validate_map(content)
        self.assertTrue(any("scripts/resume_check.py" in error for error in errors))

    def test_missing_original_protection_is_reported(self):
        content = "\n".join(
            [f"`{path}`" for path in REQUIRED_PATHS]
            + [s for s in REQUIRED_SAFETY_STATEMENTS if "直チャット原本" not in s]
            + ["優先度は1〜5の数値で管理し、既定値は3"]
        )
        errors = validate_map(content)
        self.assertTrue(any("直チャット原本" in error for error in errors))

    def test_priority_default_must_match_board(self):
        content = "\n".join(
            [f"`{path}`" for path in REQUIRED_PATHS]
            + list(REQUIRED_SAFETY_STATEMENTS)
            + ["優先度は未指定"]
        )
        errors = validate_map(content)
        self.assertTrue(any("priority range 1-5" in error for error in errors))

    def test_002_no_rework_guard_passes(self):
        content = "\n".join(REQUIRED_NO_REWORK_STATEMENTS)
        self.assertEqual(validate_no_002_rework(content), [])

    def test_missing_002_no_rework_rule_is_reported(self):
        content = "\n".join(
            statement for statement in REQUIRED_NO_REWORK_STATEMENTS
            if statement != "再開・再検証・再実行しない"
        )
        errors = validate_no_002_rework(content)
        self.assertTrue(any("再開・再検証・再実行しない" in error for error in errors))



class MigrationDesignStatusTests(unittest.TestCase):
    def test_current_design_and_completed_board_check_are_required(self):
        content = "PR #1119は2026-10-16にマージ済み\\n項目002は完了扱い。再実施しない。\\n`/ChatGPT/Dropbox作業管理統合ボード.xlsx`"
        self.assertEqual(validate_design_status(content), [])

    def test_stale_design_that_reopens_item_002_fails(self):
        content = "PR #1119は2026-10-16にマージ済み\\n項目002は完了扱い。\\n`/ChatGPT/Dropbox作業管理統合ボード.xlsx`"
        errors = validate_design_status(content)
        self.assertTrue(any("再実施しない" in error for error in errors))

    def test_missing_merged_pr_evidence_fails(self):
        content = "項目002は完了扱い。再実施しない。\\n`/ChatGPT/Dropbox作業管理統合ボード.xlsx`"
        errors = validate_design_status(content)
        self.assertTrue(any("PR #1119" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
