"""URL canonicalization and metadata normalization utilities."""

import html
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "ref",
    "source",
    "rss",
    "ncid",
}


def canonicalize_url(raw_url: str) -> str:
    """
    Remove parâmetros de rastreamento de marketing (UTM, fbclid), fragmentos (#)
    e normaliza barras finais na URL.
    """
    if not raw_url:
        return ""

    parsed = urlparse(raw_url.strip())
    # Filtrar query params indesejados
    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    filtered_params = [(k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS]

    new_query = urlencode(filtered_params)
    clean_path = parsed.path.rstrip("/") if parsed.path != "/" else "/"

    canonical = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        clean_path,
        parsed.params,
        new_query,
        "",  # Remove fragment
    ))

    return canonical.rstrip("?")


def sanitize_title(raw_title: str) -> str:
    """Decodifica entidades HTML e limpa espaços extras no título."""
    if not raw_title:
        return ""
    
    unescaped = html.unescape(raw_title)
    # Substituir espaços não separáveis (&nbsp;)
    unescaped = unescaped.replace("\xa0", " ")
    # Normalizar múltiplos espaços em branco
    cleaned = re.sub(r"\s+", " ", unescaped).strip()
    return cleaned
