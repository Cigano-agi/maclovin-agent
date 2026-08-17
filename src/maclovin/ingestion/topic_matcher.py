"""Deterministic topic and keyword matching for news items."""

import re
from typing import List
from maclovin.models import TopicConfig, NewsItem


def is_item_matching_topic(item: NewsItem, topic: TopicConfig) -> bool:
    """Verifica se o título ou conteúdo contém alguma das palavras-chave do tópico."""
    text_corpus = f"{item.title} {item.raw_content or ''}".lower()
    
    for kw in topic.keywords:
        kw_clean = kw.strip().lower()
        if not kw_clean:
            continue
        # Casamento por palavra inteira ou substring segura
        pattern = r"\b" + re.escape(kw_clean) + r"\b"
        if re.search(pattern, text_corpus, re.IGNORECASE):
            return True

    return False


def match_topics_to_news(items: List[NewsItem], topics: List[TopicConfig]) -> List[NewsItem]:
    """
    Associa cada notícia aos tópicos ativos correspondentes.
    Retorna apenas itens que correspondem a pelo menos um tópico ativo (ou todos se nenhum tópico for definido).
    """
    active_topics = [t for t in topics if t.active]
    if not active_topics:
        return items

    matched_items: List[NewsItem] = []

    for item in items:
        matched_topic_ids: List[str] = []
        highest_priority = 5

        for topic in active_topics:
            if is_item_matching_topic(item, topic):
                matched_topic_ids.append(topic.id)
                if topic.priority < highest_priority:
                    highest_priority = topic.priority

        if matched_topic_ids:
            item.topic_ids = matched_topic_ids
            # Score de relevância base proporcional à prioridade do tópico (1=1.0, 2=0.8, etc.)
            item.relevance_score = max(0.5, 1.0 - (highest_priority - 1) * 0.15)
            matched_items.append(item)

    return matched_items
