import pytest
from datetime import datetime, timezone

from maclovin.models import NewsItem
from maclovin.intelligence.summarizer import summarize_item, summarize_all


def test_summarize_item(mock_llm_provider):
    item = NewsItem(
        id="1",
        source_id="tc",
        title="OpenAI Lança Novo Modelo GPT-5",
        canonical_url="https://tc.com/1",
        published_date_utc=datetime.now(timezone.utc),
        raw_content="A OpenAI anunciou hoje seu novo modelo de linguagem focado em raciocínio.",
    )

    summarized = summarize_item(item, topic_name="Inteligência Artificial", provider=mock_llm_provider)

    assert summarized.summary is not None
    assert "Resumo objetivo" in summarized.summary
    assert summarized.why_it_matters is not None
    assert "Acelera" in summarized.why_it_matters


def test_summarize_all(mock_llm_provider):
    items = [
        NewsItem(
            id=str(i),
            source_id="tc",
            title=f"Notícia {i}",
            canonical_url=f"https://tc.com/{i}",
            published_date_utc=datetime.now(timezone.utc),
            raw_content=f"Conteúdo da notícia {i}",
        )
        for i in range(3)
    ]

    summarized_items = summarize_all(items, topic_name="AI", provider=mock_llm_provider)
    assert len(summarized_items) == 3
    for it in summarized_items:
        assert it.summary is not None
