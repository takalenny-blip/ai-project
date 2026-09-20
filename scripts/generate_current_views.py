#!/usr/bin/env python3
"""Generate deterministic current-state views atomically."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
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
    env = state["execution_environment"]
    current = state["current_position"]
    nxt = state["next_step"]

    header = f"""更新日：{state["updated"]}

## 正本

- 正本リポジトリ：{state["canonical_repository"]}
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**{env["active"]}**
- 退役：{", ".join(env.get("retired", [])) or "(なし)"}
- work_pc clone：**{state.get("work_pc", {}).get("clone_status", "unknown")}**

## 現在地点

**{current["summary"]}**

## 次の一手

- 環境：**{nxt["environment"]}**
- 目的：**{nxt["target"]}**
- 根拠：{nxt["evidence"]}
- 状態：{nxt["status"]}
"""

    bud = f"""# BUD — バドのための最上位ダッシュボード

{header}

## 現在の作業レーン

**{state["primary_lane"]}**

「一括改修」は設計を一括で行う意味であり、実装は小さな検証単位で進める。

順序：**現状棚卸し → 大手術の設計 → 採用する改善を確定 → 小さな検証単位で順次実装 → 検証**。

- 棚卸し：{surgery["inventory"]}
- 設計：{surgery["design"]}
- 採用：{surgery["adoption"]}
- 実装：{surgery["bulk_refactor"]}
- 検証：{surgery["verification"]}

## 現在状態モデル

- {model["target"]}
- 自動生成：{model["generation_flow"]}

## 直チャット

- 最新保存：**{dc["latest_saved"]}**
- 最新パス：{dc["latest_path"]}
- 旧連番保存：{dc["legacy_serial_files_preserved"]}
- 新タイムスタンプ方式：{dc["new_timestamp_naming_allowed"]}

## 移行

- 状態：{migration["status"]}
- 通常工程：{migration["normal_work_policy"]}
- 暫定同期：{migration["temporary_manual_sync"]}
"""

    handover = f"""# 現在の引き継ぎ

{header}

## 現在の作業レーン

**{state["primary_lane"]}**

「一括改修」＝設計を一括、実装を小さな検証単位。

## 現在状態

- 目的：{model["target"]}
- 自動生成状態：{model["status"]}
- 生成フロー：{model["generation_flow"]}

## 直チャット

- 最新：**{dc["latest_saved"]}**
- 実体：{dc["latest_path"]}

## 移行

- {migration["normal_work_policy"]}
- {migration["temporary_manual_sync"]}
"""
    return bud.rstrip("\n"), handover.rstrip("\n")

def write_views_atomically(out_dir: Path, bud: str, handover: str) -> None:
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.", dir=out_dir.parent))
    try:
        (temp_dir / "BUD.md").write_text(bud, encoding="utf-8")
        (temp_dir / "現在の引き継ぎ.md").write_text(handover, encoding="utf-8")
        if out_dir.exists():
            shutil.rmtree(out_dir)
        temp_dir.rename(out_dir)
        temp_dir = None
    finally:
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--check-deterministic", action="store_true")
    args = parser.parse_args()

    bud, handover = render(load_state())
    write_views_atomically(args.out_dir, bud, handover)

    if args.check_deterministic:
        bud2, handover2 = render(load_state())
        if (bud, handover) != (bud2, handover2):
            print("FAIL: render is not deterministic")
            return 1
        print("OK: deterministic render")
    else:
        print(f"OK: rendered {args.out_dir / 'BUD.md'}")
        print(f"OK: rendered {args.out_dir / '現在の引き継ぎ.md'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
