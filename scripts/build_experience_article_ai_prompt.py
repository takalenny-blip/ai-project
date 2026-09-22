#!/usr/bin/env python3
"""Build a provider-neutral AI editing prompt from deterministic article material."""
from __future__ import annotations
import argparse, json
from pathlib import Path

SYSTEM_INSTRUCTIONS = """あなたは経験ログを記事候補へ編集するAIです。
入力に含まれる一次記録だけを根拠として使ってください。
事実・結果・本人の判断や感想は、入力中の記録を超えて補完しないでください。
入力にない固有名詞、出来事、数値、因果関係、本人の発言を作らないでください。
不明な点は推測せず「記録上不明」としてください。
記事候補は「タイトル」「導入」「本文」「得られた知見」「未確定・注意」「grounding」の構造で出力してください。
groundingは1件以上のオブジェクト配列とし、各件に「source_path」と「evidence」を含めてください。
source_pathは入力記事素材の一次記録にあるsource_pathだけを使い、evidenceはその一次記録の内容からそのまま抜き出した完全一致の文字列にしてください。
記事本文の主張を一次記録へ追跡できない場合は、その主張を作らず「記録上不明」としてください。
文章表現の整理・順序変更・見出し化は行ってよいですが、意味を変更しないでください。
Bloggerへの投稿、公開、認証、外部通信は行わないでください。
"""

def build_prompt(material: dict) -> str:
    if material.get("schema_version") != 1:
        raise ValueError("unsupported article material schema_version")
    payload = json.dumps(material, ensure_ascii=False, indent=2)
    return (
        SYSTEM_INSTRUCTIONS
        + "\n\n## 入力記事素材\n"
        + payload
        + '\n\n## 出力形式\n{"title":"","intro":"","body":"","insights":"","uncertain_or_notes":"","grounding":[{"source_path":"","evidence":""}]}\n'
    )

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    material = json.loads(Path(args.input).read_text(encoding="utf-8"))
    prompt = build_prompt(material)
    if args.output == "-":
        print(prompt, end="")
    else:
        Path(args.output).write_text(prompt, encoding="utf-8")

if __name__ == "__main__":
    main()
