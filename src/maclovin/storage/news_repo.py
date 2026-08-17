"""Repository for persisting sources, news items, and consolidated events in SQLite."""

import sqlite3
import json
from datetime import date, datetime, timezone
from typing import List, Tuple
from maclovin.models import NewsItem, EventCluster, SourceConfig


def save_sources(conn: sqlite3.Connection, sources: List[SourceConfig]) -> None:
    """Insere ou atualiza as fontes de dados configuradas."""
    cursor = conn.cursor()
    for s in sources:
        cursor.execute(
            """
            INSERT INTO sources (id, name, ingestion_type, url, active, category)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                ingestion_type=excluded.ingestion_type,
                url=excluded.url,
                active=excluded.active,
                category=excluded.category;
            """,
            (s.id, s.name, s.ingestion_type, s.url, 1 if s.active else 0, getattr(s, "category", "news")),
        )
    conn.commit()


def save_news_items(conn: sqlite3.Connection, items: List[NewsItem]) -> Tuple[int, int]:
    """
    Persiste notícias e ferramentas coletadas no SQLite garantindo idempotência via INSERT OR IGNORE.
    Retorna (itens_inseridos, duplicatas_ignoradas).
    """
    cursor = conn.cursor()
    inserted_count = 0
    duplicates_count = 0

    for item in items:
        cursor.execute("SELECT id FROM sources WHERE id = ?", (item.source_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT OR IGNORE INTO sources (id, name, ingestion_type, url, active, category) VALUES (?, ?, ?, ?, ?, ?)",
                (item.source_id, item.source_id, "rss", item.canonical_url, 1, "news"),
            )

        features_json = json.dumps(item.key_features, ensure_ascii=False) if item.key_features else None

        cursor.execute(
            """
            INSERT OR IGNORE INTO news_items (
                id, source_id, title, canonical_url, published_date_utc,
                collected_date_utc, raw_content, content_hash,
                relevance_score, item_type, pricing_model, key_features,
                summary, why_it_matters
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.source_id,
                item.title,
                item.canonical_url,
                item.published_date_utc.isoformat(),
                item.collected_date_utc.isoformat(),
                item.raw_content,
                item.content_hash,
                item.relevance_score,
                item.item_type,
                item.pricing_model,
                features_json,
                item.summary,
                item.why_it_matters,
            ),
        )
        if cursor.rowcount > 0:
            inserted_count += 1
        else:
            duplicates_count += 1

    conn.commit()
    return inserted_count, duplicates_count


def save_events(conn: sqlite3.Connection, events: List[EventCluster]) -> None:
    """Insere ou atualiza eventos consolidados e seus relacionamentos com notícias."""
    cursor = conn.cursor()

    for event in events:
        cursor.execute(
            """
            INSERT OR REPLACE INTO events (
                id, reference_date, title, main_topic_id,
                relevance_score, consolidated_summary, why_it_matters
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.reference_date.isoformat(),
                event.title,
                event.main_topic_id,
                event.relevance_score,
                event.consolidated_summary,
                event.why_it_matters,
            ),
        )

        for news_id in event.news_item_ids:
            cursor.execute(
                "INSERT OR IGNORE INTO event_news_items (event_id, news_item_id) VALUES (?, ?)",
                (event.id, news_id),
            )

    conn.commit()


def get_news_by_date(conn: sqlite3.Connection, target_date: date) -> List[NewsItem]:
    """Busca todas as notícias gravadas para uma determinada data de publicação."""
    cursor = conn.cursor()
    date_str = target_date.isoformat()
    cursor.execute(
        "SELECT id, source_id, title, canonical_url, published_date_utc, collected_date_utc, raw_content, content_hash, relevance_score, item_type, pricing_model, key_features, summary, why_it_matters FROM news_items WHERE date(published_date_utc) = ?",
        (date_str,),
    )
    rows = cursor.fetchall()
    items: List[NewsItem] = []

    for r in rows:
        if isinstance(r, sqlite3.Row):
            d = dict(r)
        else:
            cols = [c[0] for c in cursor.description]
            d = dict(zip(cols, r))

        pub_dt = datetime.fromisoformat(d["published_date_utc"])
        col_dt = datetime.fromisoformat(d["collected_date_utc"])
        raw_feat = d.get("key_features")
        features = json.loads(raw_feat) if raw_feat else []

        item = NewsItem(
            id=d["id"],
            source_id=d["source_id"],
            title=d["title"],
            canonical_url=d["canonical_url"],
            published_date_utc=pub_dt,
            collected_date_utc=col_dt,
            raw_content=d["raw_content"],
            content_hash=d["content_hash"],
            relevance_score=d.get("relevance_score") or 0.0,
            item_type=d.get("item_type") or "news",
            pricing_model=d.get("pricing_model") or "Não especificado",
            key_features=features,
            summary=d.get("summary"),
            why_it_matters=d.get("why_it_matters"),
        )
        items.append(item)

    return items
