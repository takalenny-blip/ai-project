#!/usr/bin/env python3
"""Validate an AI article candidate against the supplied primary article material."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED_FIELDS = ("title", "intro", "body", "insights", "uncertain_or_notes", "grounding")
GROUNDING_FIELDS = ("source_path", "evidence")


def _source_texts(material: dict) -> dict[str, str]:
    texts: dict[str, str] = {}
    source = material.get("source", {})
    exp_path = source.get("exp_path")
    exp = material.get("exp", {})
    if exp_path:
        texts[exp_path] = json.dumps(exp.get("sections", {}), ensure_ascii=False)
    for rec in material.get("recs", []):
        path = rec.get("source_path")
        if path:
            texts[path] = json.dumps(rec.get("sections", {}), ensure_ascii=False)
    return texts


def validate_candidate(material: dict, candidate: dict) -> list[str]:
    errors: list[str] = []
    if material.get("schema_version") != 1:
        errors.append("unsupported article material schema_version")
    missing = [field for field in REQUIRED_FIELDS if not isinstance(candidate.get(field), str) and field != "grounding"]
    if missing:
        errors.append("missing candidate text fields: " + ", ".join(missing))
    grounding = candidate.get("grounding")
    if not isinstance(grounding, list) or not grounding:
        errors.append("grounding must be a non-empty list")
        return errors

    sources = _source_texts(material)
    for index, item in enumerate(grounding):
        if not isinstance(item, dict):
            errors.append(f"grounding[{index}] must be an object")
            continue
        missing_fields = [field for field in GROUNDING_FIELDS if not isinstance(item.get(field), str) or not item[field].strip()]
        if missing_fields:
            errors.append(f"grounding[{index}] missing: " + ", ".join(missing_fields))
            continue
        source_path = item["source_path"]
        evidence = item["evidence"]
        source_text = sources.get(source_path)
        if source_text is None:
            errors.append(f"grounding[{index}] unknown source_path: {source_path}")
            continue
        if evidence not in source_text:
            errors.append(f"grounding[{index}] evidence is not an exact substring of source: {source_path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--material", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    material = json.loads(Path(args.material).read_text(encoding="utf-8"))
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    errors = validate_candidate(material, candidate)
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("OK: article candidate grounding is structurally and textually grounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
