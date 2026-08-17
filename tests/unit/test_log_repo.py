import pytest
from datetime import datetime, timezone
from maclovin.storage.log_repo import record_execution, get_latest_execution


def test_record_and_get_latest_execution(in_memory_db):
    started_at = datetime(2026, 8, 17, 8, 0, 0, tzinfo=timezone.utc)
    finished_at = datetime(2026, 8, 17, 8, 0, 15, tzinfo=timezone.utc)

    record_execution(
        in_memory_db,
        reference_date="2026-08-16",
        started_at=started_at,
        finished_at=finished_at,
        status="PARTIAL_FAILURE",
        sources_queried=4,
        sources_failed=1,
        items_collected=15,
        duplicates_ignored=2,
        errors=["Fonte TechCrunch timeout"],
    )

    latest = get_latest_execution(in_memory_db)
    assert latest is not None
    assert latest["reference_date"] == "2026-08-16"
    assert latest["status"] == "PARTIAL_FAILURE"
    assert latest["sources_queried_count"] == 4
    assert latest["sources_failed_count"] == 1
    assert latest["items_collected_count"] == 15
    assert latest["duplicates_ignored_count"] == 2
    assert "TechCrunch" in latest["errors_json"]
