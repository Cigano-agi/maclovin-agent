"""SQLite database engine, connection manager, and schema migrations for maclovin."""

import sqlite3
import pathlib
from typing import Optional


BASE_SCHEMA_SQL = """
-- Tabela de Fontes
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    ingestion_type TEXT NOT NULL,
    url TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    category TEXT NOT NULL DEFAULT 'news',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tabela de Notícias e Ferramentas Coletadas (Idempotência via UNIQUE em canonical_url)
CREATE TABLE IF NOT EXISTS news_items (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    canonical_url TEXT NOT NULL UNIQUE,
    published_date_utc TEXT NOT NULL,
    collected_date_utc TEXT NOT NULL,
    raw_content TEXT,
    content_hash TEXT NOT NULL,
    relevance_score REAL DEFAULT 0.0,
    item_type TEXT NOT NULL DEFAULT 'news',
    pricing_model TEXT NOT NULL DEFAULT 'Não especificado',
    key_features TEXT,
    summary TEXT,
    why_it_matters TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE INDEX IF NOT EXISTS idx_news_pubdate ON news_items(published_date_utc);
CREATE INDEX IF NOT EXISTS idx_news_hash ON news_items(content_hash);

-- Tabela de Eventos Consolidados
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    reference_date TEXT NOT NULL,
    title TEXT NOT NULL,
    main_topic_id TEXT NOT NULL,
    relevance_score REAL NOT NULL DEFAULT 0.0,
    consolidated_summary TEXT NOT NULL,
    why_it_matters TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_date ON events(reference_date);

-- Relacionamento N:N entre Eventos e Notícias
CREATE TABLE IF NOT EXISTS event_news_items (
    event_id TEXT NOT NULL,
    news_item_id TEXT NOT NULL,
    PRIMARY KEY (event_id, news_item_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (news_item_id) REFERENCES news_items(id) ON DELETE CASCADE
);

-- Tabela de Logs de Auditoria e Execução
CREATE TABLE IF NOT EXISTS execution_logs (
    id TEXT PRIMARY KEY,
    reference_date TEXT NOT NULL,
    started_at_utc TEXT NOT NULL,
    finished_at_utc TEXT,
    status TEXT NOT NULL,
    sources_queried_count INTEGER NOT NULL DEFAULT 0,
    sources_failed_count INTEGER NOT NULL DEFAULT 0,
    items_collected_count INTEGER NOT NULL DEFAULT 0,
    duplicates_ignored_count INTEGER NOT NULL DEFAULT 0,
    errors_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_exec_date ON execution_logs(reference_date);
"""


def init_db_schema(conn: sqlite3.Connection) -> None:
    """Executa o script de criação das tabelas e migrações seguras de schema."""
    conn.executescript(BASE_SCHEMA_SQL)
    
    # Migrações seguras para tabelas pré-existentes
    try:
        conn.execute("ALTER TABLE news_items ADD COLUMN item_type TEXT NOT NULL DEFAULT 'news'")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE news_items ADD COLUMN pricing_model TEXT NOT NULL DEFAULT 'Não especificado'")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE news_items ADD COLUMN key_features TEXT")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE sources ADD COLUMN category TEXT NOT NULL DEFAULT 'news'")
    except Exception:
        pass

    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_news_type ON news_items(item_type)")
    except Exception:
        pass

    conn.commit()


def get_db_connection(db_path: str = "data/maclovin.db") -> sqlite3.Connection:
    """
    Abre conexão com o SQLite, ativa modo WAL (Write-Ahead Logging) e foreign keys.
    Cria automaticamente diretórios pais se necessário.
    """
    if db_path != ":memory:":
        path = pathlib.Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    if db_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")

    init_db_schema(conn)
    return conn
