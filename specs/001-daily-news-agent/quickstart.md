# Quickstart & Validation Guide: Daily News Intelligence Agent V1

**Feature**: `001-daily-news-agent`  
**Target Environment**: Windows 10/11 com Python 3.11+ e `uv`  

---

## 1. Instalação e Configuração

```bash
# 1. Clonar ou navegar até a raiz do projeto
cd C:/Users/juice/Desktop/PROJETOS/maclovin

# 2. Criar e sincronizar ambiente virtual com uv
uv venv
uv sync

# 3. Configurar variáveis de ambiente
copy .env.example .env
# Edite o .env para adicionar GEMINI_API_KEY ou OPENAI_API_KEY se utilizar provedor em nuvem
```

---

## 2. Execução dos Testes Automatizados (TDD Verification)

```bash
# Executar toda a suíte de testes com mocks isolados
uv run pytest -v

# Executar com relatório de cobertura
uv run pytest --cov=src -v
```

---

## 3. Validação End-to-End da Execução Diária

```bash
# 1. Execução manual do agente para a data de ontem (D-1)
uv run python -m maclovin run

# 2. Verificar geração do briefing em Markdown
cat briefings/*.md

# 3. Verificar idempotência (segunda execução não duplica notícias no banco)
uv run python -m maclovin run
# Deve exibir no console: "Itens duplicados ignorados: N | Novos itens inseridos: 0"
```

---

## 4. Configuração da Inicialização Automática no Windows

```powershell
# Executar script para registrar inicialização no Windows Startup
powershell -ExecutionPolicy Bypass -File scripts/setup_startup.ps1

# Para desinstalar o atalho de inicialização posteriormente
powershell -ExecutionPolicy Bypass -File scripts/uninstall_startup.ps1
```
