"""Execution logging and observability repository in SQLite."""

import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


def record_execution(
    conn: sqlite3.Connection,
    reference_date: str,
    started_at: datetime,
    finished_at: Optional[datetime],
    status: str,
    sources_queried: int,
    sources_failed: int,
    items_collected: int,
    duplicates_ignored: int,
    errors: Optional[List[str]] = None,
) -> str:
    """Registra uma execução na tabela execution_logs."""
    exec_id = str(uuid.uuid4())
    cursor = conn.cursor()
    errors_json = json.dumps(errors, ensure_ascii=False) if errors else None

    cursor.execute(
        """
        INSERT INTO execution_logs (
            id, reference_date, started_at_utc, finished_at_utc,
            status, sources_queried_count, sources_failed_count,
            items_collected_count, duplicates_ignored_count, errors_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            exec_id,
            reference_date,
            started_at.isoformat(),
            finished_at.isoformat() if finished_at else None,
            status,
            sources_queried,
            sources_failed,
            items_collected,
            duplicates_ignored,
            errors_json,
        ),
    )
    conn.commit()
    return exec_id


def get_latest_execution(conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """Recupera o registro da última execução realizada."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, reference_date, started_at_utc, finished_at_utc, status,
               sources_queried_count, sources_failed_count, items_collected_count,
               duplicates_ignored_count, errors_json, created_at
        FROM execution_logs
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    if not row:
        return None

    if isinstance(row, sqlite3.Row):
        return dict(row)
    cols = [c[0] for c in cursor.description]
    return dict(zip(cols, row))
