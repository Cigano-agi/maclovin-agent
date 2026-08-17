import pytest
from datetime import datetime, timezone, date

from maclovin.models import NewsItem, EventCluster, SourceConfig
from maclovin.storage.news_repo import save_sources, save_news_items, save_events, get_news_by_date


def test_save_news_items_and_idempotency(in_memory_db):
    source = SourceConfig(id="tc", name="TechCrunch", ingestion_type="rss", url="https://tc.com/rss")
    save_sources(in_memory_db, [source])

    item1 = NewsItem(
        id="1",
        source_id="tc",
        title="Breaking News",
        canonical_url="https://tc.com/1",
        published_date_utc=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
        raw_content="Content of article 1",
    )

    # First insertion -> 1 inserted, 0 duplicates
    inserted, duplicates = save_news_items(in_memory_db, [item1])
    assert inserted == 1
    assert duplicates == 0

    # Second insertion of same item -> 0 inserted, 1 duplicate
    inserted2, duplicates2 = save_news_items(in_memory_db, [item1])
    assert inserted2 == 0
    assert duplicates2 == 1

    # Query items for that date
    items_in_db = get_news_by_date(in_memory_db, date(2026, 8, 16))
    assert len(items_in_db) == 1
    assert items_in_db[0].title == "Breaking News"


def test_save_events(in_memory_db):
    source = SourceConfig(id="tc", name="TechCrunch", ingestion_type="rss", url="https://tc.com/rss")
    save_sources(in_memory_db, [source])

    item = NewsItem(
        id="1",
        source_id="tc",
        title="Event News",
        canonical_url="https://tc.com/event",
        published_date_utc=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
        raw_content="Content",
    )
    save_news_items(in_memory_db, [item])

    event = EventCluster(
        id="evt-1",
        reference_date=date(2026, 8, 16),
        title="Major Tech Event",
        main_topic_id="ai-ml",
        news_items=[item],
        news_item_ids=["1"],
        relevance_score=0.9,
        consolidated_summary="Summary of event",
        why_it_matters="Impact",
    )

    save_events(in_memory_db, [event])
    cursor = in_memory_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM events WHERE id = 'evt-1'")
    assert cursor.fetchone()[0] == 1
