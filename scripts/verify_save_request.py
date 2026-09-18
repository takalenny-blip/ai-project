#!/usr/bin/env python3
"""Verify the save-request-intake chain from its push-source commit SHA."""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import urllib.parse

REPO = "takalenny-blip/ai-project"
WORKFLOW = "save-request-intake.yml"


def gh_api(path: str):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def gh_blob(sha: str) -> str:
    payload = gh_api(f"repos/{REPO}/git/blobs/{urllib.parse.quote(sha, safe='')}")
    data = payload.get("content", "")
    if payload.get("encoding") == "base64":
        return base64.b64decode(data).decode("utf-8")
    return data


def read_path_at_commit(ref: str, path: str) -> str | None:
    tree = gh_api(
        f"repos/{REPO}/git/trees/{urllib.parse.quote(ref, safe='')}?recursive=1"
    )
    for entry in tree.get("tree", []):
        if entry.get("path") == path and entry.get("type") == "blob":
            return gh_blob(entry["sha"])
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_sha")
    args = ap.parse_args()
    sha = args.source_sha

    wf = urllib.parse.quote(WORKFLOW, safe="")
    runs = gh_api(
        f"repos/{REPO}/actions/workflows/{wf}/runs"
        f"?event=push&head_sha={urllib.parse.quote(sha, safe='')}&per_page=10"
    ).get("workflow_runs", [])

    if not runs:
        print(json.dumps({
            "stage": "intake_run", "status": "not_found",
            "source_sha": sha, "workflow": WORKFLOW
        }, ensure_ascii=False, indent=2))
        return 2
    if len(runs) > 1:
        print(json.dumps({
            "stage": "intake_run", "status": "ambiguous",
            "source_sha": sha, "run_ids": [r["id"] for r in runs]
        }, ensure_ascii=False, indent=2))
        return 3

    run = runs[0]
    run_id = run["id"]
    save_branch = f"save/direct-chat-{run_id}"
    owner = REPO.split("/")[0]
    head = urllib.parse.quote(f"{owner}:{save_branch}", safe="")

    prs = gh_api(f"repos/{REPO}/pulls?head={head}&state=all&per_page=10")
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

    if not isinstance(prs, list) or not prs:
        result.update(stage="pr_creation", status="not_found")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 4
    if len(prs) > 1:
        result.update(
            stage="pr_creation", status="ambiguous",
            pr_candidates=[p.get("number") for p in prs]
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 5

    pr = prs[0]
    number = pr["number"]
    head_sha = pr["head"]["sha"]
    result["pr"] = {
        "number": number,
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
        {"name": c.get("name"), "status": c.get("status"),
         "conclusion": c.get("conclusion")}
        for c in checks
    ]

    reviews = gh_api(f"repos/{REPO}/pulls/{number}/reviews?per_page=100")
    approved = [r for r in reviews if r.get("state") == "APPROVED"]
    result["approval"] = {
        "approved": bool(approved),
        "approval_count": len(approved),
    }

    merge_sha = pr.get("merge_commit_sha")
    if merge_sha:
        state_text = read_path_at_commit(merge_sha, "docs/現在状態.json")
        state_ok = False
        state_sha = None
        latest_path = None
        if state_text is not None:
            try:
                state = json.loads(state_text)
                direct = state.get("direct_chat", {})
                latest_path = direct.get("latest_path")
                latest_content_sha = direct.get("latest_content_sha")
                if latest_path:
                    latest_text = read_path_at_commit(merge_sha, latest_path)
                    if latest_text is not None:
                        state_ok = True
                        # Verify the canonical state's recorded content SHA
                        # against the actual direct-chat blob at the merge commit.
                        blob_tree = gh_api(
                            f"repos/{REPO}/git/trees/"
                            f"{urllib.parse.quote(merge_sha, safe='')}?recursive=1"
                        )
                        for entry in blob_tree.get("tree", []):
                            if entry.get("path") == latest_path and entry.get("type") == "blob":
                                state_sha = entry.get("sha")
                                break
                        if latest_content_sha and state_sha:
                            state_ok = latest_content_sha == state_sha
            except (json.JSONDecodeError, TypeError):
                state_ok = False
        result["readback"] = {
            "verified": state_ok,
            "ref": merge_sha,
            "latest_path": latest_path,
            "latest_content_sha": state_sha,
        }

    intake_ok = run.get("conclusion") == "success"
    ci_ok = bool(checks) and all(
        c.get("status") == "completed" and c.get("conclusion") == "success"
        for c in checks
    )
    merged_ok = bool(pr.get("merged_at"))
    approval_ok = bool(approved)
    readback_ok = bool(result["readback"] and result["readback"]["verified"])

    if not intake_ok:
        result.update(stage="intake_run", status="not_success")
        code = 6
    elif not ci_ok:
        result.update(stage="ci", status="missing_or_not_success")
        code = 7
    elif not merged_ok:
        result.update(stage="merge", status="pending")
        code = 8
    elif not approval_ok:
        result.update(stage="approval", status="missing")
        code = 9
    elif not readback_ok:
        result.update(stage="readback", status="failed")
        code = 10
    else:
        result.update(stage="complete", status="verified")
        code = 0

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
