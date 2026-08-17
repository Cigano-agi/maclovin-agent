"""Console printer for daily executive briefing summary with tools and news."""

from maclovin.models import BriefingReport


def print_console_summary(report: BriefingReport) -> None:
    """Imprime um resumo no terminal destacando ferramentas e notícias."""
    print("=" * 60)
    print(f"MACLOVIN INTELLIGENCE BRIEFING -- {report.reference_date.isoformat()}")
    print("=" * 60)

    if report.alerts:
        for alert in report.alerts:
            print(f"[AVISO] {alert}")
        print("-" * 60)

    # Ferramentas
    if report.tools_and_launches:
        print(f"🛠️  Radar de Ferramentas & Lançamentos ({len(report.tools_and_launches)} encontrados):\n")
        for idx, tool in enumerate(report.tools_and_launches[:4], 1):
            pricing = tool.pricing_model or "Não especificado"
            print(f" {idx}. {tool.title} [{pricing.upper()}]")
            summary = tool.summary or tool.title
            print(f"    -> {summary[:110]}...")
            print(f"    -> Link: {tool.canonical_url}")
            print()

    # Notícias
    items_to_show = report.events if report.events else report.standalone_news
    if items_to_show:
        print(f"📰 Principais Notícias ({len(items_to_show)} fatos selecionados):\n")
        for idx, item in enumerate(items_to_show[:4], 1):
            title = getattr(item, "title", "")
            print(f" {idx}. {title}")
            summary = getattr(item, "consolidated_summary", getattr(item, "summary", ""))
            if summary:
                print(f"    -> {summary[:110]}...")
            print()

    if not report.tools_and_launches and not items_to_show:
        print("[INFO] Nenhuma atualizacao relevante encontrada no periodo analisado.")

    print("-" * 60)
    stats = report.execution_stats
    print(f"Fontes: {stats.get('sources_ok', 0)} | Ferramentas: {len(report.tools_and_launches)} | Noticias: {len(items_to_show)}")
    print("=" * 60)
