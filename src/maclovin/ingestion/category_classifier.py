"""Deterministic & Semantic Category Classifier for Maclovin News.

Categorias suportadas:
- 'tools': Softwares, bibliotecas, repositórios GitHub, frameworks, APIs, modelos e extensões de código/produtividade.
- 'news': Notícias de mercado, grandes aquisições, regulação, OpenAI, Google, Anthropic, startups e investimentos.
- 'learning': Tutoriais, arquitetura de sistemas, deep dives, papers, guias técnicos e engenharia.
- 'geek': Games, consoles (PS5, Xbox, Nintendo), Steam, filmes, séries, trailers, HQs, quadrinhos, mangás, animes e cultura pop.
"""

import re
from typing import Optional, Tuple
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
    "cursor", "ollama", "vllm", "langchain", "llamaindex", "show hn",
]

MARKET_NEWS_KEYWORDS = [
    "acquire", "adquire", "aquisição", "investimento", "startup", "valuation", "demissão", "layoff", "disband",
    "ceo", "sam altman", "anthropic", "openai", "google", "meta", "nvidia", "processo", "regulação",
    "governo", "multa", "receita", "faturamento", "relatório", "anúncio oficial", "mercado de ia",
]


def classify_category(title: str, text: str = "", source_category: str = "news") -> str:
    """Classifica a matéria na categoria correta: 'geek', 'learning', 'tools' ou 'news'."""
    combined = f"{title} {text}".lower()

    # 1. Checagem prioritária para Cultura Geek & Games
    for kw in GEEK_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "geek"

    # 2. Checagem para Tutoriais e Aprendizado Técnico
    for kw in LEARNING_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "learning"

    # 3. Checagem para Ferramentas reais
    has_tool_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in TOOL_KEYWORDS)
    if has_tool_kw:
        return "tools"

    # 4. Checagem para Notícias de Mercado
    has_news_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in MARKET_NEWS_KEYWORDS)
    if has_news_kw:
        return "news"

    if source_category in ("geek", "learning", "tools", "news"):
        return source_category

    return "news"


def classify_tool_subtype(title: str, text: str = "", url: str = "") -> str:
    """Classifica uma ferramenta como 'repo' (Repositório GitHub/Open-Source) ou 'app' (Software/SaaS)."""
    combined = f"{title} {text} {url}".lower()
    if "github.com" in combined or "gitlab.com" in combined or "huggingface.co" in combined or "repositório" in combined or "repository" in combined or "código aberto" in combined or "open-source" in combined or "open source" in combined:
        return "repo"
    return "app"


def refine_item_category(item: NewsItem, default_source_cat: str = "news") -> NewsItem:
    """Atualiza a categoria, item_type e tool_subtype de um NewsItem."""
    cat = classify_category(item.title, item.raw_content or item.summary or "", default_source_cat)
    item.item_type = "tool" if cat == "tools" else cat
    if cat == "tools":
        item.tool_subtype = classify_tool_subtype(item.title, item.raw_content or item.summary or "", item.canonical_url)
    if cat == "geek" and "geek-culture" not in item.topic_ids:
        item.topic_ids.append("geek-culture")
    elif cat == "learning" and "tech-learning" not in item.topic_ids:
        item.topic_ids.append("tech-learning")
    elif cat == "tools" and "ai-tools" not in item.topic_ids:
        item.topic_ids.append("ai-tools")
    elif cat == "news" and "ai-ml" not in item.topic_ids:
        item.topic_ids.append("ai-ml")
    return item
