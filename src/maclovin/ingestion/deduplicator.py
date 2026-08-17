"""Deterministic deduplication and content hashing utilities."""

import hashlib
from typing import List, Tuple, Dict
from maclovin.models import NewsItem


def compute_content_hash(title: str, text: str) -> str:
    """Calcula SHA-256 a partir do título e corpo normalizado."""
    payload = f"{title.strip().lower()} {text.strip().lower()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def deduplicate_items(items: List[NewsItem]) -> Tuple[List[NewsItem], int]:
    """
    Remove itens com URLs canônicas duplicadas ou mesmo hash de conteúdo exato.
    Retorna a lista desduplicada e a quantidade de duplicatas descartadas.
    """
    seen_urls = set()
    seen_hashes = set()
    unique_items: List[NewsItem] = []
    duplicates_count = 0

    for item in items:
        if item.canonical_url in seen_urls or (item.content_hash and item.content_hash in seen_hashes):
            duplicates_count += 1
            continue

        seen_urls.add(item.canonical_url)
        if item.content_hash:
            seen_hashes.add(item.content_hash)

        unique_items.append(item)

    return unique_items, duplicates_count
