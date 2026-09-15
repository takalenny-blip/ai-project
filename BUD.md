# BUD — バドのための最上位ダッシュボード

更新日：2026-09-15

## 正本

- 正本リポジトリ：`takalenny-blip/ai-project`
- 現在状態正本：`docs/現在状態.json`
- 現在ビュー：BUD.md / docs/引き継ぎ/現在の引き継ぎ.md

## 現在の作業レーン

**ai-project運用基盤の大手術（一括改修）**

「一括改修」は設計を一括で行う意味であり、実装は小さな検証単位で進める。

順序：**現状棚卸し → 大手術の設計 → 採用する改善を確定 → 小さな検証単位で順次実装 → 検証**。

- 棚卸し：complete
- 設計：revised_complete
- 採用：complete
- 実装：current_views_migrated_ci_guard_added
- 検証：independent_verification_pending

## 現在状態モデル

- docs/現在状態.jsonを唯一の現在状態正本とし、BUD.mdとdocs/引き継ぎ/現在の引き継ぎ.mdを生成ビューにする
- 自動生成：第1実装済み。scripts/generate_current_views.pyが候補ビューを決定的に生成し、GitHub Actionsで決定性と完全一致を検証する。

## 直チャット

- 最新保存：**045**
- 最新パス：`直チャット/2026-09-15_直チャット即時保存_045.md`
- 旧連番保存：True
- 新タイムスタンプ方式：True

## 移行

- 状態：independent_verification_pending
- 通常工程：大手術の独立検証が完了するまでDiMORA本来工程は再開せず、大手術を優先する
- 暫定同期：BUD/引き継ぎの手動同期は終了し、現在状態JSONを正本として生成結果を一致検証する

## 次の一手

**Claude独立検証の証拠不足を解消するため、現行実ファイルとrun #15〜#31の実statusを提示して再検証を受ける。修正は判定確定後に行う。**
