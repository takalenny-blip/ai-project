#!/usr/bin/env python3
"""Detect added, changed, and removed DiMORA favorite-program records."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
KEY_FIELDS=("eventId","mindsProgramId")
RECORD_FIELDS=("eventId","mindsProgramId","title","startDate","endDate","bcsNm","chNo","mode","requestId","recTimerState","length","status","genre")
def load(path:Path)->list[dict[str,Any]]:
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,list) or not all(isinstance(x,dict) for x in data): raise ValueError("normalized input must be a JSON array of objects")
    return data
def record_key(record:dict[str,Any])->str:
    values=[str(record.get(field) or "") for field in KEY_FIELDS]
    if not any(values): raise ValueError("record has no identifying fields")
    return "\x1f".join(values)
def index(records:list[dict[str,Any]])->dict[str,dict[str,Any]]:
    result={}
    for record in records:
        key=record_key(record)
        if key in result: raise ValueError("duplicate record key")
        result[key]=record
    return result
def detect(previous:list[dict[str,Any]],current:list[dict[str,Any]])->dict[str,Any]:
    before,after=index(previous),index(current)
    added=sorted(set(after)-set(before)); removed=sorted(set(before)-set(after))
    changed=sorted(key for key in set(before)&set(after) if {f:before[key].get(f) for f in RECORD_FIELDS}!={f:after[key].get(f) for f in RECORD_FIELDS})
    return {"previous_count":len(previous),"current_count":len(current),"added_count":len(added),"changed_count":len(changed),"removed_count":len(removed),"added":[after[k] for k in added],"changed":[{"before":before[k],"after":after[k]} for k in changed],"removed":[before[k] for k in removed]}
def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("previous",type=Path); parser.add_argument("current",type=Path); args=parser.parse_args()
    print(json.dumps(detect(load(args.previous),load(args.current)),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
