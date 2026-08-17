import pytest
from datetime import datetime, timezone

from maclovin.ingestion.feed_reader import parse_feed_content, fetch_feed
from maclovin.models import SourceConfig


def test_parse_feed_content_filtering(sample_rss_xml):
    source = SourceConfig(
        id="test-source",
        name="Test Source",
        ingestion_type="rss",
        url="https://example.com/feed.xml",
        active=True,
    )
    # Temporal window covering 2026-08-16
    start_utc = datetime(2026, 8, 16, 0, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2026, 8, 16, 23, 59, 59, tzinfo=timezone.utc)

    items = parse_feed_content(sample_rss_xml, source, start_utc, end_utc)

    # Two items from 2026-08-16 should pass; the old item from 2026-08-10 must be excluded
    assert len(items) == 2
    assert "OpenAI Announces Major GPT-5" in items[0].title
    assert "Google Unveils Next-Gen" in items[1].title
    assert items[0].source_id == "test-source"
    assert items[0].canonical_url == "https://example.com/openai-gpt5-breakthrough"
