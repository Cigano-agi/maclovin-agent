# Implementation Plan: Daily News Intelligence Agent V1

**Branch**: `001-daily-news-agent` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from [`specs/001-daily-news-agent/spec.md`](./spec.md)

## Summary

O **Daily News Intelligence Agent** é um agente local em Python que automatiza o monitoramento diário de notícias sobre Inteligência Artificial e outros tópicos configurados pelo usuário, respondendo à pergunta *"O que aconteceu ontem nos assuntos que decidi acompanhar?"*.

A arquitetura adota uma abordagem em camadas:
1. **Configuração Declarativa**: Tópicos e fontes em `config/config.yaml`.
2. **Ingestão Determinística**: Coleta em feeds RSS/APIs via `feedparser` e `httpx` sem dependência de LLM (Princípio VI).
3. **Persistência Transacional & Idempotência**: Banco relacional SQLite embutido (`data/maclovin.db`) com índices únicos por URL canônica.
4. **Inteligência Desacoplada**: Adaptador modular `BaseLLMProvider` (Google Gemini, OpenAI, Anthropic e Ollama) para classificação, agrupamento de eventos e resumos estritos sem alucinação (Princípios IV e VI).
5. **Entrega de Briefing**: Relatório em Markdown (`briefings/YYYY-MM-DD.md`) e resumo no console.
6. **Automação**: CLI unificado (`maclovin run`) com script PowerShell de setup para inicialização automática no Windows.

## Technical Context

**Language/Version**: Python 3.11+ gerenciado via `uv`

**Primary Dependencies**:
- `feedparser >= 6.0.11` (Ingestão RSS/Atom)
- `httpx >= 0.27.0` (Requisições HTTP com timeouts)
- `beautifulsoup4 >= 4.12.3` (Extração/limpeza de HTML)
- `pydantic >= 2.7.0` (Modelagem, validação e schemas estruturados)
- `pyyaml >= 6.0.1` (Configuração)
- `python-dotenv >= 1.0.1` (Segredos e chaves de API)
- `google-genai >= 0.1.0` / `openai >= 1.0.0` (SDKs de IA)

**Storage**: SQLite 3 (`data/maclovin.db`) em modo WAL com chaves únicas para garantia estrita de idempotência.

**Testing**: `pytest >= 8.0.0`, `pytest-mock >= 3.14.0`, `pytest-cov`, `respx` (TDD mandatório com 100% de isolamento e mocking de I/O externo).

**Target Platform**: Windows 10/11 (com script PowerShell de registro no Startup/Agendador).

**Project Type**: CLI Application & Local Automated Agent.

**Performance Goals**: Execução completa diária de ~10 fontes em < 30 segundos; geração de resumos em < 15 segundos.

**Constraints**: Zero invasão de paywalls/logins (Princípio V); zero alucinações (Princípio IV); coleta 100% determinística sem LLM (Princípio VI); idempotência estrita (Princípio II).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Status | Verificação no Design |
|---|---|---|
| **I. Janela Temporal & Timezone** | **PASS** | Cálculo estrito de 00:00 às 23:59 de D-1 utilizando timezone configurada no `config.yaml`. |
| **II. Idempotência & Desduplicação** | **PASS** | `canonical_url` e `content_hash` com constraint `UNIQUE` no SQLite; verificação antes de inserir. |
| **III. Metadados Obrigatórios** | **PASS** | Schema `NewsItem` exige `source_id`, `title`, `canonical_url`, `published_date_utc` e `collected_date_utc`. |
| **IV. Fidelidade Factual (Anti-Alucinação)** | **PASS** | Prompts estruturados com Strict Grounding recebendo apenas texto coletado; proibição de dados externos. |
| **V. Coleta Ética & Priorização de RSS** | **PASS** | RSS/APIs estruturados prioritários; zero bypass de paywalls, logins ou CAPTCHAs. |
| **VI. Separação Determinística vs. IA** | **PASS** | Módulos `ingestion` e `storage` rodam 100% sem LLM; módulo `intelligence` entra apenas na fase 2. |
| **VII. Resiliência a Falhas de Fontes** | **PASS** | Try/catch com isolamento de falhas por fonte; erros registrados em `execution_logs` sem abortar o pipeline. |
| **VIII. Observabilidade & Logs** | **PASS** | Gravação estruturada em `execution_logs` (contagens, tempos, fontes com erro, duplicates ignorados). |
| **IX. Síntese & Otimização de Saída** | **PASS** | Briefing em Markdown contém resumos executivos, eventos e links; sem texto integral das matérias. |
| **X. Ciclo TDD Mandatório** | **PASS** | Suíte de testes com `pytest` estruturada para ciclo Red-Green-Refactor antes da codificação. |
| **XI. Mocking de Dependências** | **PASS** | Fixtures de mock para feeds RSS, SQLite in-memory e `LLMProvider` mockado para testes unitários. |
| **XII. Defesa em Profundidade** | **PASS** | Validação de schemas com Pydantic, credenciais via `.env`, proteção contra injeções SQL com queries parametrizadas. |
| **XIII. Validação Ativa** | **PASS** | Critérios de aceitação e quickstart guide mapeados com testes automatizados verificáveis. |

## Project Structure

### Documentation (this feature)

```text
specs/001-daily-news-agent/
├── plan.md              # Plano de implementação (/speckit-plan)
├── research.md          # Decisões de arquitetura e tradeoffs (/speckit-plan)
├── data-model.md        # Entidades, schemas e DDL SQLite (/speckit-plan)
├── quickstart.md        # Guia de validação e testes ponta a ponta (/speckit-plan)
├── checklists/
│   └── requirements.md  # Checklist de qualidade validado
├── contracts/
│   ├── cli-contract.md          # Especificação da interface de linha de comando
│   ├── config-schema.md         # Schema do arquivo config.yaml
│   └── ai-provider-contract.md  # Interface abstrata dos provedores de IA
└── tasks.md             # Tarefas de implementação geradas pelo /speckit-tasks
```

### Source Code (repository root)

```text
config/
└── config.yaml               # Arquivo padrão de tópicos e fontes

scripts/
├── setup_startup.ps1         # Script para registrar execução no Windows Startup
└── uninstall_startup.ps1     # Script para remover inicialização automática

src/
└── maclovin/
    ├── __init__.py
    ├── __main__.py           # Ponto de entrada CLI (`python -m maclovin`)
    ├── cli.py                # Interface de comandos (run, status, check)
    ├── config.py             # Parser e validador Pydantic do config.yaml
    ├── core/
    │   ├── __init__.py
    │   ├── clock.py          # Gestão de timezone e cálculo da janela D-1
    │   └── pipeline.py       # Orquestrador do fluxo diário
    ├── ingestion/
    │   ├── __init__.py
    │   ├── feed_reader.py    # Leitor determinístico de feeds RSS/Atom
    │   ├── html_extractor.py # Fallback limpo de extração de texto HTML
    │   └── normalizer.py     # Normalizador de datas e URLs canônicas
    ├── storage/
    │   ├── __init__.py
    │   ├── database.py       # Inicialização SQLite (WAL mode, schemas)
    │   ├── news_repo.py      # Repositório de notícias com garantia de idempotência
    │   └── log_repo.py       # Repositório de auditoria e logs de execução
    ├── intelligence/
    │   ├── __init__.py
    │   ├── base.py           # Interface BaseLLMProvider e schemas de saída
    │   ├── gemini_provider.py# Implementação Google Gemini
    │   ├── openai_provider.py# Implementação OpenAI / compatíveis
    │   ├── ollama_provider.py# Implementação Ollama local
    │   ├── classifier.py     # Classificação semântica de relevância
    │   ├── clusterer.py      # Agrupamento de notícias em eventos
    │   └── summarizer.py     # Sumarização estrita (Strict Grounding)
    └── reporting/
        ├── __init__.py
        ├── markdown_builder.py # Gerador do arquivo briefings/YYYY-MM-DD.md
        └── console_printer.py  # Renderizador de resumo no terminal

tests/
├── conftest.py               # Fixtures globais (SQLite in-memory, mock feeds, mock LLM)
├── unit/
│   ├── test_clock.py         # Testes de cálculo de janela temporal e timezone
│   ├── test_config.py        # Testes de validação do config.yaml
│   ├── test_feed_reader.py   # Testes determinísticos de parsing de RSS
│   ├── test_news_repo.py     # Testes de idempotência e inserção no SQLite
│   ├── test_classifier.py    # Testes de classificação de relevância
│   ├── test_summarizer.py    # Testes de sumarização anti-alucinação
│   └── test_markdown.py      # Testes de formatação do relatório de briefing
└── integration/
    ├── test_pipeline_e2e.py  # Teste ponta a ponta do ciclo diário com mocks
    └── test_idempotency_e2e.py# Teste de reexecução e zero duplicatas
```

**Structure Decision**: Estrutura modular em pacote Python único (`src/maclovin`), com separação rigorosa de responsabilidades entre ingestão determinística (`ingestion`), armazenamento relacional (`storage`), inteligência de IA (`intelligence`), geração de relatórios (`reporting`) e orquestração de linha de comando (`cli`).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| *Nenhuma violação* | O design cumpre 100% das 13 diretrizes da Constituição | Não aplicável |
