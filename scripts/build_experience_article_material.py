#!/usr/bin/env python3
"""Build deterministic article material from one EXP and its REC files."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

HEADING_RE = re.compile(r"^## (.+?)\s*$")


def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {"\n".join([key]): "\n".join(value).strip() for key, value in sections.items()}


def find_rec_files(log_dir: Path, exp_id: str) -> list[Path]:
    candidates = []
    for path in log_dir.iterdir():
        if not path.is_file() or path.suffix != ".md":
            continue
        if path.name.startswith(f"{exp_id}_REC-") or path.name.startswith(f"REC_{exp_id}_REC-"):
            candidates.append(path)
    return sorted(candidates, key=lambda p: p.name)


def build_material(log_dir: Path, exp_id: str) -> dict:
    exp_path = log_dir / f"{exp_id}.md"
    if not exp_path.is_file():
        raise FileNotFoundError(f"EXP file not found: {exp_path}")

    exp_sections = parse_sections(exp_path.read_text(encoding="utf-8"))
    recs = []
    for rec_path in find_rec_files(log_dir, exp_id):
        recs.append(
            {
                "source_path": rec_path.name,
                "sections": parse_sections(rec_path.read_text(encoding="utf-8")),
            }
        )

    return {
        "schema_version": 1,
        "exp_id": exp_id,
        "source": {
            "exp_path": str(exp_path.as_posix()),
            "rec_paths": [item["source_path"] for item in recs],
        },
        "exp": {
            "title": exp_sections.get("タイトル", ""),
            "sections": exp_sections,
        },
        "recs": recs,
        "article_material": {
            "facts": exp_sections.get("内容", ""),
            "result": exp_sections.get("結果", ""),
            "insights": exp_sections.get("得られた知見", exp_sections.get("気づき", "")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", required=True, help="EXP-ID such as EXP-0000000050")
    parser.add_argument("--log-dir", default="経験ログ")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    material = build_material(Path(args.log_dir), args.exp)
    payload = json.dumps(material, ensure_ascii=False, indent=2) + "\n"

    if args.output == "-":
        print(payload, end="")
    else:
        Path(args.output).write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
