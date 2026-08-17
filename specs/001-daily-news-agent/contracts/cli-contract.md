# CLI Interface Contract: `maclovin`

**Feature**: `001-daily-news-agent`  
**Interface**: Command Line Interface (CLI)  
**Standard**: POSIX / Windows CLI standard text streams (stdin/args -> stdout/stderr)

## 1. Comandos Principais

### 1.1 `maclovin run` (Execução Diária)
Executa o ciclo completo de coleta, classificação, sumarização e geração do briefing diário.

**Sintaxe**:
```bash
maclovin run [OPTIONS]
# ou
python -m maclovin run [OPTIONS]
```

**Opções**:
- `--date YYYY-MM-DD`: Data de referência a analisar (Padrão: dia anterior D-1 no timezone configurado).
- `--config PATH`: Caminho do arquivo de configuração (Padrão: `config/config.yaml`).
- `--output-dir PATH`: Diretório de saída dos relatórios (Padrão: `briefings/`).
- `--dry-run`: Executa a coleta e parsing sem persistir no SQLite ou gerar arquivo em disco.
- `--verbose`: Ativa logs detalhados de debug no terminal.

**Códigos de Saída (Exit Codes)**:
- `0`: Sucesso total (`SUCCESS`) ou concluído com avisos parciais de fontes (`PARTIAL_FAILURE`).
- `1`: Falha de configuração ou argumentos inválidos.
- `2`: Falha crítica de execução (nenhuma fonte acessível ou banco inacessível).

---

### 1.2 `maclovin status` (Consulta de Última Execução)
Exibe o estado, métricas e alertas da execução mais recente.

**Sintaxe**:
```bash
maclovin status
```

---

### 1.3 `maclovin check` (Validação de Ambiente e Fontes)
Verifica conectividade com as fontes configuradas, status do banco de dados e credenciais de LLM no `.env`.

**Sintaxe**:
```bash
maclovin check
```
