import pytest
from datetime import date
from maclovin.core.pipeline import Pipeline
from maclovin.models import AppConfig


def test_idempotent_pipeline_execution(sample_config, in_memory_db, mock_llm_provider, monkeypatch):
    # Mock network fetching to return fixed items
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Tech Feed</title>
    <item>
      <title>OpenAI Breakthrough in AI Agents</title>
      <link>https://example.com/openai-breakthrough</link>
      <pubDate>Sun, 16 Aug 2026 14:00:00 +0000</pubDate>
      <description>OpenAI agents</description>
    </item>
  </channel>
</rss>"""

    from maclovin.ingestion import feed_reader
    def mock_fetch(source, start, end):
        return feed_reader.parse_feed_content(sample_xml, source, start, end), []

    monkeypatch.setattr(feed_reader, "fetch_feed", mock_fetch)

    pipeline = Pipeline(
        config=sample_config,
        llm_provider=mock_llm_provider,
        db_connection=in_memory_db,
    )

    # First run
    report1 = pipeline.run(target_date=date(2026, 8, 16), dry_run=False)
    cursor = in_memory_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM news_items")
    count_run1 = cursor.fetchone()[0]
    assert count_run1 == 1

    # Second run for the exact same date and feed
    report2 = pipeline.run(target_date=date(2026, 8, 16), dry_run=False)
    cursor.execute("SELECT COUNT(*) FROM news_items")
    count_run2 = cursor.fetchone()[0]
    # Count of news items must remain exactly 1 (zero duplicates inserted)
    assert count_run2 == 1
