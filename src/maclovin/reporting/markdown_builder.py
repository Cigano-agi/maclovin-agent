"""Markdown report builder for Daily News & Tools Briefings with HTML/Link sanitization."""

import pathlib
from datetime import datetime
from maclovin.models import BriefingReport, EventCluster, NewsItem
from maclovin.ingestion.security import sanitize_markdown_text, sanitize_url


def format_pricing_badge(pricing: str) -> str:
    """Retorna uma tag visual formatada para o modelo de preço."""
    pricing_lower = (pricing or "").lower()
    if "grátis" in pricing_lower or "open-source" in pricing_lower or "free" in pricing_lower:
        return "🟢 `[GRÁTIS / OPEN-SOURCE]`"
    elif "freemium" in pricing_lower:
        return "🟡 `[FREEMIUM]`"
    elif "pago" in pricing_lower or "paid" in pricing_lower:
        return "🔵 `[PAGO / COMERCIAL]`"
    else:
        return "⚪ `[ACESSO NÃO ESPECIFICADO]`"


def generate_markdown_report(report: BriefingReport) -> str:
    """Gera o documento Markdown estruturado e sanitizado a partir do BriefingReport."""
    lines = []
    lines.append(f"# Daily Intelligence Briefing: {report.reference_date.isoformat()}\n")
    lines.append(f"*Gerado em:* `{report.generated_at_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}`\n")
    lines.append("---\n")

    if report.alerts:
        lines.append("## ⚠️ Avisos Operacionais\n")
        for alert in report.alerts:
            lines.append(f"- {sanitize_markdown_text(alert)}")
        lines.append("\n---\n")

    has_tools = bool(report.tools_and_launches)
    has_news = bool(report.events or report.standalone_news)
    has_learning = bool(report.learning_items)
    has_geek = bool(report.geek_items)

    if not has_tools and not has_news and not has_learning and not has_geek:
        lines.append("## ℹ️ Nenhuma Atualização Relevante Encontrada\n")
        lines.append("Nenhum conteúdo publicado no período atendeu aos critérios dos tópicos configurados.\n")
        return "\n".join(lines)

    # 1. SEÇÃO DE FERRAMENTAS & LANÇAMENTOS (GRÁTIS E PAGAS)
    if has_tools:
        lines.append("## 🛠️ Radar de Ferramentas, Apps & Lançamentos\n")
        for idx, tool in enumerate(report.tools_and_launches, 1):
            badge = format_pricing_badge(tool.pricing_model)
            title = sanitize_markdown_text(tool.title)
            url = sanitize_url(tool.canonical_url)

            lines.append(f"### {idx}. {title}")
            lines.append(f"**Fonte:** `{sanitize_markdown_text(tool.source_id)}` | **Preço/Modelo:** {badge}\n")

            summary_text = sanitize_markdown_text(tool.summary or tool.title)
            lines.append(f"> **O que faz:** {summary_text}\n")

            if tool.why_it_matters:
                lines.append(f"💡 **Valor prático:** {sanitize_markdown_text(tool.why_it_matters)}\n")

            if tool.key_features:
                lines.append("**Destaques & Funcionalidades:**")
                for feat in tool.key_features:
                    lines.append(f"- {sanitize_markdown_text(feat)}")
                lines.append("")

            lines.append(f"🔗 **Link Direto:** [{url}]({url})\n")
            lines.append("---\n")

    # 2. SEÇÃO DE APRENDER TECNOLOGIA & DEEP DIVES
    if has_learning:
        lines.append("## 📚 Aprender Tecnologia & Deep Dives\n")
        for idx, item in enumerate(report.learning_items, 1):
            title = sanitize_markdown_text(item.title)
            url = sanitize_url(item.canonical_url)
            lines.append(f"### {idx}. {title}")
            lines.append(f"**Fonte:** `{sanitize_markdown_text(item.source_id)}`\n")
            if item.summary:
                lines.append(f"> {sanitize_markdown_text(item.summary)}\n")
            if item.why_it_matters:
                lines.append(f"💡 **O que você aprende:** {sanitize_markdown_text(item.why_it_matters)}\n")
            lines.append(f"🔗 **Link:** [{url}]({url})\n")
            lines.append("---\n")

    # 3. SEÇÃO DO UNIVERSO GEEK & NERD
    if has_geek:
        lines.append("## 🎮 Universo Geek & Nerd\n")
        for idx, item in enumerate(report.geek_items, 1):
            title = sanitize_markdown_text(item.title)
            url = sanitize_url(item.canonical_url)
            lines.append(f"### {idx}. {title}")
            lines.append(f"**Fonte:** `{sanitize_markdown_text(item.source_id)}`\n")
            if item.summary:
                lines.append(f"> {sanitize_markdown_text(item.summary)}\n")
            if item.why_it_matters:
                lines.append(f"💡 **Destaque Nerd:** {sanitize_markdown_text(item.why_it_matters)}\n")
            lines.append(f"🔗 **Link:** [{url}]({url})\n")
            lines.append("---\n")

    # 4. SEÇÃO DE NOTÍCIAS E ACONTECIMENTOS GERAIS
    if has_news:
        lines.append("## 📰 Principais Notícias & Acontecimentos do Setor\n")

        if report.events:
            for idx, event in enumerate(report.events, 1):
                event_title = sanitize_markdown_text(event.title)
                lines.append(f"### {idx}. {event_title}")
                lines.append(f"**Tópico:** `{sanitize_markdown_text(event.main_topic_id)}` | **Relevância:** `{int(event.relevance_score * 100)}%`\n")
                lines.append(f"> {sanitize_markdown_text(event.consolidated_summary)}\n")

                if event.why_it_matters:
                    lines.append(f"💡 **Por que importa:** {sanitize_markdown_text(event.why_it_matters)}\n")

                if event.news_items:
                    lines.append("**Fontes e Matérias:**")
                    for item in event.news_items:
                        item_title = sanitize_markdown_text(item.title)
                        item_url = sanitize_url(item.canonical_url)
                        lines.append(f"- [{item_title}]({item_url}) — *{sanitize_markdown_text(item.source_id)}* ({item.published_date_utc.strftime('%H:%M UTC')})")
                lines.append("\n---\n")

        elif report.standalone_news:
            for idx, item in enumerate(report.standalone_news, 1):
                title = sanitize_markdown_text(item.title)
                url = sanitize_url(item.canonical_url)
                lines.append(f"### {idx}. {title}")
                lines.append(f"**Fonte:** `{sanitize_markdown_text(item.source_id)}` | **Data:** `{item.published_date_utc.strftime('%Y-%m-%d %H:%M UTC')}`\n")
                
                if item.summary:
                    lines.append(f"> {sanitize_markdown_text(item.summary)}\n")
                
                if item.why_it_matters:
                    lines.append(f"💡 **Por que importa:** {sanitize_markdown_text(item.why_it_matters)}\n")

                lines.append(f"🔗 **Link Original:** [{url}]({url})\n")
                lines.append("---\n")

    # Estatísticas de execução no rodapé
    lines.append("## 📊 Estatísticas da Coleta")
    stats = report.execution_stats
    lines.append(f"- **Fontes Consultadas:** {stats.get('sources_ok', 0)}")
    lines.append(f"- **Ferramentas Catalogadas:** {stats.get('tools_count', len(report.tools_and_launches))}")
    lines.append(f"- **Deep Dives & Tutoriais:** {stats.get('learning_count', len(report.learning_items))}")
    lines.append(f"- **Geek & Hardware:** {stats.get('geek_count', len(report.geek_items))}")
    lines.append(f"- **Notícias Analisadas:** {stats.get('news_count', len(report.standalone_news) + len(report.events))}")
    if "execution_time_sec" in stats:
        lines.append(f"- **Tempo de Processamento:** {stats.get('execution_time_sec', 0):.2f}s")

    lines.append("\n\n*Relatório gerado automaticamente por Maclovin Intelligence Platform.*")
    return "\n".join(lines)


def save_markdown_report(report: BriefingReport, output_dir: str = "briefings") -> str:
    """Salva o briefing gerado em disco no caminho `output_dir/YYYY-MM-DD.md`."""
    out_dir = pathlib.Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{report.reference_date.isoformat()}.md"
    file_path = out_dir / filename

    content = generate_markdown_report(report)
    file_path.write_text(content, encoding="utf-8")
    return str(file_path.resolve())
