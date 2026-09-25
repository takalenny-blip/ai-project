from pathlib import Path

import scripts.blog_html_version as versioning


def test_next_version_starts_at_one_when_no_snapshots(tmp_path, monkeypatch):
    monkeypatch.setattr(versioning, "VERSION_DIR", tmp_path / "versions")
    assert versioning.available_versions() == []
    assert versioning.next_version() == 1


def test_backup_uses_blog_number_and_five_digit_generation(tmp_path, monkeypatch):
    current = tmp_path / "current.html"
    current.write_bytes(b"<h2>test</h2>\r\n")
    versions = tmp_path / "versions"
    monkeypatch.setattr(versioning, "CURRENT_HTML", current)
    monkeypatch.setattr(versioning, "VERSION_DIR", versions)

    destination = versioning.backup()

    assert destination.name == "BLOG-0001_ver00001.html"
    assert destination.read_bytes() == current.read_bytes()


def test_backup_increments_after_existing_generation(tmp_path, monkeypatch):
    current = tmp_path / "current.html"
    current.write_bytes(b"current")
    versions = tmp_path / "versions"
    versions.mkdir()
    (versions / "BLOG-0001_ver00001.html").write_bytes(b"old")
    (versions / "BLOG-0001_ver00003.html").write_bytes(b"old3")
    (versions / "other.html").write_bytes(b"ignored")
    monkeypatch.setattr(versioning, "CURRENT_HTML", current)
    monkeypatch.setattr(versioning, "VERSION_DIR", versions)

    assert versioning.next_version() == 4


def test_restore_copies_snapshot_exactly(tmp_path, monkeypatch):
    current = tmp_path / "current.html"
    current.write_bytes(b"new")
    versions = tmp_path / "versions"
    versions.mkdir()
    snapshot = versions / "BLOG-0001_ver00002.html"
    snapshot.write_bytes(b"original\r\n")
    monkeypatch.setattr(versioning, "CURRENT_HTML", current)
    monkeypatch.setattr(versioning, "VERSION_DIR", versions)

    source = versioning.restore(2)

    assert source == snapshot
    assert current.read_bytes() == b"original\r\n"
