# Tasks: Daily News Intelligence Agent V1

**Branch**: `001-daily-news-agent` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment setup, and dependency management

- [X] T001 Initialize Python project with `pyproject.toml` dependencies (`feedparser`, `httpx`, `beautifulsoup4`, `pydantic`, `pyyaml`, `python-dotenv`, `google-genai`, `openai`, `pytest`, `pytest-mock`, `respx`)
- [X] T002 [P] Create default configuration file in `config/config.yaml` with topics, sources, and settings
- [X] T003 [P] Create environment variable template `.env.example` with API key placeholders
- [X] T004 [P] Configure global test fixtures and test harness in `tests/conftest.py` with in-memory SQLite and mock fixtures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain models, timezone calculation, database engine, and base interfaces

**⚠️ CRITICAL**: Must be completed before user stories

- [X] T005 [P] Create domain entities and Pydantic validation schemas in `src/maclovin/models.py`
- [X] T006 [P] Implement timezone resolution and D-1 temporal window calculator in `src/maclovin/core/clock.py`
- [X] T007 [P] Unit test for temporal window and timezone calculations in `tests/unit/test_clock.py`
- [X] T008 [P] Implement YAML configuration parser and validator in `src/maclovin/config.py`
- [X] T009 [P] Unit test for configuration parsing and schema validation in `tests/unit/test_config.py`
- [X] T010 Implement SQLite database engine, WAL configuration, and schema migrations in `src/maclovin/storage/database.py`
- [X] T011 [P] Implement abstract LLM provider interface and response models in `src/maclovin/intelligence/base.py`

**Checkpoint**: Foundation ready — domain models, database, clock, and configuration initialized.

---

## Phase 3: User Story 1 - Receber as notícias relevantes de ontem (Priority: P1) 🎯 MVP

**Goal**: Permitir a ingestão determinística de feeds RSS/Atom filtrados pela data de ontem (D-1) e geração do primeiro briefing diário em Markdown.

**Independent Test**: Executar a coleta sobre feeds simulados com múltiplas datas e verificar se apenas matérias de D-1 (00:00 às 23:59) são aceitas e formatadas no briefing.

### Tests for User Story 1 (TDD)
- [X] T012 [P] [US1] Unit test for RSS feed parser and date filtering in `tests/unit/test_feed_reader.py`
- [X] T013 [P] [US1] Unit test for Markdown briefing builder in `tests/unit/test_markdown.py`

### Implementation for User Story 1
- [X] T014 [US1] Implement deterministic RSS/Atom feed reader and date filter in `src/maclovin/ingestion/feed_reader.py`
- [X] T015 [US1] Implement Markdown report generator in `src/maclovin/reporting/markdown_builder.py`
- [X] T016 [US1] Implement terminal summary renderer in `src/maclovin/reporting/console_printer.py`
- [X] T017 [US1] Implement core pipeline orchestrator in `src/maclovin/core/pipeline.py`

**Checkpoint**: User Story 1 funcional de forma independente (MVP de coleta determinística e geração de Markdown).

---

## Phase 4: User Story 2 - Configurar assuntos de interesse (Priority: P1)

**Goal**: Permitir ao usuário personalizar tópicos e palavras-chave de interesse no YAML e associar notícias aos tópicos correspondentes.

**Independent Test**: Modificar `config/config.yaml` com novos tópicos e validar se o pipeline reflete os novos tópicos nos resultados.

### Tests for User Story 2 (TDD)
- [X] T018 [P] [US2] Unit test for topic matching and filtering in `tests/unit/test_topic_matcher.py`

### Implementation for User Story 2
- [X] T019 [US2] Implement deterministic keyword and topic matcher in `src/maclovin/ingestion/topic_matcher.py`
- [X] T020 [US2] Integrate topic classification into `src/maclovin/core/pipeline.py`

---

## Phase 5: User Story 3 - Identificar a origem e proveniência das informações (Priority: P1)

**Goal**: Garantir que toda notícia coletada possua metadados completos e validados (fonte, título, URL canônica, data de publicação UTC e data de coleta).

**Independent Test**: Injetar itens com metadados parciais ou URLs inválidas e validar rejeição ou sanitização conforme a Constituição.

### Tests for User Story 3 (TDD)
- [X] T021 [P] [US3] Unit test for URL canonicalization and metadata normalization in `tests/unit/test_normalizer.py`

### Implementation for User Story 3
- [X] T022 [US3] Implement URL canonicalizer and metadata normalizer in `src/maclovin/ingestion/normalizer.py`
- [X] T023 [US3] Implement HTML text extraction fallback (without paywall bypass) in `src/maclovin/ingestion/html_extractor.py`

---

## Phase 6: User Story 4 - Evitar notícias duplicadas e agrupar coberturas (Priority: P1)

**Goal**: Detectar duplicações óbvias, calcular hash de conteúdo e agrupar matérias cobrindo o mesmo acontecimento em entidades `EventCluster`.

**Independent Test**: Enviar matérias repetidas de fontes diferentes e verificar a consolidação em um único evento no briefing.

### Tests for User Story 4 (TDD)
- [X] T024 [P] [US4] Unit test for content hashing and event clustering in `tests/unit/test_clusterer.py`

### Implementation for User Story 4
- [X] T025 [US4] Implement content hashing and duplicate detection in `src/maclovin/ingestion/deduplicator.py`
- [X] T026 [US4] Implement event clustering logic via AI adapter in `src/maclovin/intelligence/clusterer.py`

---

## Phase 7: User Story 5 - Priorizar acontecimentos por relevância (Priority: P1)

**Goal**: Avaliar aderência semântica e ordenar notícias e eventos por grau de relevância para os tópicos do usuário.

**Independent Test**: Processar notícias centrais vs. tangenciais e validar que as de maior pontuação aparecem no topo do briefing.

### Tests for User Story 5 (TDD)
- [X] T027 [P] [US5] Unit test for semantic relevance classification in `tests/unit/test_classifier.py`

### Implementation for User Story 5
- [X] T028 [US5] Implement semantic relevance classifier in `src/maclovin/intelligence/classifier.py`
- [X] T029 [US5] Integrate relevance sorting into `src/maclovin/reporting/markdown_builder.py`

---

## Phase 8: User Story 6 - Obter resumos objetivos e factuais (Priority: P1)

**Goal**: Gerar resumos concisos com Strict Grounding, garantindo zero alucinações a partir do texto coletado.

**Independent Test**: Comparar o resumo com o texto bruto e verificar ausência de informações externas; validar sinalização explícita de matéria incompleta.

### Tests for User Story 6 (TDD)
- [X] T030 [P] [US6] Unit test for strict grounding summarizer and mock LLM in `tests/unit/test_summarizer.py`

### Implementation for User Story 6
- [X] T031 [US6] Implement strict grounding summarizer in `src/maclovin/intelligence/summarizer.py`
- [X] T032 [US6] Implement Google Gemini provider in `src/maclovin/intelligence/gemini_provider.py`
- [X] T033 [P] [US6] Implement OpenAI / Ollama provider in `src/maclovin/intelligence/openai_provider.py`

---

## Phase 9: User Story 7 - Entender o motivo de importância de cada notícia (Priority: P2)

**Goal**: Adicionar contextualização interpretativa ("Por que importa") claramente distinguível dos fatos relatados.

**Independent Test**: Verificar se itens com alta relevância possuem a seção "Por que importa" separada dos fatos apurados.

### Tests for User Story 7 (TDD)
- [X] T034 [P] [US7] Unit test for "Why it matters" prompt generation in `tests/unit/test_why_it_matters.py`

### Implementation for User Story 7
- [X] T035 [US7] Integrate "Why it matters" extraction and rendering into `src/maclovin/intelligence/summarizer.py` and `src/maclovin/reporting/markdown_builder.py`

---

## Phase 10: User Story 8 - Preservar histórico e assegurar idempotência (Priority: P2)

**Goal**: Persistir notícias, eventos e relacionamentos no SQLite, garantindo que reexecuções no mesmo dia não gerem duplicatas.

**Independent Test**: Executar o pipeline duas vezes no mesmo dia com a mesma base e verificar que o número de notícias salvas permanece idêntico (zero duplicatas).

### Tests for User Story 8 (TDD)
- [X] T036 [P] [US8] Unit test for repository operations and unique constraints in `tests/unit/test_news_repo.py`
- [X] T037 [US8] Integration test for idempotency across repeated runs in `tests/integration/test_idempotency_e2e.py`

### Implementation for User Story 8
- [X] T038 [US8] Implement news item and event persistence repository in `src/maclovin/storage/news_repo.py`
- [X] T039 [US8] Integrate SQLite repository into pipeline execution in `src/maclovin/core/pipeline.py`

---

## Phase 11: User Story 9 - Acompanhar a integridade e status de cada execução (Priority: P2)

**Goal**: Registrar auditoria detalhada de cada execução (`SUCCESS`, `PARTIAL_FAILURE`, `FAILED`), fontes com falha e contagens operacionais.

**Independent Test**: Simular falha de rede em 1 das 3 fontes e validar status `PARTIAL_FAILURE` no log sem quebrar a execução global.

### Tests for User Story 9 (TDD)
- [X] T040 [P] [US9] Unit test for execution logging and error recording in `tests/unit/test_log_repo.py`
- [X] T041 [US9] Integration test for source fault tolerance in `tests/integration/test_fault_tolerance.py`

### Implementation for User Story 9
- [X] T042 [US9] Implement execution log repository in `src/maclovin/storage/log_repo.py`
- [X] T043 [US9] Implement exception isolation and partial failure handling in `src/maclovin/core/pipeline.py`

---

## Phase 12: Polish, Windows Startup Automation & CLI

**Purpose**: Interface de linha de comando completa, scripts de automação no Windows e validação end-to-end

- [X] T044 Implement unified CLI interface (`maclovin run`, `status`, `check`) in `src/maclovin/cli.py`
- [X] T045 [P] Create package entrypoint `src/maclovin/__main__.py`
- [X] T046 [P] Create Windows Startup registration script in `scripts/setup_startup.ps1`
- [X] T047 [P] Create Windows Startup uninstallation script in `scripts/uninstall_startup.ps1`
- [X] T048 Integration test end-to-end for full CLI execution in `tests/integration/test_pipeline_e2e.py`
- [X] T049 Validate quickstart scenarios per `specs/001-daily-news-agent/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
1. **Setup (Phase 1)**: Can start immediately.
2. **Foundational (Phase 2)**: Depends on Phase 1 completion — Blocks all User Stories.
3. **User Stories (Phases 3-11)**: Depend on Phase 2 completion.
   - P1 Stories (US1 → US2 → US3 → US4 → US5 → US6) deliver MVP and core value.
   - P2 Stories (US7 → US8 → US9) add persistence, idempotency and observability.
4. **Polish & Automation (Phase 12)**: Depends on completion of user stories.

### Parallel Opportunities
- All tasks marked with `[P]` can be developed in parallel as they operate on independent files.
- Unit test tasks in each phase can be authored concurrently with contract models.

---

## Implementation Strategy (MVP First)

1. **Sprint 1 (MVP)**: Setup (Phase 1) + Foundational (Phase 2) + US1 (Phase 3) $\rightarrow$ Testable deterministic briefing pipeline!
2. **Sprint 2 (P1 Features)**: US2, US3, US4, US5, US6 $\rightarrow$ Intelligent classification, clustering and strict summaries.
3. **Sprint 3 (P2 & Hardening)**: US7, US8, US9 + Phase 12 $\rightarrow$ SQLite persistence, idempotency, execution logs and Windows Startup automation.
