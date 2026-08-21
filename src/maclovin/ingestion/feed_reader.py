"""Deterministic RSS/Atom feed parser and date-window filtering with SSRF and DoS protection."""

import datetime
from typing import List, Tuple, Optional
import feedparser

from maclovin.models import SourceConfig, NewsItem
from maclovin.core.clock import parse_iso_or_rfc_date, is_within_window
from maclovin.ingestion.normalizer import canonicalize_url, sanitize_title
from maclovin.ingestion.html_extractor import clean_html_text
from maclovin.ingestion.security import safe_fetch_url


def parse_feed_content(
    raw_xml: str,
    source: SourceConfig,
    start_utc: datetime.datetime,
    end_utc: datetime.datetime,
) -> List[NewsItem]:
    """Faz o parsing do XML do feed e filtra apenas os itens dentro da janela temporal."""
    feed = feedparser.parse(raw_xml)
    items: List[NewsItem] = []

    for entry in feed.entries:
        title = sanitize_title(entry.get("title", ""))
        if not title:
            continue

        raw_link = entry.get("link", "")
        if not raw_link:
            continue
        canonical_link = canonicalize_url(raw_link)

        # Determinar data de publicação
        published_dt = None
        for date_field in ("published", "pubDate", "updated", "created"):
            val = entry.get(date_field)
            if val:
                published_dt = parse_iso_or_rfc_date(val)
                if published_dt:
                    break

        if not published_dt and hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
            except Exception:
                published_dt = None

        if not published_dt and hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                published_dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
            except Exception:
                published_dt = None

        # Descartar se não estiver dentro da janela
        if not is_within_window(published_dt, start_utc, end_utc):
            continue

        # Extração de conteúdo / resumo bruto
        raw_content = ""
        if "summary" in entry:
            raw_content = clean_html_text(entry.summary)
        elif "description" in entry:
            raw_content = clean_html_text(entry.description)
        elif "content" in entry and len(entry.content) > 0:
            raw_content = clean_html_text(entry.content[0].get("value", ""))

        category = getattr(source, "category", "news")
        item_type = "tool" if category == "tools" else ("learning" if category == "learning" else ("geek" if category == "geek" else "news"))

        # Extract thumbnail / OG image from RSS entry
        thumbnail_url = None
        # Try media:thumbnail or media:content
        media_thumbnail = entry.get('media_thumbnail', [])
        if media_thumbnail and isinstance(media_thumbnail, list):
            thumbnail_url = media_thumbnail[0].get('url')
        if not thumbnail_url:
            media_content = entry.get('media_content', [])
            if media_content and isinstance(media_content, list):
                for mc in media_content:
                    if mc.get('medium') == 'image' or mc.get('type', '').startswith('image/'):
                        thumbnail_url = mc.get('url')
                        break
        # Try enclosures
        if not thumbnail_url:
            for enc in entry.get('enclosures', []):
                if enc.get('type', '').startswith('image/'):
                    thumbnail_url = enc.get('href') or enc.get('url')
                    break
        # Try first <img> in raw_content
        if not thumbnail_url and raw_content:
            import re as _re
            img_match = _re.search(r'https?://[^\s"\'>]+\.(?:jpg|jpeg|png|webp|gif)(?:[?][^\s"\'>]*)?', raw_content, _re.IGNORECASE)
            if img_match:
                thumbnail_url = img_match.group(0)

        item = NewsItem(
            id="",
            source_id=source.id,
            title=title,
            canonical_url=canonical_link,
            published_date_utc=published_dt,
            collected_date_utc=datetime.datetime.now(datetime.timezone.utc),
            raw_content=raw_content,
            item_type=item_type,
            thumbnail_url=thumbnail_url,
        )
        items.append(item)

    return items


def fetch_feed(
    source: SourceConfig,
    start_utc: datetime.datetime,
    end_utc: datetime.datetime,
) -> Tuple[List[NewsItem], List[str]]:
    """
    Coleta o feed remoto utilizando download seguro (proteção SSRF, validação de IP e limite de tamanho).
    Retorna (itens_coletados, lista_de_erros).
    """
    errors: List[str] = []
    if not source.active:
        return [], errors

    xml_text, error = safe_fetch_url(source.url, timeout=float(source.timeout_seconds))
    if error:
        errors.append(f"Falha ao consultar fonte '{source.name}' ({source.url}): {error}")
        return [], errors

    try:
        items = parse_feed_content(xml_text or "", source, start_utc, end_utc)
        return items, errors
    except Exception as e:
        errors.append(f"Erro ao processar conteúdo XML de '{source.name}': {e}")
        return [], errors
