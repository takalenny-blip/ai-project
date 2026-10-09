#!/usr/bin/env python3
"""Select actionable work items from the canonical work queue."""
from __future__ import annotations

from datetime import date
from typing import Iterable


TERMINAL_STATUSES = {"done", "held"}
ACTIVE_STATUSES = {"queued", "in_progress"}


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def validate_work_items(items: Iterable[dict]) -> None:
    items = list(items)
    ids = [item.get("id") for item in items]
    if any(not item_id for item_id in ids):
        raise ValueError("every work item requires id")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate work item id")
    known = set(ids)
    for item in items:
        if item.get("status") not in ACTIVE_STATUSES | TERMINAL_STATUSES:
            raise ValueError(f"invalid work item status: {item.get('status')}")
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or any(dep not in known for dep in deps):
            raise ValueError(f"unknown dependency in {item['id']}")
        if item["id"] in deps:
            raise ValueError(f"self dependency in {item['id']}")
        for field in ("title", "priority", "scope", "target", "evidence",
                      "readiness", "unblock_action", "environment",
                      "created_at", "updated_at"):
            if field not in item:
                raise ValueError(f"{item['id']} missing {field}")
        if item["readiness"] not in {"ready", "blocked"}:
            raise ValueError(f"invalid readiness in {item['id']}")
        if item.get("execution_state") not in {"actionable", "waiting_external"}:
            raise ValueError(f"invalid execution_state in {item['id']}")
        progress = item.get("progress")
        if not isinstance(progress, dict):
            raise ValueError(f"{item['id']} requires structured progress")
        steps = progress.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError(f"{item['id']} progress.steps must be a non-empty list")
        step_ids = [step.get("id") for step in steps]
        if any(not step_id for step_id in step_ids) or len(step_ids) != len(set(step_ids)):
            raise ValueError(f"{item['id']} progress step ids must be unique")
        allowed_step_statuses = {"pending", "in_progress", "waiting_external", "done"}
        if any(step.get("status") not in allowed_step_statuses for step in steps):
            raise ValueError(f"{item['id']} has invalid progress step status")
        current_step = progress.get("current_step")
        if current_step not in step_ids:
            raise ValueError(f"{item['id']} progress.current_step must reference a step")
        current = next(step for step in steps if step["id"] == current_step)
        if current["status"] == "done":
            raise ValueError(f"{item['id']} current progress step cannot be done")
        if item["execution_state"] == "waiting_external" and current["status"] != "waiting_external":
            raise ValueError(f"{item['id']} waiting_external requires waiting progress step")
        if item["execution_state"] == "actionable" and current["status"] == "waiting_external":
            raise ValueError(f"{item['id']} actionable cannot point at waiting progress step")
        if item["execution_state"] == "waiting_external" and not item.get("wait_reason"):
            raise ValueError(f"waiting_external item requires wait_reason: {item['id']}")
        if item["readiness"] == "blocked" and (not item["unblock_action"] or not item.get("blocked_reason")):
            raise ValueError(f"blocked item requires blocked_reason and unblock_action: {item['id']}")
    graph = {item["id"]: item.get("depends_on", []) for item in items}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError("work item dependency cycle detected")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def select_actionable(items: Iterable[dict], today: str | date | None = None) -> list[dict]:
    items = list(items)
    validate_work_items(items)
    current = date.fromisoformat(today) if isinstance(today, str) else (today or date.today())
    by_id = {item["id"]: item for item in items}
    actionable = []
    for item in items:
        if item["status"] in TERMINAL_STATUSES:
            continue
        if item["readiness"] != "ready":
            continue
        if item["execution_state"] != "actionable":
            continue
        if any(by_id[dep]["status"] != "done" for dep in item["depends_on"]):
            continue
        not_before = _date(item.get("not_before"))
        if not_before and current < not_before:
            continue
        actionable.append(item)
    return sorted(actionable, key=lambda item: (item["priority"], item["created_at"], item["id"]))

