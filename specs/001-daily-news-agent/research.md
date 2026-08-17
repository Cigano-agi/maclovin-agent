# Research & Architecture Decisions: Daily News Intelligence Agent V1

**Feature**: `001-daily-news-agent`  
**Date**: 2026-08-17  
**Status**: Completed  

## 1. Technical Decisions & Tradeoffs

### Decision 1: Linguagem e Runtime
- **Decisão**: Python 3.11+ utilizando `uv` como gerenciador de pacotes e ferramentas de execução.
- **Racional**: Python oferece o ecossistema mais maduro e eficiente para parsing de feeds (RSS/Atom), manipulação de dados, automação local no Windows e integração com SDKs de Inteligência Artificial.
- **Alternativas Rejeitadas**:
  - *Node.js / TypeScript*: Bom ecossistema, mas com menos bibliotecas especializadas em parsing robusto de feeds heterogêneos de RSS/Atom legados comparado ao `feedparser`.
  - *Go / Rust*: Excelente desempenho, mas desenvolvimento mais lento para pipelines de NLP/LLM locais e complexidade desnecessária para a carga de processamento diário de um único usuário.

---

### Decision 2: Ingestão Determinística e Extração de Feeds
- **Decisão**: Biblioteca `feedparser` combinada com `httpx` com timeouts rigorosos (10s), headers padrão de User-Agent identificável e fallback secundário com `BeautifulSoup4` (`html.parser`).
- **Racional**: Cumpre os princípios constitucionais V (coleta ética sem invasão de paywalls/logins) e VI (coleta 100% determinística sem uso de LLM). Isola erros de rede por fonte com try/catch e logs estruturados.
- **Alternativas Rejeitadas**:
  - *Selenium / Playwright*: Pesados, lentos, consumem muitos recursos e incentivam tentativas de contorno de bloqueios (o que viola a constituição).
  - *Scrapy*: Framework excessivamente complexo e assíncrono para a necessidade de consumir feeds RSS e páginas estáticas simples.

---

### Decision 3: Persistência Relacional e Idempotência
- **Decisão**: Banco de dados relacional embutido **SQLite 3** (`data/maclovin.db`) em modo WAL (Write-Ahead Logging), gerenciado via schemas tipados (Pydantic / dataclasses).
- **Racional**: Não requer serviço externo ativo, possui transações ACID locais, suporte a índices únicos (`canonical_url`, `published_date_utc`, `hash_conteudo`) para garantir matematicamente a idempotência e permitir buscas estruturadas por período e tópico.
- **Alternativas Rejeitadas**:
  - *Arquivos JSON planos*: Vulneráveis a corrupção em caso de encerramento abrupto e ineficientes para checagem de unicidade e junções relacionais entre fontes, notícias e eventos.
  - *PostgreSQL / MySQL*: Exigem instalação de servidor externo, aumentando drasticamente o atrito de instalação e uso local.

---

### Decision 4: Adaptador Modular de Provedores de IA (LLMs)
- **Decisão**: Arquitetura orientada a interfaces (`BaseLLMProvider`) com implementações desacopladas para:
  1. `GeminiProvider` (Google Gemini API via SDK oficial)
  2. `OpenAIProvider` (OpenAI API / compatíveis)
  3. `AnthropicProvider` (Claude API)
  4. `OllamaProvider` (modelos locais offline via API REST do Ollama)
- **Racional**: Permite ao usuário alternar entre modelos em nuvem econômicos/rápidos (ex: Gemini 2.5 Flash / GPT-4o-mini) e modelos locais totalmente privados (Llama 3 / Qwen), sem alterar uma única linha de lógica do pipeline. Chaves de API são injetadas estritamente via `.env`.
- **Alternativas Rejeitadas**:
  - *Acoplamento direto a um único SDK*: Inflexível e cria dependência de um único fornecedor.
  - *LangChain / LlamaIndex*: Frameworks com muitas camadas de abstração desnecessárias e dependências pesadas; chamadas estruturadas diretas com prompts enxutos são mais confiáveis e fáceis de testar.

---

### Decision 5: Anti-Alucinação e Strict Grounding
- **Decisão**: As etapas de sumarização e classificação recebem apenas o texto bruto extraído e instruções estritas com formatação estruturada (JSON Schema / Structured Outputs).
- **Racional**: Impede a alucinação (Princípio IV) O prompt instrui explicitamente o modelo a: (1) usar somente fatos presentes no texto de entrada; (2) marcar campos com aviso explícito de insuficiência caso a matéria seja incompleta; (3) isolar a mente 'Por que importa' do corpo factual.
- **Alternativas Rejeitadas**:
  - *Geração de texto livre sem schema*: Propenso a devaneios e formatação inconsistente.

---

### Decision 6: Estratégia de Testes Automatizados (TDD & Mocks)
- **Decisão**: Suíte completa com `pytest`, `pytest-mock` e `respx` para interceptação de tráfego HTTP.
- **Racional**: Cumpre os princípios constitucionais X e XI. Testes de ingestão e classificação rodam de forma 100% offline, ultrabrápida e determinística, sem fazer requisições reais à internet nem gastar tokens de LLM durante os testes unitários.
- **Fixtures Chave**:
  - Banco SQLite em memória (`:memory:`) para testes de repositório.
  - Mock de feeds RSS (XML estático) para testes de coleta.
  - Mock do `LLMProvider` com respostas estruturadas pré-definidas para testes de pipeline.

---

### Decision 7: Automação no Windows Startup
- **Decisão**: Script PowerShell `scripts/setup_startup.ps1` que cria um atalho de inicialização no diretório do usuário (`%APPDATA(�Microsoft\Windows\Start Menu\Programs\Startup`) ou registra uma tarefa no Agendador de Tarefas do Windows (`schtasks`).
- **Racional**: Não invasivo, dispensa privilégios administrativos de sistema se criado na pasta Startup do usuário e permite remoção simples via script (`scripts/uninstall_startup.ps1`).

---

## 2. Matriz de Dependências Selecionadas

| Pacote | Versão Mënima | Função no Projeto | Justificativa |
|---|---|---|---|
| `feedparser` | `>=6.0.11` | Ingestão RSS/Atom | Padrão da indéstria para parsing de feeds XML/Atom. |
| hhttx`| `>=0.27.0` | Cliente HTTP | Suporte a chamadas síncronas/assíncronas com timeouts estritos e tratamento de erros. |
| `beautifulsoup4` | `>=4.12.3` | Parsing HTML (Fallback) | Extração limpa de texto de tags HTML em artigos. |
| `pydantic` | `>=2.7.0` | Validação de Dados & Schemas | Tipagem estrita de entidades, configurações YAMLe respostas JSON da IA. |
| `pyyaml` | `>=6.0.1` | Configuração | Leitura e escrita de `config/config.yaml`. |
| `python-dotenv` | `>=1.0.1` | Gestão de Segredos | Carregamento de chaves de API a partir de `.env`. |
| pytest` | `>=8.0.0` | Framework de Testes | Execução de testes TDD, fixtures e asserções. |
| `pytest-mocj� | `>=3.14.0` | Mocking em Testes | Isolamento de I/O externo e LLMs nos testes. |
