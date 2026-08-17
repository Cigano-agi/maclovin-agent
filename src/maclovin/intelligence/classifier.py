"""Semantic classification and relevance scoring."""

from typing import List
from maclovin.models import NewsItem, TopicConfig, ClassificationResult
from maclovin.intelligence.base import BaseLLMProvider


def sort_by_relevance(items: List[NewsItem]) -> List[NewsItem]:
    """Ordena itens de notícias por score de relevância decrescente."""
    return sorted(items, key=lambda x: x.relevance_score, reverse=True)


def refine_with_llm(
    items: List[NewsItem],
    topics: List[TopicConfig],
    provider: BaseLLMProvider,
) -> List[NewsItem]:
    """
    Refina o score de relevância e os tópicos associados a cada notícia usando LLM.
    Descarta itens classificados como não relevantes pelo modelo.
    """
    refined: List[NewsItem] = []

    for item in items:
        try:
            result: ClassificationResult = provider.classify_news(
                title=item.title,
                text=item.raw_content or "",
                topics=topics,
            )
            if result.is_relevant:
                item.topic_ids = result.topic_ids
                item.relevance_score = result.relevance_score
                refined.append(item)
        except Exception:
            # Em caso de falha individual de IA, preserva o item com pontuação heurística
            refined.append(item)

    return sort_by_relevance(refined)
