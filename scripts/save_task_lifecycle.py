#!/usr/bin/env python3
"""Resolve parent/child task state without mistaking delegated work for failure."""
from __future__ import annotations
from dataclasses import dataclass

CHILD_STATES = {"not_started", "dispatched", "in_progress", "blocked", "completed", "failed"}

@dataclass(frozen=True)
class TaskLifecycle:
    parent_status: str
    reason: str

def resolve(parent_requested: bool, children: list[dict]) -> TaskLifecycle:
    if not parent_requested:
        return TaskLifecycle("not_started", "parent task was not requested")
    if not children:
        return TaskLifecycle("dispatched", "parent exists but no child outcome is recorded")
    states = [c.get("status") for c in children]
    if any(s not in CHILD_STATES for s in states):
        raise ValueError("unknown child status")
    if all(s == "completed" for s in states):
        return TaskLifecycle("completed", "all delegated child tasks completed")
    if any(s == "failed" for s in states):
        return TaskLifecycle("failed", "a delegated child explicitly reported terminal failure")
    if any(s in {"blocked", "dispatched", "in_progress"} for s in states):
        return TaskLifecycle("in_progress", "delegated child work is pending; parent is not failed")
    return TaskLifecycle("dispatched", "child task has been delegated but no terminal outcome exists")
