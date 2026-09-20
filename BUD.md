# BUD — バドのための最上位ダッシュボード

更新日：2026-09-20

## 正本

- 正本リポジトリ：takalenny-blip/ai-project
- 現在状態正本：docs/現在状態.json
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 実行環境

- 現在：**work_pc**
- 退役：vaio_p
- work_pc clone：**unverified**

## 現在地点

**退役済み環境を除外し、work_pcを現在の作業環境として再開基盤を整備済み。PR1・PR2・PR3はマージ済み。PR3のCIガードと直チャット保存経路のcanonical確認まで完了。**

## 次の一手

- 環境：**work_pc**
- 目的：**PR3完了後のcanonical現在状態を確認し、次の実装単位を決める**
- 根拠：docs/現在状態.json / scripts/current_state_guard.py / tests/test_current_state_guard.py / .github/workflows/current-state-guard.yml
- 状態：ready

## 現在の作業レーン

**DIGA / DiMORA自動化**

「一括改修」は設計を一括で行う意味であり、実装は小さな検証単位で進める。

順序：**現状棚卸し → 大手術の設計 → 採用する改善を確定 → 小さな検証単位で順次実装 → 検証**。

- 棚卸し：complete
- 設計：revised_complete
- 採用：complete
- 実装：current_views_migrated_ci_guard_added
- 検証：done

## 現在状態モデル

- docs/現在状態.jsonを唯一の現在状態正本とし、BUD.mdとdocs/引き継ぎ/現在の引き継ぎ.mdを生成ビューにする
- 自動生成：第1実装済み。scripts/generate_current_views.pyが候補ビューを決定的に生成し、GitHub Actionsで決定性と完全一致を検証する。

## 直チャット

- 最新保存：**2026-09-20T14-11-30.979062+0900**
- 最新パス：直チャット/2026-09-20_直チャット即時保存_2026-09-20T14-11-30.979062+0900.md
- 旧連番保存：true
- 新タイムスタンプ方式：true

## 移行

- 状態：complete
- 通常工程：大手術の独立検証が完了したためDiMORA本来工程へ復帰する
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する
