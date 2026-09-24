#!/usr/bin/env python3
from scripts.build_blogger_draft_payload import normalize_h3_spacing

def test_h3_gets_one_blank_paragraph():
    html = "<p>前</p><h3>見出し</h3>"
    assert normalize_h3_spacing(html) == "<p>前</p><p><br /></p><h3>見出し</h3>"

def test_multiple_blank_paragraphs_are_collapsed():
    html = "<p>前</p><p><br /></p><p><br /></p><h3>見出し</h3>"
    assert normalize_h3_spacing(html) == "<p>前</p><p><br /></p><h3>見出し</h3>"

def test_existing_single_blank_paragraph_is_preserved():
    html = "<p>前</p><p><br /></p><h3>見出し</h3>"
    assert normalize_h3_spacing(html) == html
