#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("save_lifecycle_status", ROOT / "scripts" / "save_lifecycle_status.py")
mod = importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(mod)
def test_queue_closed_is_not_failure_when_downstream_save_merged():
    result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"final_save_pr":{"number":554,"state":"closed","merged":True},"canonical_readback":{"verified":True}})
    assert result.status == "completed"
def test_queue_closed_without_downstream_save_is_incomplete():
    result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False}})
    assert result.status == "failed_or_incomplete"
def test_merged_save_without_readback_is_not_complete():
    result = mod.resolve({"queue_pr":{"number":553,"state":"closed","merged":False},"final_save_pr":{"number":554,"state":"closed","merged":True},"canonical_readback":{"verified":False}})
    assert result.status == "merged_readback_pending"
if __name__ == "__main__":
    test_queue_closed_is_not_failure_when_downstream_save_merged(); test_queue_closed_without_downstream_save_is_incomplete(); test_merged_save_without_readback_is_not_complete(); print("OK")