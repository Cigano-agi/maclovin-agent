"""Deterministic & Semantic Category Classifier for Maclovin News.

Categorias suportadas:
- 'tools': Softwares, bibliotecas, repositórios GitHub, frameworks, APIs, modelos e extensões de código/produtividade.
- 'news': Notícias de mercado, grandes aquisições, regulação, OpenAI, Google, Anthropic, startups e investimentos.
- 'learning': Tutoriais, arquitetura de sistemas, deep dives, papers, guias técnicos e engenharia.
- 'geek': Games, consoles (PS5, Xbox, Nintendo), Steam, filmes, séries, trailers, HQs, quadrinhos, mangás, animes e cultura pop.
"""

import re
from typing import Optional
from maclovin.models import NewsItem


GEEK_KEYWORDS = [
    "game", "jogos", "jogo", "gameplay", "gamer", "playstation", "ps5", "ps4", "xbox", "nintendo", "switch",
    "steam", "gta", "rpg", "filme", "filmes", "cinema", "movie", "série", "series", "trailer", "teaser",
    "hq", "hqs", "quadrinho", "quadrinhos", "comic", "comics", "mangá", "manga", "anime", "animes",
    "marvel", "dc", "batman", "superman", "vingadores", "star wars", "geek", "nerd", "cosplay",
    "rtx", "geforce", "radeon", "gpu gamer", "intel core", "ryzen", "alienware", "steam deck",
]

LEARNING_KEYWORDS = [
    "tutorial", "como criar", "como construir", "how to", "guide", "guia", "passo a passo", "step by step",
    "arquitetura", "architecture", "deep dive", "deep-dive", "paper", "whitepaper", "benchmark", "benchmarks",
    "como funciona", "how it works", "best practices", "boas práticas", "roadmap", "cheatsheet", "handbook",
    "system design", "design de sistemas", "engenharia de software", "aprenda", "curso", "explorando",
]

TOOL_KEYWORDS = [
    "tool", "ferramenta", "software", "open-source", "open source", "código aberto", "github", "repositório",
    "repository", "library", "biblioteca", "framework", "saas", "extension", "extensão", "plugin", "sdk", "api",
    "npm", "pypi", "docker", "release", "lançamento de ferramenta", "qwen", "llama", "whisper", "claude code",
    "cursor", "ollama", "vllm", "langchain", "llamaindex",
]

MARKET_NEWS_KEYWORDS = [
    "acquire", "adquire", "aquisição", "investimento", "startup", "valuation", "demissão", "layoff", "disband",
    "ceo", "sam altman", "anthropic", "openai", "google", "meta", "nvidia", "processo", "regulação",
    "governo", "multa", "receita", "faturamento", "relatório", "anúncio oficial", "mercado de ia",
]


def classify_category(title: str, text: str = "", source_category: str = "news") -> str:
    """
    Classifica a matéria de forma rigorosa e determinística na categoria correta.
    Retorna: 'geek', 'learning', 'tools' ou 'news'.
    """
    combined = f"{title} {text}".lower()

    # 1. Checagem prioritária para Cultura Geek & Games (evita que games caiam em ferramentas)
    for kw in GEEK_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "geek"

    # 2. Checagem para Tutoriais, Deep Dives e Aprendizado Técnico
    for kw in LEARNING_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "learning"

    # 3. Checagem para Ferramentas reais de software/código/modelos
    has_tool_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in TOOL_KEYWORDS)
    if has_tool_kw:
        return "tools"

    # 4. Checagem para Notícias de Mercado e Empresas de IA
    has_news_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in MARKET_NEWS_KEYWORDS)
    if has_news_kw:
        return "news"

    # 5. Se a fonte tiver uma categoria padrão confiável, usa
    if source_category in ("geek", "learning", "tools", "news"):
        return source_category

    return "news"


def refine_item_category(item: NewsItem, default_source_cat: str = "news") -> NewsItem:
    """Atualiza a categoria e item_type de um NewsItem com base na classificação estrita."""
    cat = classify_category(item.title, item.raw_content or item.summary or "", default_source_cat)
    item.item_type = "tool" if cat == "tools" else cat
    if cat == "geek" and "geek-culture" not in item.topic_ids:
        item.topic_ids.append("geek-culture")
    elif cat == "learning" and "tech-learning" not in item.topic_ids:
        item.topic_ids.append("tech-learning")
    elif cat == "tools" and "ai-tools" not in item.topic_ids:
        item.topic_ids.append("ai-tools")
    elif cat == "news" and "ai-ml" not in item.topic_ids:
        item.topic_ids.append("ai-ml")
    return item
