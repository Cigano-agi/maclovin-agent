"""Console printer for daily executive briefing summary with tools and news."""

import sys
from maclovin.models import BriefingReport


def safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode(sys.stdout.encoding or "ascii", errors="replace").decode(sys.stdout.encoding or "ascii")
        print(safe_text)


def print_console_summary(report: BriefingReport) -> None:
    """Imprime um resumo no terminal destacando ferramentas e notícias."""
    safe_print("=" * 60)
    safe_print(f"MACLOVIN INTELLIGENCE BRIEFING -- {report.reference_date.isoformat()}")
    safe_print("=" * 60)

    if report.alerts:
        for alert in report.alerts:
            safe_print(f"[AVISO] {alert}")
        safe_print("-" * 60)

    # Ferramentas
    if report.tools_and_launches:
        safe_print(f"[*] Radar de Ferramentas & Lancamentos ({len(report.tools_and_launches)} encontrados):\n")
        for idx, tool in enumerate(report.tools_and_launches[:4], 1):
            pricing = tool.pricing_model or "Nao especificado"
            safe_print(f" {idx}. {tool.title} [{pricing.upper()}]")
            summary = tool.summary or tool.title
            safe_print(f"    -> {summary[:110]}...")
            safe_print(f"    -> Link: {tool.canonical_url}")
            safe_print("")

    # Notícias
    items_to_show = report.events if report.events else report.standalone_news
    if items_to_show:
        safe_print(f"[*] Principais Noticias ({len(items_to_show)} fatos selecionados):\n")
        for idx, item in enumerate(items_to_show[:4], 1):
            title = getattr(item, "title", "")
            safe_print(f" {idx}. {title}")
            summary = getattr(item, "consolidated_summary", getattr(item, "summary", ""))
            if summary:
                safe_print(f"    -> {summary[:110]}...")
            safe_print("")

    if not report.tools_and_launches and not items_to_show:
        safe_print("[INFO] Nenhuma atualizacao relevante encontrada no periodo analisado.")

    safe_print("-" * 60)
    stats = report.execution_stats
    safe_print(f"Fontes: {stats.get('sources_ok', 0)} | Ferramentas: {len(report.tools_and_launches)} | Noticias: {len(items_to_show)}")
    safe_print("=" * 60)
