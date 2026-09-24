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

def test_empty_h3_spacing_marker_becomes_blank_paragraph():
    html = '<p>前</p><h3 id="toc-1"><br /></h3><h3 id="toc-1">見出し</h3>'
    assert normalize_h3_spacing(html) == '<p>前</p><p><br /></p><h3 id="toc-1">見出し</h3>'

def test_empty_h3_with_whitespace_is_removed():
    html = '<h3 id="toc-1"> \n<br />\n </h3>\n<h3 id="toc-1">見出し</h3>'
    assert normalize_h3_spacing(html) == '<p><br /></p><h3 id="toc-1">見出し</h3>'
