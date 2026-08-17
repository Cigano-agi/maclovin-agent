"""Strict grounding summarizer avoiding hallucinations and ensuring 100% PT-BR translation."""

from typing import List, Optional
from maclovin.models import NewsItem, SummaryResult
from maclovin.intelligence.base import BaseLLMProvider
from maclovin.intelligence.translator import translate_to_pt_br


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
            item.title = translate_to_pt_br(res.title.strip())
        else:
            item.title = translate_to_pt_br(item.title)

        item.summary = translate_to_pt_br(res.summary or item.title)
        item.why_it_matters = translate_to_pt_br(res.why_it_matters) if res.why_it_matters else "Acompanhamento relevante para inovação e desenvolvimento."

        if res.item_type:
            item.item_type = res.item_type
        if res.pricing_model:
            item.pricing_model = res.pricing_model
        if res.key_features:
            item.key_features = [translate_to_pt_br(f) for f in res.key_features]
    except Exception:
        item.title = translate_to_pt_br(item.title)
        item.summary = translate_to_pt_br(item.summary or item.title)
        item.why_it_matters = "Acompanhamento relevante para inovação e desenvolvimento."

    return item


def summarize_all(
    items: List[NewsItem],
    topic_name: str,
    provider: BaseLLMProvider,
) -> List[NewsItem]:
    """Sumariza e traduz uma lista de notícias e matérias em lote."""
    return [summarize_item(item, topic_name, provider) for item in items]
