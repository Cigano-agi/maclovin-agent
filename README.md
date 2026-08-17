# Maclovin Intelligence 🕶️🍸

Agente local autônomo em Python para monitoramento diário, curadoria de notícias, radar de ferramentas (gratuitas e pagas), aprendizado de engenharia e universo geek de Inteligência Artificial.

---

## 🚀 Funcionalidades Principais

- **🌐 Plataforma Web Interativa:** Dashboard moderno em `http://localhost:8000` com busca em tempo real, filtros de preço e botão de sincronização ao vivo.
- **🛠️ Radar de Ferramentas & Lançamentos:** Identificação e catalogação de novos apps, frameworks e modelos com badges (`[GRÁTIS / OPEN-SOURCE]`, `[FREEMIUM]`, `[PAGO]`).
- **📰 Notícias & Mercado de IA:** Cobertura dos principais fatos corporativos e avanços do setor.
- **📚 Aprender Tecnologia & Deep Dives:** Tutoriais avançados, guias de arquitetura de sistemas e papers explicados.
- **🎮 Universo Geek & Nerd:** Hardware de ponta (GPUs/CPUs), ciência, hacking e gaming tech.
- **🛡️ Anti-Alucinação Estrita (Strict Grounding):** Resumos factuais e seção *"Por que importa"* gerados por LLM sem invenção de dados.
- **⚡ Idempotência Matemática no SQLite:** O agente pode ser executado múltiplas vezes sem duplicar informações no banco.
- **🤖 Provedores de IA Flexíveis:** Suporte a **NVIDIA NIM / GLM-5.2**, **Google Gemini**, **OpenAI**, **Anthropic** e **Ollama** local.

---

## 📦 Instalação e Uso Rápido

### 1. Sincronizar Dependências
```bash
uv sync
```

### 2. Configurar Variáveis de Ambiente
```bash
copy .env.example .env
```
Edite o arquivo `.env` para inserir sua chave (`NVIDIA_API_KEY`, `GEMINI_API_KEY`, etc.).

### 3. Abrir a Plataforma Web
```bash
uv run python -m maclovin web
```
Acesse no seu navegador: **http://localhost:8000**

### 4. Execução Manual via Terminal
```bash
# Diagnóstico de ambiente
uv run python -m maclovin check

# Coleta e resumo diário via terminal
uv run python -m maclovin run

# Consultar status da última execução
uv run python -m maclovin status
```

---

## 🧪 Testes Automatizados (TDD)

```bash
uv run pytest
```
