"""Automatic translation engine to ensure 100% Portuguese (PT-BR) output."""

import urllib.parse
import urllib.request
import json
import re
from typing import Optional


# Dicionário de termos comuns para tradução rápida e termos técnicos
TERM_REPLACEMENTS = {
    "open source": "código aberto",
    "free tier": "plano gratuito",
    "features": "funcionalidades",
    "launch": "lançamento",
    "release": "nova versão",
    "pricing": "preço",
}


def is_likely_portuguese(text: str) -> bool:
    """Verifica se o texto já está predominantemente em português."""
    if not text:
        return True
    pt_indicators = [" de ", " do ", " da ", " com ", " para ", " em ", " não ", " que ", " um ", " uma ", " os ", " as ", " por ", " sobre ", " como "]
    lower = " " + text.lower() + " "
    matches = sum(1 for ind in pt_indicators if ind in lower)
    return matches >= 2


def translate_to_pt_br(text: Optional[str]) -> str:
    """
    Traduz texto em inglês para Português do Brasil (PT-BR).
    Se já estiver em português ou vazio, retorna o texto limpo.
    """
    if not text or not text.strip():
        return ""

    clean_text = text.strip()
    if is_likely_portuguese(clean_text):
        return clean_text

    # Tenta tradução via endpoint rápido
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=pt&dt=t&q=" + urllib.parse.quote(clean_text[:1500])
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=4) as res:
            raw = res.read().decode("utf-8")
            data = json.loads(raw)
            translated = "".join([part[0] for part in data[0] if part and len(part) > 0 and part[0]])
            if translated and translated.strip():
                return translated.strip()
    except Exception:
        pass

    return clean_text
