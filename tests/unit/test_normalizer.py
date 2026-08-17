import pytest
from maclovin.ingestion.normalizer import canonicalize_url, sanitize_title
from maclovin.ingestion.html_extractor import clean_html_text


def test_canonicalize_url():
    # Strips tracking query parameters like utm_source, fbclid, etc.
    raw_url = "https://techcrunch.com/2026/08/16/ai-agent/?utm_source=twitter&utm_medium=social#heading-1"
    clean_url = canonicalize_url(raw_url)
    assert clean_url == "https://techcrunch.com/2026/08/16/ai-agent"


def test_sanitize_title():
    raw_title = "   OpenAI Launches GPT-5 &amp; New Features &nbsp;  "
    clean_title = sanitize_title(raw_title)
    assert clean_title == "OpenAI Launches GPT-5 & New Features"


def test_clean_html_text():
    raw_html = "<p>This is a <b>great</b> AI breakthrough.<br>Read more at <a href='#'>link</a>.</p>"
    text = clean_html_text(raw_html)
    assert "This is a great AI breakthrough." in text
    assert "<p>" not in text
    assert "<br>" not in text
