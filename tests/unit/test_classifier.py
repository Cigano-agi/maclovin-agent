import pytest
from datetime import datetime, timezone

from maclovin.models import NewsItem, TopicConfig
from maclovin.intelligence.classifier import refine_with_llm, sort_by_relevance


def test_sort_by_relevance():
    item1 = NewsItem(
        id="1",
        source_id="tc",
        title="Low relevance",
        canonical_url="https://tc.com/1",
        published_date_utc=datetime.now(timezone.utc),
        relevance_score=0.4,
    )
    item2 = NewsItem(
        id="2",
        source_id="tc",
        title="High relevance",
        canonical_url="https://tc.com/2",
        published_date_utc=datetime.now(timezone.utc),
        relevance_score=0.95,
    )
    sorted_items = sort_by_relevance([item1, item2])
    assert sorted_items[0].id == "2"
    assert sorted_items[1].id == "1"


def test_refine_with_llm(mock_llm_provider, sample_config):
    item = NewsItem(
        id="1",
        source_id="tc",
        title="OpenAI announces GPT-5 release",
        canonical_url="https://tc.com/1",
        published_date_utc=datetime.now(timezone.utc),
        raw_content="Advanced AI model released.",
    )
    refined = refine_with_llm([item], sample_config.topics, mock_llm_provider)
    assert len(refined) == 1
    assert refined[0].relevance_score == 0.95
    assert "ai-ml" in refined[0].topic_ids
