"""Clean HTML text extraction fallback (ethical scraping without paywall bypass)."""

import re
from bs4 import BeautifulSoup


def clean_html_text(raw_html: str) -> str:
    """
    Remove tags HTML, scripts, estilos e formata o texto em linhas legíveis.
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove elementos não textuais
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # Normalizar espaços e quebras
    text = re.sub(r"\s+", " ", text).strip()
    return text
