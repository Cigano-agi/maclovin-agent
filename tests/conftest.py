import pytest
import sqlite3
from typing import List
from datetime import datetime, timezone

from maclovin.models import (
    TopicConfig,
    SourceConfig,
    NewsItem,
    EventCluster,
    ClassificationResult,
    SummaryResult,
    EventClusterResult,
    AppConfig,
    SettingsConfig,
    AIConfig,
)
from maclovin.intelligence.base import BaseLLMProvider


@pytest.fixture
def sample_config() -> AppConfig:
    return AppConfig(
        version="1.0",
        settings=SettingsConfig(
            timezone="America/Sao_Paulo",
            output_dir="briefings",
            database_path=":memory:",
            log_level="DEBUG",
        ),
        ai=AIConfig(
            provider="gemini",
            model="gemini-2.5-flash",
            temperature=0.1,
            timeout_seconds=10,
        ),
        topics=[
            TopicConfig(
                id="ai-ml",
                name="Inteligência Artificial",
                keywords=["AI", "LLM", "OpenAI", "Gemini", "Inteligência Artificial"],
                active=True,
                priority=1,
            ),
            TopicConfig(
                id="automation",
                name="Automação e Robótica",
                keywords=["Automação", "Robótica", "Agente"],
                active=True,
                priority=2,
            ),
        ],
        sources=[
            SourceConfig(
                id="techcrunch-ai",
                name="TechCrunch AI",
                ingestion_type="rss",
                url="https://techcrunch.com/category/artificial-intelligence/feed/",
                active=True,
                timeout_seconds=5,
            ),
            SourceConfig(
                id="theverge-ai",
                name="The Verge AI",
                ingestion_type="rss",
                url="https://www.theverge.com/rss/ai/index.xml",
                active=True,
                timeout_seconds=5,
            ),
        ],
    )


@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    # Initialize tables
    from maclovin.storage.database import init_db_schema
    init_db_schema(conn)
    yield conn
    conn.close()


@pytest.fixture
def sample_rss_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Tech News Feed</title>
    <link>https://example.com</link>
    <description>Daily tech news</description>
    <item>
      <title>OpenAI Announces Major GPT-5 Breakthrough in Reasoning</title>
      <link>https://example.com/openai-gpt5-breakthrough</link>
      <pubDate>Sun, 16 Aug 2026 14:30:00 +0000</pubDate>
      <description>OpenAI announced a major breakthrough in automated reasoning and LLM agent autonomy.</description>
    </item>
    <item>
      <title>Google Unveils Next-Gen AI Agent Platform</title>
      <link>https://example.com/google-next-gen-ai-agent</link>
      <pubDate>Sun, 16 Aug 2026 18:00:00 +0000</pubDate>
      <description>Google deepens its AI agent capabilities with seamless local execution.</description>
    </item>
    <item>
      <title>Old News from Last Week</title>
      <link>https://example.com/old-news</link>
      <pubDate>Mon, 10 Aug 2026 12:00:00 +0000</pubDate>
      <description>This should be excluded by the temporal filter.</description>
    </item>
  </channel>
</rss>
"""


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider for unit and integration testing."""

    def classify_news(self, title: str, text: str, topics: list) -> ClassificationResult:
        is_ai = any(kw.lower() in (title + " " + text).lower() for kw in ["openai", "google", "ai", "llm", "inteligência"])
        return ClassificationResult(
            is_relevant=is_ai,
            topic_ids=["ai-ml"] if is_ai else [],
            relevance_score=0.95 if is_ai else 0.1,
        )

    def summarize_news(self, title: str, text: str, topic_context: str) -> SummaryResult:
        return SummaryResult(
            title=title,
            summary=f"Resumo objetivo baseado no fato relatado: {title}.",
            why_it_matters="Acelera o desenvolvimento de novos modelos e ferramentas de IA.",
            insufficient_data=False,
        )

    def cluster_events(self, items: list) -> List[EventClusterResult]:
        if not items:
            return []
        return [
            EventClusterResult(
                event_title=items[0].title,
                main_topic_id=items[0].topic_ids[0] if items[0].topic_ids else "ai-ml",
                relevance_score=0.95,
                consolidated_summary=f"Fato consolidado a partir de {len(items)} matérias analisadas.",
                why_it_matters="Impacto relevante nos ecossistemas de desenvolvimento e automação.",
            )
        ]


@pytest.fixture
def mock_llm_provider() -> MockLLMProvider:
    return MockLLMProvider()
