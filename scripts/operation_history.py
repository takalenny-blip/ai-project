#!/usr/bin/env python3
"""Shared operation-history helpers for canonical state changes."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def state_fingerprint(state: dict[str, Any]) -> str:
    """Fingerprint canonical state while excluding its own operation history."""
    snapshot = {k: v for k, v in state.items() if k != "operation_history"}
    payload = json.dumps(
        snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def append_operation(
    state: dict[str, Any],
    *,
    operation: str,
    purpose: str,
    target: str,
    before_state_fingerprint: str,
    after_state_fingerprint: str,
    result: str,
    status: str,
) -> None:
    """Append one completed canonical operation without recording history as progress."""
    history = state.setdefault("operation_history", [])
    if not isinstance(history, list):
        raise ValueError("operation_history must be a list")
    history.append(
        {
            "operation": operation,
            "purpose": purpose,
            "target": target,
            "result": result,
            "status": status,
            "before_state_fingerprint": before_state_fingerprint,
            "after_state_fingerprint": after_state_fingerprint,
        }
    )
    del history[:-50]
