"""Strict grounding summarizer avoiding hallucinations and extracting PT-BR summaries, tools metadata, and translated titles."""

from typing import List, Optional
from maclovin.models import NewsItem, SummaryResult
from maclovin.intelligence.base import BaseLLMProvider


def summarize_item(
    item: NewsItem,
    topic_name: str,
    provider: BaseLLMProvider,
) -> NewsItem:
    """
    Gera resumo factual, contextualização de impacto e tradução para Português (PT-BR)
    seguindo o princípio de Strict Grounding (Anti-Alucinação).
    """
    try:
        res: SummaryResult = provider.summarize_news(
            title=item.title,
            text=item.raw_content or item.title,
            topic_context=topic_name,
        )
        if res.title and res.title.strip():
            item.title = res.title.strip()
        item.summary = res.summary
        item.why_it_matters = res.why_it_matters
        if res.item_type:
            item.item_type = res.item_type
        if res.pricing_model:
            item.pricing_model = res.pricing_model
        if res.key_features:
            item.key_features = res.key_features
    except Exception:
        item.summary = item.title
        item.why_it_matters = "Acompanhamento relevante para os tópicos selecionados."

    return item


def summarize_all(
    items: List[NewsItem],
    topic_name: str,
    provider: BaseLLMProvider,
) -> List[NewsItem]:
    """Sumariza e traduz uma lista de notícias e matérias em lote."""
    return [summarize_item(item, topic_name, provider) for item in items]
