# 保存要求：本線ループ防止対策

## 直前回答

ユーザーから「やるやる詐欺。何ターン目だ？」を指摘され、その後「大問題なのに対策されず繰り返す。しっかり直せ」と指摘された。

今回、本線を進めると言いながら状態更新・検証・保存の周辺作業だけが続く問題を、運用上の注意ではなくCIで止める対策を実装した。

- PR #293「本線ループ防止：work/*を実質作業なしで進めないゲートを追加」
- scripts/main_work_progress_guard.py
- tests/test_main_work_progress_guard.py
- .github/workflows/main-work-progress-gate.yml
- docs/現在状態.json にガード契約を記録
- work/* PRは実質的な実装・テスト・workflow変更を含まない場合に失敗させる
- 状態・生成ビューだけの更新は保存トラックへ分離する

PR #293 は自動承認済みでsquash merge済み。merge SHA: 60e8bd8910594240d75492356f6556f4331a5f05。

また、入口チェック結果だけをcanonical stateへ記録するPR #292は、この問題に該当するため閉じた。

## 方針

ここからは「次に進む」と言うだけにせず、work/*で実質的な本線実装を行う。正規化検証は再実行しない。
