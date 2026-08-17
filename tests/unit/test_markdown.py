import pytest
from datetime import date, datetime, timezone
import tempfile
import pathlib

from maclovin.models import BriefingReport, EventCluster, NewsItem
from maclovin.reporting.markdown_builder import generate_markdown_report, save_markdown_report


def test_generate_markdown_report_with_tools_and_news():
    tool_item = NewsItem(
        id="tool-1",
        source_id="product-hunt-ai",
        title="SuperDev AI — Open Source Coding Agent",
        canonical_url="https://github.com/superdev/ai",
        published_date_utc=datetime(2026, 8, 16, 10, 0, 0, tzinfo=timezone.utc),
        item_type="tool",
        pricing_model="Grátis / Open-Source",
        key_features=["Suporte a multi-repositórios", "100% local e privado"],
        summary="Um assistente de programação local que automatiza testes e refatorações.",
        why_it_matters="Aumenta a produtividade de engenharia sem custo de licença.",
    )

    news_item = NewsItem(
        id="news-1",
        source_id="techcrunch-ai",
        title="OpenAI Lança Novo Modelo com Foco em Raciocínio",
        canonical_url="https://techcrunch.com/openai-reasoning-model",
        published_date_utc=datetime(2026, 8, 16, 14, 0, 0, tzinfo=timezone.utc),
        relevance_score=0.95,
        summary="A OpenAI apresentou um novo modelo focado em problemas complexos.",
        why_it_matters="Reduz o custo computacional e melhora a autonomia de agentes.",
    )

    event = EventCluster(
        id="event-1",
        reference_date=date(2026, 8, 16),
        title="Nova Geração de Modelos de Raciocínio da OpenAI",
        main_topic_id="ai-ml",
        news_items=[news_item],
        news_item_ids=["news-1"],
        relevance_score=0.95,
        consolidated_summary="A OpenAI lançou uma nova família de modelos de raciocínio avançado.",
        why_it_matters="Impacto direto em automação e agentes inteligentes autônomos.",
    )

    report = BriefingReport(
        id="2026-08-16",
        reference_date=date(2026, 8, 16),
        events=[event],
        tools_and_launches=[tool_item],
        standalone_news=[],
        execution_stats={"sources_ok": 4, "total_news": 2},
        alerts=[],
    )

    md = generate_markdown_report(report)

    assert "# Daily Intelligence Briefing: 2026-08-16" in md
    assert "## 🛠️ Radar de Ferramentas, Apps & Lançamentos" in md
    assert "SuperDev AI" in md
    assert "GRÁTIS / OPEN-SOURCE" in md
    assert "https://github.com/superdev/ai" in md
    assert "## 📰 Principais Notícias & Acontecimentos do Setor" in md
    assert "Nova Geração de Modelos de Raciocínio" in md


def test_save_markdown_report():
    report = BriefingReport(
        id="2026-08-16",
        reference_date=date(2026, 8, 16),
        events=[],
        tools_and_launches=[],
        standalone_news=[],
        execution_stats={"sources_ok": 1, "total_news": 0},
        alerts=["Nenhuma notícia relevante encontrada no período."],
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = save_markdown_report(report, output_dir=tmp_dir)
        p = pathlib.Path(out_path)
        assert p.exists()
        assert "2026-08-16.md" in p.name
        content = p.read_text(encoding="utf-8")
        assert "Nenhuma Atualização Relevante Encontrada" in content
