# DiMORA検証状態モデル修正

PR #234で完了している実データ正規化検証と、未確認のwork_pc原本ファイル直接アクセスを別工程として現在状態へ反映する。PR #255で再実行防止ガードをmainへ反映済み。

## 状態
- 実データ正規化検証：完了（PR #234）
- 原本ファイル直接アクセス検証：未確認
- 次の一手：原本ファイル直接アクセスだけを検証する

<!-- BUD_STATE_PATCH_BEGIN
{
  "verification_records": {
    "dimora_actual_data_normalization": {
      "status": "verified",
      "label": "DiMORA実データ正規化検証",
      "evidence": {
        "method": "PR #234でmainのscripts/dimora_json_normalizer.pyに実データ1件を入力して検証",
        "checked_at": "2026-09-20",
        "pr": "#234",
        "input_count": 1,
        "output_count": 1,
        "field_count": 13,
        "result_sha256": "d445b92b13f34fef12cfd8206373b69d437329d7b362c4defe7eaf79ab182759"
      }
    },
    "dimora_source_artifact_access": {
      "status": "unverified",
      "label": "work_pc上のDiMORA実機エクスポート原本JSONへの直接アクセス",
      "evidence": null
    }
  },
  "current_position": {
    "status": "current",
    "summary": "DiMORAの実データ正規化検証（P2）はPR #234で完了済み。これはwork_pc上の原本ファイルへのBudの直接アクセス検証とは別であり、現在はそのアクセス経路だけを検証する段階。",
    "evidence": {
      "type": "repository_record",
      "references": [
        "PR #234: DiMORA実データ正規化検証完了",
        "PR #255: 検証scope分離・再実行防止機構をmainへ反映"
      ],
      "note": "PR #234の実データ正規化検証結果を完了済みscopeとして固定し、PR #255でnext_step.scopeとverification_recordsによる分離ガードを実装・merge済み。"
    }
  },
  "next_step": {
    "environment": "work_pc",
    "scope": "dimora_source_artifact_access",
    "target": "work_pc上のDiMORA実機エクスポート原本JSONへの直接アクセス経路を検証する",
    "evidence": "work_pc runtime artifact: dimora-favorite-programs.json / PR #234の実データ正規化検証とは別scope",
    "readiness": "blocked",
    "blocked_reason": "work_pc上の実機エクスポート原本JSONが、現在の実行環境から直接利用可能であることは未確認",
    "unblock_action": "work_pcで原本JSONの存在・可読性・形式・件数を確認し、直接アクセス経路の証拠を記録する。正規化検証は再実行しない。",
    "prerequisites": [
      {
        "name": "scripts/dimora_json_normalizer.py",
        "kind": "repo_file",
        "verify_scope": "ci",
        "status": "verified",
        "evidence": {
          "method": "GitHub main readback with repository blob SHA",
          "checked_at": "2026-09-20",
          "blob_sha": "7bcf28c818f836dd7257b7f5db1dd233da8543c5"
        }
      },
      {
        "name": "tests/test_dimora_json_normalizer.py",
        "kind": "repo_file",
        "verify_scope": "ci",
        "status": "verified",
        "evidence": {
          "method": "GitHub main readback with repository blob SHA",
          "checked_at": "2026-09-20",
          "blob_sha": "8ff57ffba6562fbf350f6679783ee83234692588"
        }
      },
      {
        "name": "dimora-favorite-programs.json",
        "location": "work_pc runtime artifact",
        "kind": "external_artifact",
        "verify_scope": "runtime",
        "status": "unverified",
        "evidence": null
      }
    ]
  }
}
BUD_STATE_PATCH_END -->