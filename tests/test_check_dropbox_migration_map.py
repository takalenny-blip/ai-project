import unittest

from check_dropbox_migration_map import (
    REQUIRED_NO_REWORK_STATEMENTS,
    REQUIRED_PATHS,
    REQUIRED_SAFETY_STATEMENTS,
    validate_map,
    validate_no_002_rework,
    validate_design_status,
    validate_retired_queue_files,
    validate_retired_queue_manual,
    validate_roadmap_queue_guidance,
    validate_handoff_readme,
    validate_startup_reference_docs,
    validate_supporting_rule_docs,
)


class DropboxMigrationMapTests(unittest.TestCase):
    def test_valid_map_passes(self):
        content = "\n".join(
            [f"`{path}`" for path in REQUIRED_PATHS]
            + list(REQUIRED_SAFETY_STATEMENTS)
            + ["優先度1〜5、既定値3"]
        )
        self.assertEqual(validate_map(content), [])

    def test_retired_github_queue_files_must_be_absent(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(validate_retired_queue_files(root), [])
            (root / "scripts").mkdir()
            (root / "scripts" / "work_queue.py").write_text("# obsolete", encoding="utf-8")
            errors = validate_retired_queue_files(root)
            self.assertTrue(any("scripts/work_queue.py" in error for error in errors))

    def test_retired_queue_manual_passes_with_explicit_retirement_notice(self):
        content = """# 廃止済み：旧GitHub作業キュー管理マニュアル
状態：廃止。
現行手順として実行してはならない。
Dropbox固定ファイル `/ChatGPT/Dropbox作業管理統合ボード.xlsx`
作業候補の抽出・登録・状態更新には使用しない
"""
        self.assertEqual(validate_retired_queue_manual(content), [])

    def test_active_legacy_queue_instruction_is_rejected(self):
        content = """# 廃止済み：旧GitHub作業キュー管理マニュアル
現行手順として実行してはならない。
Dropbox固定ファイル `/ChatGPT/Dropbox作業管理統合ボード.xlsx`
作業候補の抽出・登録・状態更新には使用しない
現在の作業キューの正本は `docs/現在状態.json` の `work_items`
"""
        errors = validate_retired_queue_manual(content)
        self.assertTrue(any("obsolete active GitHub queue instruction remains" in error for error in errors))

    def test_roadmap_uses_dropbox_for_daily_queue(self):
        content = """日常作業キュー・作業候補・優先度・次のアクションの唯一の正本はDropbox固定ボード
バドが独断で作業候補を選び直したり、ボード上の優先順位を変更したりしない
技術状態・履歴・証拠の正本は `docs/現在状態.json`
"""
        self.assertEqual(validate_roadmap_queue_guidance(content), [])

    def test_obsolete_bud_as_queue_instruction_is_rejected(self):
        content = """日常作業キュー・作業候補・優先度・次のアクションの唯一の正本はDropbox固定ボード
バドが独断で作業候補を選び直したり、ボード上の優先順位を変更したりしない
技術状態・履歴・証拠の正本は `docs/現在状態.json`
現在の事実・現在の次の一手の正本は `BUD.md`
"""
        errors = validate_roadmap_queue_guidance(content)
        self.assertTrue(any("obsolete roadmap queue instruction remains" in error for error in errors))

    def test_handoff_readme_uses_current_state_then_dropbox_queue(self):
        content = """1. `docs/現在状態.json` — 技術状態・履歴・証拠を確認する。
2. Dropbox `/ChatGPT/Dropbox作業管理統合ボード.xlsx` — 日常作業の候補・状態・優先度・次のアクションを確認する。
これらから作業候補を選ばない。
日常作業の未着手項目・優先順位・次のアクションはDropbox固定ボードで管理
"""
        self.assertEqual(validate_handoff_readme(content), [])

    def test_obsolete_handoff_first_workflow_is_rejected(self):
        content = """1. `docs/現在状態.json` — 技術状態・履歴・証拠を確認する。
2. Dropbox `/ChatGPT/Dropbox作業管理統合ボード.xlsx` — 日常作業の候補・状態・優先度・次のアクションを確認する。
これらから作業候補を選ばない。
日常作業の未着手項目・優先順位・次のアクションはDropbox固定ボードで管理
1. `BUD.md`
"""
        errors = validate_handoff_readme(content)
        self.assertTrue(any("obsolete handoff queue instruction remains" in error for error in errors))

    def test_startup_docs_use_dropbox_as_daily_queue(self):
        master = """docs/現在状態.json
Dropbox固定ボード `/ChatGPT/Dropbox作業管理統合ボード.xlsx`
日常作業キューの正本ではない"""
        canonical = """docs/現在状態.json
Dropbox固定ボード `/ChatGPT/Dropbox作業管理統合ボード.xlsx`
日常作業キューの正本"""
        self.assertEqual(validate_startup_reference_docs(master, canonical), [])

    def test_stale_bud_first_startup_instruction_is_rejected(self):
        master = """docs/現在状態.json
Dropbox固定ボード `/ChatGPT/Dropbox作業管理統合ボード.xlsx`
日常作業キューの正本ではない
現在の読解基準は `BUD.md`"""
        canonical = """docs/現在状態.json
Dropbox固定ボード `/ChatGPT/Dropbox作業管理統合ボード.xlsx`
日常作業キューの正本"""
        errors = validate_startup_reference_docs(master, canonical)
        self.assertTrue(any("obsolete BUD-first startup instruction remains" in error for error in errors))

    def test_supporting_rules_keep_dropbox_as_daily_queue(self):
        rules = """日常作業キュー・優先度・状態・次のアクションの唯一の正本"""
        currentization = """技術状態・履歴・証拠の正本は `docs/現在状態.json`
日常作業キューの変更はDropbox固定ボードへ反映"""
        resume = """BUD・引き継ぎ・過去ログから作業候補を補完しない
Dropbox固定ボードで確認する"""
        bud_manual = """日常作業キューの管理・作業候補の選択・優先度・次のアクションの決定には使わない
日常作業キューの唯一の正本はDropbox固定ボード"""
        note_design = """日常作業キュー・候補・優先度・状態・次のアクションはDropbox固定ボード
旧 `work_items` / `next_step`、BUD、引き継ぎ、会話履歴から復元しない"""
        self.assertEqual(validate_supporting_rule_docs(rules, currentization, resume, bud_manual, note_design), [])

    def test_legacy_bud_queue_rule_is_rejected(self):
        rules = """日常作業キュー・優先度・状態・次のアクションの唯一の正本
- `BUD.md`：現在の目的・現在状態・現在の次の一手"""
        currentization = """技術状態・履歴・証拠の正本は `docs/現在状態.json`
日常作業キューの変更はDropbox固定ボードへ反映"""
        resume = """BUD・引き継ぎ・過去ログから作業候補を補完しない
Dropbox固定ボードで確認する"""
        bud_manual = """日常作業キューの管理・作業候補の選択・優先度・次のアクションの決定には使わない
日常作業キューの唯一の正本はDropbox固定ボード"""
        note_design = """日常作業キュー・候補・優先度・状態・次のアクションはDropbox固定ボード
旧 `work_items` / `next_step`、BUD、引き継ぎ、会話履歴から復元しない"""
        errors = validate_supporting_rule_docs(rules, currentization, resume, bud_manual, note_design)
        self.assertTrue(any("retains obsolete queue instruction" in error for error in errors))

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
