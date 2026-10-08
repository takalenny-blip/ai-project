import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from work_queue import select_actionable, validate_work_items


def item(i, title=None, priority=10, status="queued", deps=None, not_before=None):
    return {
        "id": i, "title": title or i, "priority": priority, "status": status,
        "depends_on": deps or [], "not_before": not_before, "scope": "test",
        "target": i, "evidence": "test evidence", "readiness": "ready",
        "unblock_action": "none", "environment": "work_pc",
        "execution_state": "actionable",
        "progress": {
            "current_step": "step-1",
            "steps": [{"id": "step-1", "title": "step 1", "status": "pending"}],
            "updated_at": "2026-09-27",
        },
        "created_at": "2026-09-27", "updated_at": "2026-09-27",
    }


class WorkQueueTests(unittest.TestCase):
    def test_a_blocks_b_but_d_proceeds(self):
        items = [
            item("A", priority=10),
            item("B", priority=20, deps=["A"]),
            item("C", priority=30, deps=["B"]),
            item("D", priority=15),
            item("E", priority=40, deps=["B"]),
        ]
        self.assertEqual([x["id"] for x in select_actionable(items, "2026-09-27")], ["A", "D"])

    def test_completed_parent_releases_child(self):
        items = [
            item("A", status="done"),
            item("B", priority=20, deps=["A"]),
        ]
        self.assertEqual([x["id"] for x in select_actionable(items, "2026-09-27")], ["B"])

    def test_not_before_holds_until_date(self):
        items = [item("A", not_before="2026-10-01")]
        self.assertEqual(select_actionable(items, "2026-09-30"), [])
        self.assertEqual([x["id"] for x in select_actionable(items, "2026-10-01")], ["A"])

    def test_priority_then_created_at(self):
        items = [
            item("B", priority=10),
            item("A", priority=10),
            item("C", priority=20),
        ]
        items[0]["created_at"] = "2026-09-28"
        self.assertEqual([x["id"] for x in select_actionable(items, "2026-09-27")], ["A", "B", "C"])

    def test_missing_progress_is_rejected(self):
        x = item("A")
        del x["progress"]
        with self.assertRaises(ValueError):
            validate_work_items([x])

    def test_partial_progress_is_valid_and_preserved(self):
        items = [item("A")]
        items[0]["status"] = "in_progress"
        items[0]["progress"] = {
            "current_step": "step-2",
            "steps": [
                {"id": "step-1", "title": "already done", "status": "done", "evidence": "confirmed"},
                {"id": "step-2", "title": "resume here", "status": "in_progress"},
            ],
            "updated_at": "2026-10-08",
        }
        validate_work_items(items)
        self.assertEqual(select_actionable(items, "2026-10-08")[0]["progress"]["current_step"], "step-2")

    def test_waiting_external_requires_waiting_current_step(self):
        items = [item("A")]
        items[0]["execution_state"] = "waiting_external"
        items[0]["wait_reason"] = "external result pending"
        items[0]["progress"]["current_step"] = "step-1"
        items[0]["progress"]["steps"][0]["status"] = "waiting_external"
        validate_work_items(items)

    def test_duplicate_id_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_work_items([item("A"), item("A")])

    def test_missing_dependency_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_work_items([item("A", deps=["MISSING"])])

    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_work_items([item("A", deps=["B"]), item("B", deps=["A"])])

    def test_no_actionable_work_is_empty(self):
        items = [item("A", status="done"), item("B", status="held")]
        self.assertEqual(select_actionable(items, "2026-09-27"), [])

    def test_waiting_external_is_excluded_but_independent_candidate_remains(self):
        items = [
            item("GSC", priority=20),
            item("WP", priority=23),
            item("SITEMAP", priority=21),
        ]
        items[0]["execution_state"] = "waiting_external"
        items[0]["wait_reason"] = "GSC is processing the URL inspection result"
        candidates = select_actionable(items, "2026-10-08")
        self.assertEqual([x["id"] for x in candidates], ["SITEMAP", "WP"])
        self.assertNotIn("GSC", [x["id"] for x in candidates])

    def test_independent_ready_candidate_is_not_lost_behind_higher_priority_work(self):
        items = [
            item("GSC", priority=20),
            item("WP", priority=23),
            item("BLOG", priority=30, deps=["GSC"]),
        ]
        candidates = select_actionable(items, "2026-10-08")
        self.assertEqual([x["id"] for x in candidates], ["GSC", "WP"])
        self.assertIn("WP", [x["id"] for x in candidates])

