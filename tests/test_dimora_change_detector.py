#!/usr/bin/env python3
import sys,unittest
sys.path.insert(0,"scripts")
from dimora_change_detector import detect
def rec(event,title="番組",mode="15倍録"):
    return {"eventId":event,"mindsProgramId":event,"title":title,"startDate":"202609240100","endDate":"202609240130","bcsNm":"BS日テレ","chNo":"141","mode":mode,"requestId":event,"recTimerState":"1","length":"30","status":"10","genre":"アニメ/特撮"}
class ChangeDetectorTests(unittest.TestCase):
    def test_added_changed_removed(self):
        r=detect([rec("1","残る"),rec("2","変更前"),rec("3","削除")],[rec("1","残る"),rec("2","変更後"),rec("4","追加")])
        self.assertEqual((r["added_count"],r["changed_count"],r["removed_count"]),(1,1,1))
        self.assertEqual(r["added"][0]["eventId"],"4"); self.assertEqual(r["changed"][0]["before"]["title"],"変更前"); self.assertEqual(r["removed"][0]["eventId"],"3")
    def test_identical_snapshot_is_noop(self):
        r=detect([rec("1")],[rec("1")]); self.assertEqual((r["added_count"],r["changed_count"],r["removed_count"]),(0,0,0))
    def test_duplicate_key_is_rejected(self):
        with self.assertRaises(ValueError): detect([rec("1"),rec("1")],[rec("1")])
if __name__=="__main__": unittest.main()
