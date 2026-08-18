"""Deterministic & Semantic Category Classifier for Maclovin News.

Categorias suportadas:
- 'tools': Softwares, bibliotecas, repositórios GitHub, frameworks, APIs, modelos e extensões de código/produtividade.
- 'opportunities': Ideias de negócios, micro-SaaS, ferramentas para aplicar na empresa, soluções white-label, monetização e oportunidades B2B.
- 'business': Investimentos, valuation, Venture Capital, fusões e aquisições (M&A), startups, IPOs, lucros, demissões e mercado tech.
- 'news': Grandes anúncios do ecossistema de IA, regulação governamental, OpenAI, Google, Anthropic, novos modelos e debates.
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

OPPORTUNITY_KEYWORDS = [
    "oportunidade", "opportunity", "monetizar", "monetization", "como lucrar", "vender", "venda", "ideia de negócio",
    "business idea", "micro-saas", "micro saas", "side project", "indie hacker", "white-label", "white label",
    "automação empresarial", "solução para empresas", "reduzir custos", "para sua empresa", "aplicar no negócio",
    "mvp", "boilerplate", "template comercial", "b2b", "para clientes", "case de sucesso", "solução comercial",
    "como implementar na empresa", "transforme em produto",
]

BUSINESS_KEYWORDS = [
    "funding", "valuation", "venture capital", "vc", "round", "rodada", "investimento", "investors", "investidores",
    "m&a", "acquisition", "acquire", "adquire", "aquisição", "comprar", "comprou", "startup", "startups",
    "ipo", "lucro", "receita", "faturamento", "revenue", "quarter", "trimestre", "ações", "shares", "stock",
    "wall street", "demissão", "demissões", "layoff", "layoffs", "aporte", "aportou", "série a", "série b", "série c",
    "seed", "pre-seed", "unicórnio", "unicorn", "fintech", "market cap", "captação", "fundraise",
]

TOOL_KEYWORDS = [
    "tool", "ferramenta", "software", "open-source", "open source", "código aberto", "github", "repositório",
    "repository", "library", "biblioteca", "framework", "saas", "extension", "extensão", "plugin", "sdk", "api",
    "npm", "pypi", "docker", "release", "lançamento de ferramenta", "qwen", "llama", "whisper", "claude code",
    "cursor", "ollama", "vllm", "langchain", "llamaindex", "show hn",
]

MARKET_NEWS_KEYWORDS = [
    "ceo", "sam altman", "anthropic", "openai", "google", "meta", "nvidia", "processo", "regulação",
    "governo", "multa", "relatório", "anúncio oficial", "mercado de ia", "deepseek", "chatgpt",
]


def classify_category(title: str, text: str = "", source_category: str = "news") -> str:
    """Classifica a matéria na categoria correta: 'geek', 'learning', 'opportunities', 'business', 'tools' ou 'news'."""
    combined = f"{title} {text}".lower()

    # 1. Checagem prioritária para Cultura Geek & Games
    for kw in GEEK_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "geek"

    # 2. Checagem para Oportunidades de Negócio & Monetização
    for kw in OPPORTUNITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "opportunities"

    # 3. Checagem para Tutoriais e Aprendizado Técnico
    for kw in LEARNING_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "learning"

    # 4. Checagem para Business, Startups & Investimentos
    for kw in BUSINESS_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            return "business"

    # 5. Checagem para Ferramentas reais
    has_tool_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in TOOL_KEYWORDS)
    if has_tool_kw:
        return "tools"

    # 6. Checagem para Notícias de Mercado
    has_news_kw = any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in MARKET_NEWS_KEYWORDS)
    if has_news_kw:
        return "news"

    if source_category in ("geek", "learning", "opportunities", "tools", "business", "news"):
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
    
    topic_map = {
        "geek": "geek-culture",
        "opportunities": "market-opportunities",
        "learning": "tech-learning",
        "business": "tech-business",
        "tools": "ai-tools",
        "news": "ai-ml",
    }
    top_id = topic_map.get(cat, "ai-ml")
    if top_id not in item.topic_ids:
        item.topic_ids.append(top_id)
        
    return item
