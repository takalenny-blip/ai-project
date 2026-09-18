#!/usr/bin/env python3
"""Verify the save-request-intake chain from its push-source commit SHA."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse


REPO = "takalenny-blip/ai-project"
WORKFLOW = "save-request-intake.yml"


def gh_api(path: str) -> dict:
    out = subprocess.check_output(["gh", "api", path], text=True)
    return json.loads(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_sha", help="SHA pushed to chat-save-request/*")
    args = ap.parse_args()

    sha = args.source_sha
    workflow = urllib.parse.quote(WORKFLOW, safe="")
    runs_path = (
        f"repos/{REPO}/actions/workflows/{workflow}/runs"
        f"?event=push&head_sha={urllib.parse.quote(sha, safe='')}&per_page=10"
    )
    runs = gh_api(runs_path).get("workflow_runs", [])
    if not runs:
        print(json.dumps({
            "stage": "intake_run",
            "status": "not_found",
            "source_sha": sha,
            "workflow": WORKFLOW,
        }, ensure_ascii=False, indent=2))
        return 2

    if len(runs) > 1:
        print(json.dumps({
            "stage": "intake_run",
            "status": "ambiguous",
            "source_sha": sha,
            "workflow": WORKFLOW,
            "run_ids": [r["id"] for r in runs],
        }, ensure_ascii=False, indent=2))
        return 3

    run = runs[0]
    run_id = run["id"]
    save_branch = f"save/direct-chat-{run_id}"
    encoded_head = urllib.parse.quote(f"{REPO.split('/')[0]}:{save_branch}", safe="")
    prs = gh_api(
        f"repos/{REPO}/pulls?head={encoded_head}&state=all&per_page=10"
    ).get("[]", [])
    if isinstance(prs, dict):
        prs = []
    # GitHub returns a JSON array for this endpoint; gh_api therefore needs
    # to tolerate non-object responses.
    if not isinstance(prs, list):
        prs = []

    result = {
        "source_sha": sha,
        "workflow": WORKFLOW,
        "intake_run": {
            "id": run_id,
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "html_url": run.get("html_url"),
        },
        "save_branch": save_branch,
        "pr": None,
        "ci": None,
        "approval": None,
        "readback": None,
    }

    if not prs:
        result["stage"] = "pr_creation"
        result["status"] = "not_found"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 4

    if len(prs) > 1:
        result["stage"] = "pr_creation"
        result["status"] = "ambiguous"
        result["pr_candidates"] = [p.get("number") for p in prs]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 5

    pr = prs[0]
    pr_number = pr["number"]
    head_sha = pr["head"]["sha"]
    result["pr"] = {
        "number": pr_number,
        "state": pr.get("state"),
        "merged_at": pr.get("merged_at"),
        "merge_commit_sha": pr.get("merge_commit_sha"),
        "head_sha": head_sha,
        "html_url": pr.get("html_url"),
    }

    checks = gh_api(
        f"repos/{REPO}/commits/{head_sha}/check-runs?per_page=100"
    ).get("check_runs", [])
    result["ci"] = [
        {"name": c.get("name"), "status": c.get("status"), "conclusion": c.get("conclusion")}
        for c in checks
    ]

    reviews = gh_api(
        f"repos/{REPO}/pulls/{pr_number}/reviews?per_page=100"
    )
    approved = [r for r in reviews if r.get("state") == "APPROVED"]
    result["approval"] = {"approved": bool(approved), "approval_count": len(approved)}

    merge_sha = pr.get("merge_commit_sha")
    if merge_sha:
        state = gh_api(
            f"repos/{REPO}/contents/docs/%E7%8F%BE%E5%9C%A8%E7%8A%B6.json?ref={merge_sha}"
        )
        result["readback"] = {
            "verified": bool(state.get("sha")),
            "sha": state.get("sha"),
            "ref": merge_sha,
        }

    if not run.get("conclusion") == "success":
        result["stage"] = "intake_run"
        result["status"] = "not_success"
        code = 6
    elif pr.get("merged_at") is None:
        result["stage"] = "merge"
        result["status"] = "pending"
        code = 7
    elif not approved:
        result["stage"] = "approval"
        result["status"] = "missing"
        code = 8
    elif not result["readback"]["verified"]:
        result["stage"] = "readback"
        result["status"] = "failed"
        code = 9
    else:
        result["stage"] = "complete"
        result["status"] = "verified"
        code = 0

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
