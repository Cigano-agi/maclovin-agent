"""Core execution pipeline orchestrator for maclovin."""

import time
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any

from maclovin.models import (
    AppConfig,
    NewsItem,
    EventCluster,
    BriefingReport,
    ExecutionRecord,
)
from maclovin.core.clock import get_yesterday_window
from maclovin.ingestion import feed_reader
from maclovin.ingestion.category_classifier import refine_item_category, classify_category
from maclovin.reporting.markdown_builder import save_markdown_report
from maclovin.reporting.console_printer import print_console_summary


class Pipeline:
    """Orquestrador principal do ciclo diário de inteligência de notícias, ferramentas, business, oportunidades, aprendizado e geek."""

    def __init__(
        self,
        config: AppConfig,
        llm_provider: Optional[Any] = None,
        db_connection: Optional[Any] = None,
    ):
        self.config = config
        self.llm_provider = llm_provider
        self.db_conn = db_connection

    def run(
        self,
        target_date: Optional[date] = None,
        dry_run: bool = False,
    ) -> BriefingReport:
        """Executa o ciclo diário completo."""
        start_time = time.time()
        started_at = datetime.now(timezone.utc)

        # 1. Resolver janela temporal — últimas 48h para garantir cobertura completa
        from datetime import timedelta
        now_utc = datetime.now(timezone.utc)
        if target_date is None:
            # Pega as últimas 48h: do início de ontem até agora
            _, end_utc_d1, ref_date = get_yesterday_window(self.config.settings.timezone)
            start_utc = now_utc - timedelta(hours=48)
            end_utc = now_utc
        else:
            ref_date = target_date
            import zoneinfo
            tz = zoneinfo.ZoneInfo(self.config.settings.timezone)
            start_local = datetime(ref_date.year, ref_date.month, ref_date.day, 0, 0, 0, tzinfo=tz)
            end_local = datetime(ref_date.year, ref_date.month, ref_date.day, 23, 59, 59, tzinfo=tz)
            start_utc = start_local.astimezone(timezone.utc)
            end_utc = end_local.astimezone(timezone.utc)

        # 2. Ingestão determinística de feeds ativos
        raw_items: List[NewsItem] = []
        alerts: List[str] = []
        sources_ok = 0
        sources_failed = 0

        active_sources = [s for s in self.config.sources if s.active]
        source_category_map = {s.id: getattr(s, "category", "news") for s in active_sources}

        for source in active_sources:
            items, errors = feed_reader.fetch_feed(source, start_utc, end_utc)
            if errors:
                sources_failed += 1
                alerts.extend(errors)
            else:
                sources_ok += 1
                default_cat = source_category_map.get(source.id, "news")
                for item in items:
                    refine_item_category(item, default_cat)
                    raw_items.append(item)

        # 3. Desduplicação determinística preliminar
        from maclovin.ingestion.deduplicator import deduplicate_items
        unique_items, duplicates_count = deduplicate_items(raw_items)

        # 4. Classificação por palavras-chave / tópicos
        from maclovin.ingestion.topic_matcher import match_topics_to_news
        matched_items = match_topics_to_news(unique_items, self.config.topics)

        # 5. Processamento de Inteligência (Refinamento, Resumos & Agrupamento)
        events: List[EventCluster] = []
        tools_list: List[NewsItem] = []
        opportunity_list: List[NewsItem] = []
        business_list: List[NewsItem] = []
        learning_list: List[NewsItem] = []
        geek_list: List[NewsItem] = []
        news_list: List[NewsItem] = []

        if self.llm_provider and matched_items:
            try:
                from maclovin.intelligence.classifier import refine_with_llm
                from maclovin.intelligence.summarizer import summarize_all
                from maclovin.intelligence.clusterer import cluster_with_llm

                refined_items = refine_with_llm(matched_items, self.config.topics, self.llm_provider)
                summarized_items = summarize_all(refined_items, "Tecnologia & Inovação", self.llm_provider)

                for it in summarized_items:
                    refine_item_category(it, source_category_map.get(it.source_id, "news"))
                    if it.item_type == "tool":
                        tools_list.append(it)
                    elif it.item_type == "opportunities":
                        opportunity_list.append(it)
                    elif it.item_type == "business":
                        business_list.append(it)
                    elif it.item_type == "learning":
                        learning_list.append(it)
                    elif it.item_type == "geek":
                        geek_list.append(it)
                    else:
                        news_list.append(it)

                if news_list:
                    events = cluster_with_llm(news_list, ref_date, self.llm_provider)
            except Exception as e:
                alerts.append(f"Aviso de IA: Falha no processamento: {e}")
                for it in matched_items:
                    refine_item_category(it, source_category_map.get(it.source_id, "news"))
                    if it.item_type == "tool":
                        tools_list.append(it)
                    elif it.item_type == "opportunities":
                        opportunity_list.append(it)
                    elif it.item_type == "business":
                        business_list.append(it)
                    elif it.item_type == "learning":
                        learning_list.append(it)
                    elif it.item_type == "geek":
                        geek_list.append(it)
                    else:
                        news_list.append(it)
        else:
            for it in matched_items:
                refine_item_category(it, source_category_map.get(it.source_id, "news"))
                if it.item_type == "tool":
                    tools_list.append(it)
                elif it.item_type == "opportunities":
                    opportunity_list.append(it)
                elif it.item_type == "business":
                    business_list.append(it)
                elif it.item_type == "learning":
                    learning_list.append(it)
                elif it.item_type == "geek":
                    geek_list.append(it)
                else:
                    news_list.append(it)

        # 6. Persistência no SQLite se conectado
        if self.db_conn and not dry_run:
            from maclovin.storage.news_repo import save_news_items, save_events
            from maclovin.storage.log_repo import record_execution
            
            save_news_items(self.db_conn, matched_items)
            if events:
                save_events(self.db_conn, events)

            exec_status = "SUCCESS" if sources_failed == 0 else ("PARTIAL_FAILURE" if sources_ok > 0 else "FAILED")
            record_execution(
                self.db_conn,
                reference_date=ref_date.isoformat(),
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                status=exec_status,
                sources_queried=len(active_sources),
                sources_failed=sources_failed,
                items_collected=len(raw_items),
                duplicates_ignored=duplicates_count,
                errors=alerts,
            )

        elapsed = time.time() - start_time
        stats = {
            "sources_ok": sources_ok,
            "sources_failed": sources_failed,
            "total_news": len(matched_items),
            "tools_count": len(tools_list),
            "opportunities_count": len(opportunity_list),
            "business_count": len(business_list),
            "learning_count": len(learning_list),
            "geek_count": len(geek_list),
            "news_count": len(news_list),
            "duplicates_ignored": duplicates_count,
            "execution_time_sec": elapsed,
        }

        report = BriefingReport(
            id=ref_date.isoformat(),
            reference_date=ref_date,
            events=events,
            tools_and_launches=tools_list,
            business_items=business_list,
            opportunity_items=opportunity_list,
            learning_items=learning_list,
            geek_items=geek_list,
            standalone_news=news_list if not events else [],
            execution_stats=stats,
            alerts=alerts,
        )

        if not dry_run:
            save_markdown_report(report, output_dir=self.config.settings.output_dir)

        print_console_summary(report)
        return report
