#!/usr/bin/env python3
"""Build a stable downstream payload from DiMORA change detection results."""
from __future__ import annotations
import argparse,json
from pathlib import Path
def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("changes",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    data=json.loads(a.changes.read_text(encoding="utf-8"))
    required=("previous_count","current_count","added_count","changed_count","removed_count")
    missing=[k for k in required if k not in data]
    if missing: raise ValueError("missing change summary fields: "+",".join(missing))
    payload={"schema":"dimora-change-v1","previous_count":data["previous_count"],"current_count":data["current_count"],"added":data.get("added",[]),"changed":data.get("changed",[]),"removed":data.get("removed",[]),"counts":{"added":data["added_count"],"changed":data["changed_count"],"removed":data["removed_count"]}}
    a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(a.output),"schema":payload["schema"],"total_changes":sum(payload["counts"].values())},ensure_ascii=False))
    return 0
if __name__=="__main__": raise SystemExit(main())
