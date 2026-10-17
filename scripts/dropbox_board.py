#!/usr/bin/env python3
"""Read and validate the canonical Dropbox work board through the Dropbox API."""
from __future__ import annotations

import io
import json
import os
import urllib.error
import urllib.request
import zipfile

DEFAULT_REMOTE_PATH = "/ChatGPT/Dropbox作業管理統合ボード.xlsx"
DOWNLOAD_URL = "https://content.dropboxapi.com/2/files/download"


def validate_xlsx_bytes(data: bytes) -> None:
    """Raise ValueError unless bytes form a readable XLSX ZIP container."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as workbook:
            bad_member = workbook.testzip()
            if bad_member is not None:
                raise ValueError(f"corrupt XLSX member: {bad_member}")
            required = {"[Content_Types].xml", "xl/workbook.xml"}
            missing = required.difference(workbook.namelist())
            if missing:
                raise ValueError("not a valid XLSX workbook; missing: " + ", ".join(sorted(missing)))
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError(f"Dropbox work board response is not a readable XLSX: {exc}") from exc


def fetch_remote_board(token: str, remote_path: str = DEFAULT_REMOTE_PATH, timeout: int = 20) -> bytes:
    """Download the exact configured Dropbox path; never fall back after API failure."""
    if not token or not token.strip():
        raise ValueError("DROPBOX_ACCESS_TOKEN is empty")
    if not remote_path.startswith("/") or "\n" in remote_path or "\r" in remote_path:
        raise ValueError("Dropbox remote path must be an absolute Dropbox path")
    request = urllib.request.Request(
        DOWNLOAD_URL,
        data=None,
        headers={
            "Authorization": "Bearer " + token,
            # Keep HTTP header bytes ASCII-only; Dropbox paths may contain Japanese.
            "Dropbox-API-Arg": json.dumps({"path": remote_path}, ensure_ascii=True),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Do not include request headers or credentials in the diagnostic.
        raise ValueError(f"Dropbox API download failed ({type(exc).__name__})") from None
    validate_xlsx_bytes(data)
    return data


def validate_remote_board_from_env() -> str:
    """Validate the remote board when credentials are configured; return its path."""
    token = os.environ.get("DROPBOX_ACCESS_TOKEN", "")
    remote_path = os.environ.get("DROPBOX_WORK_QUEUE_REMOTE_PATH", DEFAULT_REMOTE_PATH)
    fetch_remote_board(token, remote_path)
    return remote_path
