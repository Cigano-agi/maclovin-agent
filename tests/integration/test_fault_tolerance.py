import pytest
from datetime import date
from maclovin.core.pipeline import Pipeline


def test_source_fault_tolerance(sample_config, in_memory_db, mock_llm_provider, monkeypatch):
    # One source fails with network error, another source succeeds
    from maclovin.ingestion import feed_reader
    from maclovin.models import NewsItem
    from datetime import datetime, timezone

    def mock_fetch(source, start, end, client=None):
        if source.id == "techcrunch-ai":
            return [], [f"Connection timeout for {source.url}"]
        else:
            item = NewsItem(
                id="1",
                source_id=source.id,
                title="Google AI Platform Update",
                canonical_url="https://theverge.com/google-ai",
                published_date_utc=datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc),
                raw_content="Content",
            )
            return [item], []

    monkeypatch.setattr(feed_reader, "fetch_feed", mock_fetch)

    pipeline = Pipeline(
        config=sample_config,
        llm_provider=mock_llm_provider,
        db_connection=in_memory_db,
    )

    report = pipeline.run(target_date=date(2026, 8, 16), dry_run=False)

    # Pipeline MUST NOT crash. It delivers results for the working source and logs the alert.
    assert len(report.alerts) == 1
    assert "Connection timeout" in report.alerts[0]
    assert report.execution_stats["sources_ok"] == 1
    assert report.execution_stats["sources_failed"] == 1

    from maclovin.storage.log_repo import get_latest_execution
    latest = get_latest_execution(in_memory_db)
    assert latest["status"] == "PARTIAL_FAILURE"
