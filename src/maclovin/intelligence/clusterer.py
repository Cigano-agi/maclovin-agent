"""Event clustering using LLM adapter."""

import uuid
from datetime import date
from typing import List, Dict
from maclovin.models import NewsItem, EventCluster, EventClusterResult
from maclovin.intelligence.base import BaseLLMProvider


def cluster_with_llm(
    items: List[NewsItem],
    ref_date: date,
    provider: BaseLLMProvider,
) -> List[EventCluster]:
    """
    Utiliza o adaptador de IA para agrupar múltiplas matérias sobre o mesmo acontecimento
    em entidades EventCluster estruturadas.
    """
    if not items:
        return []

    cluster_results: List[EventClusterResult] = provider.cluster_events(items)
    
    events: List[EventCluster] = []
    
    # Se o LLM retornou exatamente 1 cluster consolidado para o conjunto
    if len(cluster_results) == 1:
        res = cluster_results[0]
        event = EventCluster(
            id=str(uuid.uuid4())[:8],
            reference_date=ref_date,
            title=res.event_title,
            main_topic_id=res.main_topic_id,
            news_items=items,
            news_item_ids=[it.id for it in items],
            relevance_score=res.relevance_score,
            consolidated_summary=res.consolidated_summary,
            why_it_matters=res.why_it_matters,
        )
        return [event]

    # Múltiplos clusters: associar itens por título e tópicos
    title_to_item: Dict[str, NewsItem] = {it.title.strip().lower(): it for it in items}

    for res in cluster_results:
        event_id = str(uuid.uuid4())[:8]
        matched_item = title_to_item.get(res.event_title.strip().lower())
        associated_items = [matched_item] if matched_item else [it for it in items if it.title in res.event_title or res.event_title in it.title]
        if not associated_items:
            associated_items = items[:1]

        event = EventCluster(
            id=event_id,
            reference_date=ref_date,
            title=res.event_title,
            main_topic_id=res.main_topic_id,
            news_items=associated_items,
            news_item_ids=[it.id for it in associated_items],
            relevance_score=res.relevance_score,
            consolidated_summary=res.consolidated_summary,
            why_it_matters=res.why_it_matters,
        )
        events.append(event)

    return events
