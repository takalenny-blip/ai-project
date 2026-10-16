#!/usr/bin/env python3
import io
import json
import unittest
import urllib.error
import zipfile
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dropbox_board


def minimal_xlsx():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as workbook:
        workbook.writestr("[Content_Types].xml", "<Types></Types>")
        workbook.writestr("xl/workbook.xml", "<workbook></workbook>")
    return buffer.getvalue()


class DropboxRemoteBoardTests(unittest.TestCase):
    def test_remote_download_uses_fixed_path_and_validates_xlsx(self):
        payload = minimal_xlsx()

        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return payload

        def fake_urlopen(request, timeout):
            self.assertEqual(request.full_url, dropbox_board.DOWNLOAD_URL)
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
            arg = json.loads(request.get_header("Dropbox-api-arg"))
            self.assertEqual(arg["path"], "/ChatGPT/Dropbox作業管理統合ボード.xlsx")
            self.assertEqual(timeout, 20)
            return Response()

        with patch.object(dropbox_board.urllib.request, "urlopen", side_effect=fake_urlopen):
            self.assertEqual(
                dropbox_board.fetch_remote_board("test-token"),
                payload,
            )

    def test_remote_api_failure_fails_closed_without_fallback(self):
        with patch.object(
            dropbox_board.urllib.request,
            "urlopen",
            side_effect=urllib.error.URLError("simulated outage"),
        ):
            with self.assertRaisesRegex(ValueError, "Dropbox API download failed"):
                dropbox_board.fetch_remote_board("test-token")

    def test_invalid_remote_response_fails_closed(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b"not-an-xlsx"

        with patch.object(dropbox_board.urllib.request, "urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "not a readable XLSX"):
                dropbox_board.fetch_remote_board("test-token")

    def test_empty_token_fails_before_network_access(self):
        with patch.object(dropbox_board.urllib.request, "urlopen") as request:
            with self.assertRaisesRegex(ValueError, "DROPBOX_ACCESS_TOKEN is empty"):
                dropbox_board.fetch_remote_board("")
            request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
