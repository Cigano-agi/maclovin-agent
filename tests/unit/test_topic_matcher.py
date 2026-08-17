import pytest
from datetime import datetime, timezone

from maclovin.models import TopicConfig, NewsItem
from maclovin.ingestion.topic_matcher import match_topics_to_news, is_item_matching_topic


def test_topic_matching():
    topics = [
        TopicConfig(
            id="ai-ml",
            name="Inteligência Artificial",
            keywords=["AI", "LLM", "OpenAI", "DeepSeek", "Machine Learning"],
            active=True,
            priority=1,
        ),
        TopicConfig(
            id="gaming",
            name="Jogos e Entretenimento",
            keywords=["PlayStation", "Xbox", "Nintendo"],
            active=True,
            priority=2,
        ),
    ]

    item_ai = NewsItem(
        id="item-1",
        source_id="techcrunch",
        title="OpenAI announces new LLM agent capabilities",
        canonical_url="https://example.com/1",
        published_date_utc=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
        raw_content="The new model achieves high reasoning scores.",
    )

    item_gaming = NewsItem(
        id="item-2",
        source_id="techcrunch",
        title="Nintendo Switch 2 sales projections released",
        canonical_url="https://example.com/2",
        published_date_utc=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
        raw_content="Consoles are expected to sell well.",
    )

    item_unrelated = NewsItem(
        id="item-3",
        source_id="techcrunch",
        title="Local Bakery Wins Award for Best Sourdough",
        canonical_url="https://example.com/3",
        published_date_utc=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
        raw_content="Bread making takes time and patience.",
    )

    matched = match_topics_to_news([item_ai, item_gaming, item_unrelated], topics)

    assert len(matched) == 2
    assert matched[0].id == "item-1"
    assert "ai-ml" in matched[0].topic_ids
    assert matched[1].id == "item-2"
    assert "gaming" in matched[1].topic_ids
