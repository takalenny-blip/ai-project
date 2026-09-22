#!/usr/bin/env python3
"""Build a human-reviewable blog proposal from a grounded experience article candidate."""
from __future__ import annotations
import argparse, json
from pathlib import Path
REQUIRED_FIELDS=("title","intro","body","insights","uncertain_or_notes","grounding")
def build_proposal(candidate:dict)->dict:
    missing=[n for n in REQUIRED_FIELDS if n not in candidate]
    if missing: raise ValueError("missing candidate fields: "+", ".join(missing))
    if not isinstance(candidate["grounding"],list) or not candidate["grounding"]: raise ValueError("grounding must be a non-empty list")
    return {"schema_version":1,"status":"draft","review":{"required":True,"decision":"pending","notes":""},"proposal":{n:candidate[n] for n in REQUIRED_FIELDS[:-1]},"grounding":candidate["grounding"],"publication":{"blogger_payload_ready":False,"draft_posted":False,"published":False}}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--candidate",required=True); p.add_argument("--output",default="-"); a=p.parse_args()
    out=json.dumps(build_proposal(json.loads(Path(a.candidate).read_text(encoding="utf-8"))),ensure_ascii=False,indent=2)+"\n"
    print(out,end="") if a.output=="-" else Path(a.output).write_text(out,encoding="utf-8")
if __name__=="__main__": main()
