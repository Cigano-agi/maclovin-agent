# Data Model: Daily News Intelligence Agent V1

**Feature**: `001-daily-news-agent`  
**Date**: 2026-08-17  
**Status**: Ready  

## 1. Domain Entities & Schemas

### 1.1 Topic (`TopicConfig`)
Representa um tópico ou área temática de interesse monitorada.
- `id` (str, PK): Identificador único slug (ex: `"ai-ml"`, `"automation"`).
- `name` (str): Nome legível do tópico (ex: `"Inteligência Artificial e Machine Learning"`).
- `keywords` (List[str]): Termos de busca e classificação semântica (ex: `["IA", "LLM", "OpenAI", "Anthropic"]`).
- `active` (bool, default: True): Status de ativação no ciclo de coleta.
- `priority` (int, default: 1): Peso de priorização (1 a 5).

---

### 1.2 Source (`SourceConfig`)
Representa uma origem configurada de dados para ingestão.
- `id` (str, PK): Slug da fonte (ex: `"techcrunch-ai"`, `"mit-tech-review"`).
- `name` (str): Nome do veículo (ex: `"TechCrunch AI"`).
- `ingestion_type` (str): Tipo de protocolo (`"rss"`, `"atom"`, `"api"`, `"html"`).
- `url` (str): URL do feed RSS ou endpoint.
- `active` (bool, default: True): Flag de ativação.
- `timeout_seconds` (int, default: 10): Timeout máximo para a conexão.

---

### 1.3 NewsItem (`NewsItem`)
Representa um artigo ou notícia individual coletada e normalizada.
- `id` (str, PK): UUID ou SHA-256 da URL canônica.
- `source_id` (str, FK -> Source.id): Referência à fonte de origem.
- `title` (str): Título original publicado.
- `canonical_url` (str, UNIQUE): Link original da matéria.
- `published_date_utc` (datetime): Timestamp ISO 8601 UTC de publicação.
- `collected_date_utc` (datetime): Timestamp ISO 8601 UTC da coleta.
- `raw_content` (str, optional): Texto bruto extraído (para sumarização interna, não exibido no relatório final).
- `content_hash` (str): Hash SHA-256 do corpo do texto (para desduplicação e detecção de republicação).
- `topic_ids` (List[str]): IDs dos tópicos relacionados identificados na classificação.
- `relevance_score` (float, 0.0 a 1.0): Nível de relevância em relação aos tópicos.
- `summary` (str, optional): Resumo factual conciso gerado por IA (Strict Grounding).
- `why_it_matters` (str, optional): Justificativa de impacto e importância.

---

### 1.4 EventCluster (`EventCluster`)
Representa um acontecimento ou fato consolidado coberto por uma ou mais notícias.
- `id` (str, PK): UUID do evento consolidado.
- `title` (str): Título sintetizado do acontecimento.
- `main_topic_id` (str, FK -> Topic.id): Tópico central.
- `news_item_ids` (List[str]): Lista de IDs de notícias agrupadas sob este mesmo fato.
- `sources` (List[str]): Nomes e URLs de todas as fontes que cobriram o evento.
- `relevance_score` (float): Pontuação consolidada de relevância do acontecimento.
- `consolidated_summary` (str): Resumo factual unificado dos pontos em comum.
- `why_it_matters` (str): Análise explicativa do impacto para os tópicos do usuário.

---

### 1.5 BriefingReport (`BriefingReport`)
Representa a entrega diária agregada para o usuário.
- `id` (str, PK): Identificador no formato `YYYY-MM-DD`.
- `reference_date` (date): Data analisada (D-1).
- `generated_at_utc` (datetime): Timestamp da geração do relatório.
- `events` (List[EventCluster]): Eventos selecionados e ordenados por relevância.
- `execution_stats` (dict): Estatísticas operacionais (tempo total, fontes ativas, total de itens processados).
- `alerts` (List[str]): Advertências sobre falhas parciais de fontes ou ausência de notícias.

---

### 1.6 ExecutionRecord (`ExecutionRecord`)
Registro de auditoria e observabilidade de uma execução do pipeline.
- `id` (str, PK): UUID da execução.
- `reference_date` (date): Data de referência (D-1).
- `started_at_utc` (datetime): Início da execução.
- `finished_at_utc` (datetime): Término da execução.
- `status` (str): `"SUCCESS"`, `"PARTIAL_FAILURE"` ou `"FAILED"`.
- `sources_queried_count` (int): Total de fontes chamadas.
- `sources_failed_count` (int): Total de fontes que retornaram erro.
- `items_collected_count` (int): Total de matérias brutas coletadas.
- `duplicates_ignored_count` (int): Matérias descartadas por idempotência.
- `errors_json` (str): Detalhamento em JSON dos erros e fontes com falha.

---

## 2. Esquema Relacional SQLite DDL (`data/maclovin.db`)

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- Tabela de Fontes
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    ingestion_type TEXT NOT NULL,
    url TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tabela de Notícias Coletadas (Idempotência via UNIQUE na URL canônica)
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

-- Tabela de Logs de Execução
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
```

---

## 3. Regras de Validação & Integridade

1. **Janela Temporal Estrita**: `published_date_utc` deve cair exatamente entre `YYYY-MM-D-1T00:00:00Z` e `YYYY-MM-D-1T23:59:59Z`.
2. **Idempotência por Unicidade**: Tentativas de inserir `canonical_url` repetida no mesmo período disparam descarte com incremento em `duplicates_ignored_count`.
3. **Validação de Schema Pydantic**: Entidades utilizam `model_validator` para impedir valores vazios em campos obrigatórios (`title`, `canonical_url`, `source_id`, `published_date_utc`).
