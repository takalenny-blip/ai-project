#!/usr/bin/env python3
"""Verify the save-request-intake chain from its push-source commit SHA."""
from __future__ import annotations
import argparse, json, subprocess, urllib.parse
REPO="takalenny-blip/ai-project"
WORKFLOW="save-request-intake.yml"
def gh_api(path: str):
    return json.loads(subprocess.check_output(["gh","api",path], text=True))
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("source_sha"); args=ap.parse_args()
    sha=args.source_sha
    wf=urllib.parse.quote(WORKFLOW,safe="")
    runs=gh_api(f"repos/{REPO}/actions/workflows/{wf}/runs?event=push&head_sha={urllib.parse.quote(sha,safe='')}&per_page=10").get("workflow_runs",[])
    if not runs:
        print(json.dumps({"stage":"intake_run","status":"not_found","source_sha":sha,"workflow":WORKFLOW},ensure_ascii=False,indent=2)); return 2
    if len(runs)>1:
        print(json.dumps({"stage":"intake_run","status":"ambiguous","source_sha":sha,"run_ids":[r["id"] for r in runs]},ensure_ascii=False,indent=2)); return 3
    run=runs[0]; run_id=run["id"]; save_branch=f"save/direct-chat-{run_id}"; owner=REPO.split("/")[0]
    head=urllib.parse.quote(f"{owner}:{save_branch}",safe="")
    prs=gh_api(f"repos/{REPO}/pulls?head={head}&state=all&per_page=10")
    result={"source_sha":sha,"workflow":WORKFLOW,"intake_run":{"id":run_id,"status":run.get("status"),"conclusion":run.get("conclusion"),"html_url":run.get("html_url")},"save_branch":save_branch,"pr":None,"ci":None,"approval":None,"readback":None}
    if not isinstance(prs,list) or not prs:
        result.update(stage="pr_creation",status="not_found"); print(json.dumps(result,ensure_ascii=False,indent=2)); return 4
    if len(prs)>1:
        result.update(stage="pr_creation",status="ambiguous",pr_candidates=[p.get("number") for p in prs]); print(json.dumps(result,ensure_ascii=False,indent=2)); return 5
    pr=prs[0]; number=pr["number"]; head_sha=pr["head"]["sha"]
    result["pr"]={"number":number,"state":pr.get("state"),"merged_at":pr.get("merged_at"),"merge_commit_sha":pr.get("merge_commit_sha"),"head_sha":head_sha,"html_url":pr.get("html_url")}
    checks=gh_api(f"repos/{REPO}/commits/{head_sha}/check-runs?per_page=100").get("check_runs",[])
    result["ci"]=[{"name":c.get("name"),"status":c.get("status"),"conclusion":c.get("conclusion")} for c in checks]
    reviews=gh_api(f"repos/{REPO}/pulls/{number}/reviews?per_page=100")
    approved=[r for r in reviews if r.get("state")=="APPROVED"]; result["approval"]={"approved":bool(approved),"approval_count":len(approved)}
    merge_sha=pr.get("merge_commit_sha")
    if merge_sha:
        state=gh_api(f"repos/{REPO}/contents/docs/%E7%8F%BE%E5%9C%A8%E7%8A%B6.json?ref={merge_sha}")
        result["readback"]={"verified":bool(state.get("sha")),"sha":state.get("sha"),"ref":merge_sha}
    if run.get("conclusion")!="success": result.update(stage="intake_run",status="not_success"); code=6
    elif not pr.get("merged_at"): result.update(stage="merge",status="pending"); code=7
    elif not approved: result.update(stage="approval",status="missing"); code=8
    elif not result["readback"] or not result["readback"]["verified"]: result.update(stage="readback",status="failed"); code=9
    else: result.update(stage="complete",status="verified"); code=0
    print(json.dumps(result,ensure_ascii=False,indent=2)); return code
if __name__=="__main__": raise SystemExit(main())
