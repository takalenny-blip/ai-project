#!/usr/bin/env python3
"""Generate deterministic candidate current-state views.

This first implementation is intentionally side-effect free. During the
migration period it renders candidate BUD/handover files without replacing
the existing hand-maintained views.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs" / "現在状態.json"


def load_state() -> dict:
    with STATE.open(encoding="utf-8") as f:
        return json.load(f)


def render(state: dict) -> tuple[str, str]:
    dc = state["direct_chat"]
    surgery = state["surgery"]
    model = state["current_state_model"]
    migration = state["migration"]

    bud = f'''# BUD — バドのための最上位ダッシュボード\n\n更新日：{state["updated"]}\n\n## 正本\n\n- 正本リポジトリ：`{state["canonical_repository"]}`\n- 現在状態正本：`docs/現在状態.json`\n- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md\n\n## 現在の作業レーン\n\n**{state["primary_lane"]}**\n\n「一括改修」は設計を一括で行う意味であり、実装は小さな検証単位で進める。\n\n順序：**現状棚卸し → 大手術の設計 → 採用する改善を確定 → 小さな検証単位で順次実装 → 検証**。\n\n- 棚卸し：{surgery["inventory"]}\n- 設計：{surgery["design"]}\n- 採用：{surgery["adoption"]}\n- 実装：{surgery["bulk_refactor"]}\n- 検証：{surgery["verification"]}\n\n## 現在状態モデル\n\n- {model["target"]}\n- 自動生成：{model["generation_flow"]}\n\n## 直チャット\n\n- 最新保存：**{dc["latest_saved"]}**\n- 最新パス：`{dc["latest_path"]}`\n- 旧連番保存：{dc["legacy_serial_files_preserved"]}\n- 新タイムスタンプ方式：{dc["new_timestamp_naming_allowed"]}\n\n## 移行\n\n- 状態：{migration["status"]}\n- 通常工程：{migration["normal_work_policy"]}\n- 暫定同期：{migration["temporary_manual_sync"]}\n\n## 次の一手\n\n**{surgery["next_design_item"]}**\n'''

    handover = f'''# 現在の引き継ぎ\n\n更新日：{state["updated"]}\n\n## 正本\n\n- `{state["canonical_repository"]}`\n- 現在状態の唯一の正本：`docs/現在状態.json`\n- このファイルは生成ビュー。\n\n## 現在の作業レーン\n\n**{state["primary_lane"]}**\n\n「一括改修」＝設計を一括、実装を小さな検証単位。\n\n## 現在状態\n\n- 目的：{model["target"]}\n- 自動生成状態：{model["status"]}\n- 生成フロー：{model["generation_flow"]}\n\n## 直チャット\n\n- 最新：**{dc["latest_saved"]}**\n- 実体：`{dc["latest_path"]}`\n\n## 移行\n\n- {migration["normal_work_policy"]}\n- {migration["temporary_manual_sync"]}\n\n## 次の一手\n\n**{surgery["next_design_item"]}**\n'''
    return bud, handover


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--check-deterministic", action="store_true")
    args = parser.parse_args()

    bud, handover = render(load_state())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    bud_path = args.out_dir / "BUD.md"
    handover_path = args.out_dir / "現在の引き継ぎ.md"
    bud_path.write_text(bud, encoding="utf-8")
    handover_path.write_text(handover, encoding="utf-8")

    if args.check_deterministic:
        bud2, handover2 = render(load_state())
        if (bud, handover) != (bud2, handover2):
            print("FAIL: render is not deterministic")
            return 1
        print("OK: deterministic render")
    else:
        print(f"OK: rendered {bud_path}")
        print(f"OK: rendered {handover_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
