# Configuration Schema Contract: `config/config.yaml`

**Feature**: `001-daily-news-agent`  
**Format**: YAML 1.2  
**Validation**: Pydantic `AppConfig` model

## Schema Example

```yaml
version: "1.0"

# Configurações Globais
settings:
  timezone: "America/Sao_Paulo"     # Fuso horário para determinar a janela de D-1 (00:00 às 23:59)
  output_dir: "briefings"           # Diretório onde os briefings diários em Markdown são salvos
  database_path: "data/maclovin.db" # Caminho do banco relacional SQLite local
  log_level: "INFO"                 # DEBUG, INFO, WARNING, ERROR

# Provedor de IA (LLM)
ai:
  provider: "gemini"                # gemini, openai, anthropic, ollama
  model: "gemini-2.5-flash"         # Nome do modelo utilizado
  temperature: 0.2                  # Baixa temperatura para estrita fidelidade factual
  timeout_seconds: 30               # Timeout por chamada de IA

# Tópicos de Interesse
topics:
  - id: "ai-ml"
    name: "Inteligência Artificial e Machine Learning"
    keywords:
      - "Inteligência Artificial"
      - "AI"
      - "LLM"
      - "Machine Learning"
      - "OpenAI"
      - "DeepSeek"
      - "Anthropic"
      - "Google Gemini"
    active: true
    priority: 1

  - id: "automation"
    name: "Automação e Agentes Inteligentes"
    keywords:
      - "AI Agents"
      - "Automação"
      - "RPA"
      - "Robotics"
    active: true
    priority: 2

# Fontes de Ingestão de Notícias
sources:
  - id: "techcrunch-ai"
    name: "TechCrunch AI"
    ingestion_type: "rss"
    url: "https://techcrunch.com/category/artificial-intelligence/feed/"
    active: true
    timeout_seconds: 10

  - id: "theverge-ai"
    name: "The Verge AI"
    ingestion_type: "rss"
    url: "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
    active: true
    timeout_seconds: 10

  - id: "mit-tech-review"
    name: "MIT Technology Review AI"
    ingestion_type: "rss"
    url: "https://www.technologyreview.com/topic/artificial-intelligence/feed"
    active: true
    timeout_seconds: 10
```
