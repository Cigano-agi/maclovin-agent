import pytest
from datetime import datetime, timezone, date

from maclovin.models import NewsItem, TopicConfig
from maclovin.ingestion.deduplicator import compute_content_hash, deduplicate_items
from maclovin.intelligence.clusterer import cluster_with_llm


def test_compute_content_hash():
    item1 = NewsItem(
        id="1",
        source_id="tc",
        title="OpenAI Releases New Model",
        canonical_url="https://tc.com/1",
        published_date_utc=datetime.now(timezone.utc),
        raw_content="Major release of GPT-5",
    )
    item2 = NewsItem(
        id="2",
        source_id="verge",
        title="OpenAI Releases New Model",
        canonical_url="https://verge.com/2",
        published_date_utc=datetime.now(timezone.utc),
        raw_content="Major release of GPT-5",
    )
    # Identical title and content yield the same content hash
    assert item1.content_hash == item2.content_hash


def test_deduplicate_items():
    item1 = NewsItem(
        id="1",
        source_id="tc",
        title="Title A",
        canonical_url="https://tc.com/a",
        published_date_utc=datetime.now(timezone.utc),
        raw_content="Body text",
    )
    item2 = NewsItem(
        id="2",
        source_id="tc-mirror",
        title="Title A",
        canonical_url="https://tc.com/a",  # Duplicate URL
        published_date_utc=datetime.now(timezone.utc),
        raw_content="Body text",
    )
    unique, duplicates_count = deduplicate_items([item1, item2])
    assert len(unique) == 1
    assert duplicates_count == 1


def test_cluster_with_llm(mock_llm_provider):
    item1 = NewsItem(
        id="1",
        source_id="tc",
        title="OpenAI Releases GPT-5",
        canonical_url="https://tc.com/1",
        published_date_utc=datetime.now(timezone.utc),
        topic_ids=["ai-ml"],
        raw_content="Article from TechCrunch",
    )
    item2 = NewsItem(
        id="2",
        source_id="verge",
        title="OpenAI Unveils GPT-5 Reasoning",
        canonical_url="https://verge.com/2",
        published_date_utc=datetime.now(timezone.utc),
        topic_ids=["ai-ml"],
        raw_content="Article from The Verge",
    )

    clusters = cluster_with_llm([item1, item2], ref_date=date(2026, 8, 16), provider=mock_llm_provider)

    assert len(clusters) == 1
    assert clusters[0].title == "OpenAI Releases GPT-5"
    assert len(clusters[0].news_items) == 2
