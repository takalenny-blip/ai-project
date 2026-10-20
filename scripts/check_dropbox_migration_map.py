#!/usr/bin/env python3
"""Validate the Dropbox migration dependency map and safety-critical guards."""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "docs" / "計画" / "Dropbox作業管理依存関係対応表_20261016.md"
DESIGN_PATH = ROOT / "docs" / "計画" / "Dropbox作業管理移行設計.md"
NO_REWORK_GUARD_PATH = ROOT / "docs" / "計画" / "Dropbox作業管理002再作業禁止ガード.md"
RETIRED_QUEUE_MANUAL_PATH = ROOT / "docs" / "作業キュー管理マニュアル.md"

REQUIRED_PATHS = (
    "README.md",
    "docs/AI_READ_MAP.md",
    "rules/README.md",
    "rules/運用ルール.md",
    "scripts/check_dropbox_migration_map.py",
    "scripts/generate_current_views.py",
    "scripts/current_state_guard.py",
    "scripts/resume_check.py",
    "scripts/check_entry_docs.py",
    "scripts/check_canonical_state_change.py",
    ".github/workflows/current-state-guard.yml",
    ".github/workflows/current-state-views.yml",
    "scripts/check_direct_chat_immutability.py",
    "tests/test_check_direct_chat_immutability.py",
    "BUD.md",
    "docs/引き継ぎ/現在の引き継ぎ.md",
    "docs/現在状態.json",
)

REQUIRED_SAFETY_STATEMENTS = (
    "既存の直チャット原本は変更・削除・改名・上書き・置換しない",
    "既存ボード",
    "上書き",
    "切替完了とは宣言しない",
    "PR #1102",
    "PR #1116",
    "PR #1118",
    "コールドスタート",
)

REQUIRED_NO_REWORK_STATEMENTS = (
    "項目002",
    "再開・再検証・再実行しない",
    "002は完了・再作業禁止",
    "項目003以降",
)


def validate_retired_queue_files(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative in ("scripts/work_queue.py", "tests/test_work_queue.py"):
        if (root / relative).exists():
            errors.append(f"retired GitHub queue file still exists: {relative}")
    return errors


def validate_retired_queue_manual(text: str) -> list[str]:
    """Prevent the obsolete GitHub queue manual from becoming an active instruction again."""
    errors: list[str] = []
    required = (
        "# 廃止済み：旧GitHub作業キュー管理マニュアル",
        "現行手順として実行してはならない",
        "Dropbox固定ファイル `/ChatGPT/Dropbox作業管理統合ボード.xlsx`",
        "作業候補の抽出・登録・状態更新には使用しない",
    )
    for statement in required:
        if statement not in text:
            errors.append(f"retired GitHub queue manual missing retirement boundary: {statement}")
    obsolete_active_instructions = (
        "現在の作業キューの正本は `docs/現在状態.json` の `work_items`",
        "work_items の現在の一覧を見る",
        "その場でwork_itemsへ登録",
    )
    for statement in obsolete_active_instructions:
        if statement in text:
            errors.append(f"obsolete active GitHub queue instruction remains: {statement}")
    return errors

def validate_roadmap_queue_guidance(text: str) -> list[str]:
    """Ensure the roadmap does not restore BUD as the daily queue or let the AI choose tasks unilaterally."""
    errors: list[str] = []
    required = (
        "日常作業キュー・作業候補・優先度・次のアクションの唯一の正本はDropbox固定ボード",
        "バドが独断で作業候補を選び直したり、ボード上の優先順位を変更したりしない",
        "技術状態・履歴・証拠の正本は `docs/現在状態.json`",
    )
    for statement in required:
        if statement not in text:
            errors.append(f"roadmap missing current queue boundary: {statement}")
    obsolete_instructions = (
        "現在の事実・現在の次の一手の正本は `BUD.md`",
        "バドが次の作業レーンを選び",
        "現在の事実が変わった場合はまずBUDを更新する",
    )
    for statement in obsolete_instructions:
        if statement in text:
            errors.append(f"obsolete roadmap queue instruction remains: {statement}")
    return errors

def validate_handoff_readme(text: str) -> list[str]:
    """Keep session handoff guidance from restoring the retired BUD-first queue workflow."""
    errors: list[str] = []
    required = (
        "1. `docs/現在状態.json` — 技術状態・履歴・証拠を確認する。",
        "2. Dropbox `/ChatGPT/Dropbox作業管理統合ボード.xlsx` — 日常作業の候補・状態・優先度・次のアクションを確認する。",
        "これらから作業候補を選ばない。",
        "日常作業の未着手項目・優先順位・次のアクションはDropbox固定ボードで管理",
    )
    for statement in required:
        if statement not in text:
            errors.append(f"handoff README missing current queue boundary: {statement}")
    obsolete_instructions = (
        "1. `BUD.md`",
        "docs/00_CURRENT_STATE.md",
        "必ず `docs/引き継ぎ/現在の引き継ぎ.md` を更新し",
    )
    for statement in obsolete_instructions:
        if statement in text:
            errors.append(f"obsolete handoff queue instruction remains: {statement}")
    return errors

def validate_startup_reference_docs(master_plan: str, canonical_repo: str) -> list[str]:
    """Prevent stale BUD-first startup instructions from reviving the retired queue."""
    errors: list[str] = []
    for name, text in (("master plan", master_plan), ("canonical repository guide", canonical_repo)):
        required = (
            "docs/現在状態.json",
            "Dropbox固定ボード `/ChatGPT/Dropbox作業管理統合ボード.xlsx`",
            "日常作業キュー",
        )
        for statement in required:
            if statement not in text:
                errors.append(f"{name} missing current startup boundary: {statement}")
    obsolete = (
        "現在の読解基準は `BUD.md`",
        "通常開始時は、このリポジトリの次の2ファイルを最初に確認する。",
        "1. `BUD.md`\\n2. `rules/運用ルール.md`",
    )
    for statement in obsolete:
        if statement in master_plan or statement in canonical_repo:
            errors.append(f"obsolete BUD-first startup instruction remains: {statement}")
    return errors

def validate_bud_manual_retirement(text: str) -> list[str]:
    """Require explicit retirement labels on any BUD/handoff-as-canonical update instruction."""
    errors: list[str] = []
    obsolete_instruction = re.compile(
        r"(?:BUD\\.md|docs/引き継ぎ/現在の引き継ぎ\\.md).*現在状態.*正本.*更新"
    )
    for line_number, line in enumerate(text.splitlines(), start=1):
        if obsolete_instruction.search(line) and "禁止・旧手順：実行不可" not in line:
            errors.append(
                "BUD maintenance manual contains an unretired canonical-view update "
                f"instruction at line {line_number}: {line.strip()}"
            )
    return errors


def validate_supporting_rule_docs(rules_readme: str, currentization_guard: str, resume_guard: str, bud_manual: str, note_design: str, migration_design: str) -> list[str]:
    """Ensure supporting rule indexes and guards do not restore BUD as the task queue."""
    errors: list[str] = []
    requirements = (
        ("rules README", rules_readme, "日常作業キュー・優先度・状態・次のアクションの唯一の正本"),
        ("currentization guard", currentization_guard, "技術状態・履歴・証拠の正本は `docs/現在状態.json`"),
        ("currentization guard", currentization_guard, "日常作業キューの変更はDropbox固定ボードへ反映"),
        ("resume/search guard", resume_guard, "BUD・引き継ぎ・過去ログから作業候補を補完しない"),
        ("resume/search guard", resume_guard, "Dropbox固定ボードで確認する"),
        ("BUD maintenance manual", bud_manual, "日常作業キューの管理・作業候補の選択・優先度・次のアクションの決定には使わない"),
        ("BUD maintenance manual", bud_manual, "日常作業キューの唯一の正本はDropbox固定ボード"),
        ("Note operating design", note_design, "日常作業キュー・候補・優先度・状態・次のアクションはDropbox固定ボード"),
        ("Note operating design", note_design, "旧 `work_items` / `next_step`、BUD、引き継ぎ、会話履歴から復元しない"),
        ("migration design", migration_design, "本書は現在の作業キューや実行手順ではなく"),
        ("migration design", migration_design, "ここに列挙されたPhase・タスクを現在の指示としてそのまま実行しない"),
    )
    for name, text, statement in requirements:
        if statement not in text:
            errors.append(f"{name} missing retired-queue boundary: {statement}")
    errors.extend(validate_bud_manual_retirement(bud_manual))
    obsolete = (
        ("rules README", rules_readme, "- `BUD.md`：現在の目的・現在状態・現在の次の一手"),
        ("resume/search guard", resume_guard, "`BUD.md`、最新の引き継ぎ、実際の直近ユーザー発言で確認済みとされている事実"),
        ("Note operating design", note_design, "現在状態は `docs/現在状態.json` の `work_items` を正本とする。"),
        ("Note operating design", note_design, "`docs/現在状態.json` の `work_items` を作業キューの正本とし"),
    )
    for name, text, statement in obsolete:
        if statement in text:
            errors.append(f"{name} retains obsolete queue instruction: {statement}")
    return errors

def validate_map(text: str) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_PATHS:
        if f"`{path}`" not in text:
            errors.append(f"dependency map missing required path: {path}")
    for statement in REQUIRED_SAFETY_STATEMENTS:
        if statement not in text:
            errors.append(f"dependency map missing safety/evidence statement: {statement}")
    if "優先度1〜5" not in text or "既定値3" not in text:
        errors.append("dependency map must reflect the board's priority range 1-5 and default 3")
    return errors


def validate_no_002_rework(text: str) -> list[str]:
    errors: list[str] = []
    for statement in REQUIRED_NO_REWORK_STATEMENTS:
        if statement not in text:
            errors.append(f"002 no-rework guard missing required rule: {statement}")
    return errors


def validate_design_status(text: str) -> list[str]:
    """Keep the design aligned with the completed board check and merged dependency-map PR."""
    errors: list[str] = []
    required = (
        "PR #1119は2026-10-16にマージ済み",
        "項目002は完了扱い",
        "再実施しない",
        "`/ChatGPT/Dropbox作業管理統合ボード.xlsx`",
    )
    for statement in required:
        if statement not in text:
            errors.append(f"migration design missing current-state/no-rework statement: {statement}")
    return errors


def main() -> int:
    try:
        text = MAP_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: cannot read dependency map: {exc}", file=sys.stderr)
        return 1
    errors = validate_map(text)
    errors.extend(validate_retired_queue_files())
    try:
        rules_readme_text = (ROOT / "rules" / "README.md").read_text(encoding="utf-8")
        currentization_guard_text = (ROOT / "rules" / "現在化・旧情報ガード.md").read_text(encoding="utf-8")
        resume_guard_text = (ROOT / "rules" / "再開・検索ガード.md").read_text(encoding="utf-8")
        bud_manual_text = (ROOT / "docs" / "BUD二重管理解消・運用マニュアル.md").read_text(encoding="utf-8")
        note_design_text = (ROOT / "docs" / "企画" / "Noteマニュアル群_企画制作公開運用設計.md").read_text(encoding="utf-8")
        migration_design_text = (ROOT / "docs" / "計画" / "Dropbox作業管理移行設計.md").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read supporting rule docs: {exc}")
    else:
        errors.extend(validate_supporting_rule_docs(rules_readme_text, currentization_guard_text, resume_guard_text, bud_manual_text, note_design_text, migration_design_text))
    try:
        master_plan_text = (ROOT / "docs" / "マスタープラン.md").read_text(encoding="utf-8")
        canonical_repo_text = (ROOT / "docs" / "正本リポジトリ.md").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read startup reference docs: {exc}")
    else:
        errors.extend(validate_startup_reference_docs(master_plan_text, canonical_repo_text))
    handoff_readme_path = ROOT / "docs" / "引き継ぎ" / "README.md"
    try:
        handoff_readme_text = handoff_readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read handoff README: {exc}")
    else:
        errors.extend(validate_handoff_readme(handoff_readme_text))
    roadmap_path = ROOT / "docs" / "全体進行設計図.md"
    try:
        roadmap_text = roadmap_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read roadmap queue guidance: {exc}")
    else:
        errors.extend(validate_roadmap_queue_guidance(roadmap_text))
    try:
        retired_manual_text = RETIRED_QUEUE_MANUAL_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read retired GitHub queue manual: {exc}")
    else:
        errors.extend(validate_retired_queue_manual(retired_manual_text))
    try:
        design_text = DESIGN_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read Dropbox migration design: {exc}")
    else:
        errors.extend(validate_design_status(design_text))
    try:
        guard_text = NO_REWORK_GUARD_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read 002 no-rework guard: {exc}")
    else:
        errors.extend(validate_no_002_rework(guard_text))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: dependency map and 002 no-rework guard cover required safety boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
