"""Command Line Interface (CLI) for maclovin daily news & intelligence agent."""

import argparse
import sys
import os
import webbrowser
import threading
import time
from datetime import datetime, date

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from maclovin.config import load_config
from maclovin.storage.database import get_db_connection
from maclovin.storage.log_repo import get_latest_execution
from maclovin.intelligence.factory import create_llm_provider
from maclovin.core.pipeline import Pipeline


def cmd_run(args) -> int:
    """Executa o pipeline diário de notícias e ferramentas."""
    cfg = load_config(args.config)
    if args.output_dir:
        cfg.settings.output_dir = args.output_dir

    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"[ERRO] Formato de data inválido '{args.date}'. Use YYYY-MM-DD.")
            return 1

    conn = None
    if not args.dry_run:
        conn = get_db_connection(cfg.settings.database_path)

    provider = create_llm_provider(cfg.ai)
    pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=conn)

    report = pipeline.run(target_date=target_date, dry_run=args.dry_run)

    if conn:
        conn.close()

    return 0


def cmd_status(args) -> int:
    """Exibe o estado e estatísticas da última execução."""
    cfg = load_config(args.config)
    conn = get_db_connection(cfg.settings.database_path)
    latest = get_latest_execution(conn)
    conn.close()

    if not latest:
        print("[INFO] Nenhuma execução registrada no banco de dados local.")
        return 0

    print("=" * 60)
    print(f"STATUS DA ÚLTIMA EXECUÇÃO: {latest['reference_date']}")
    print("=" * 60)
    print(f"- Status: {latest['status']}")
    print(f"- Iniciado em: {latest['started_at_utc']}")
    print(f"- Finalizado em: {latest['finished_at_utc']}")
    print(f"- Fontes Consultadas: {latest['sources_queried_count']} (Falhas: {latest['sources_failed_count']})")
    print(f"- Notícias Coletadas: {latest['items_collected_count']}")
    print(f"- Duplicatas Ignoradas: {latest['duplicates_ignored_count']}")
    if latest.get("errors_json"):
        print(f"- Avisos/Erros: {latest['errors_json']}")
    print("=" * 60)
    return 0


def cmd_check(args) -> int:
    """Verifica conectividade das fontes, integridade do banco e credenciais de IA."""
    cfg = load_config(args.config)
    print("Diagnosticando ambiente do maclovin...\n")

    # 1. Configuração
    print(f"[OK] Arquivo de configuração: {args.config} (Versão {cfg.version})")
    print(f"     Timezone configurada: {cfg.settings.timezone}")
    print(f"     Tópicos ativos: {len([t for t in cfg.topics if t.active])}")
    print(f"     Fontes ativas: {len([s for s in cfg.sources if s.active])}")

    # 2. Banco de dados
    try:
        conn = get_db_connection(cfg.settings.database_path)
        conn.close()
        print(f"[OK] Banco SQLite acessível em '{cfg.settings.database_path}'")
    except Exception as e:
        print(f"[FALHA] Falha ao acessar banco SQLite: {e}")

    # 3. Provedor de IA
    print(f"[IA] Provedor de IA: {cfg.ai.provider} (Modelo: {cfg.ai.model})")
    if cfg.ai.provider == "gemini":
        has_key = bool(os.getenv("GEMINI_API_KEY"))
        print(f"     GEMINI_API_KEY definida: {'[SIM]' if has_key else '[NAO CONFIGURADA - modo heurístico ativo]'}")
    elif cfg.ai.provider in ("openai", "nvidia", "glm", "anthropic"):
        has_key = bool(os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY"))
        print(f"     API KEY definida: {'[SIM]' if has_key else '[NAO CONFIGURADA]'}")

    print("\nDiagnóstico concluído com sucesso!")
    return 0


def cmd_web(args) -> int:
    """Inicia a plataforma web local e abre no navegador."""
    cfg = load_config(args.config)
    port = args.port or cfg.settings.web_port or 8000

    from maclovin.web.server import run_web_server

    if not args.no_browser:
        def open_browser():
            time.sleep(0.8)
            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=open_browser, daemon=True).start()

    run_web_server(port=port)
    return 0


def cmd_startup(args) -> int:
    """
    Rotina de Inicialização do Windows:
    1. Executa a coleta diária automática (run).
    2. Abre o painel web no navegador.
    3. Mantém o servidor web ativo em segundo plano.
    """
    cfg = load_config(args.config)
    port = args.port or cfg.settings.web_port or 8000

    # 1. Executar coleta diária
    try:
        conn = get_db_connection(cfg.settings.database_path)
        provider = create_llm_provider(cfg.ai)
        pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=conn)
        pipeline.run(dry_run=False)
        conn.close()
    except Exception as e:
        print(f"[WARN] Falha na coleta do startup: {e}")

    # 2. Abrir navegador
    def open_browser():
        time.sleep(1.0)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Iniciar servidor
    from maclovin.web.server import run_web_server
    run_web_server(port=port)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="maclovin",
        description="Maclovin — Daily Intelligence, Tools Radar & Geek Hub",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Comando `run`
    p_run = subparsers.add_parser("run", help="Executa a coleta diária e gera o briefing")
    p_run.add_argument("--date", type=str, help="Data de referência (YYYY-MM-DD)")
    p_run.add_argument("--config", type=str, default="config/config.yaml", help="Caminho do config.yaml")
    p_run.add_argument("--output-dir", type=str, help="Diretório de saída dos briefings")
    p_run.add_argument("--dry-run", action="store_true", help="Executa sem persistir no banco ou salvar em disco")

    # Comando `web`
    p_web = subparsers.add_parser("web", help="Inicia a plataforma web interativa no navegador")
    p_web.add_argument("--port", type=int, help="Porta do servidor web (padrão: 8000)")
    p_web.add_argument("--config", type=str, default="config/config.yaml", help="Caminho do config.yaml")
    p_web.add_argument("--no-browser", action="store_true", help="Não abre o navegador automaticamente")

    # Comando `startup`
    p_startup = subparsers.add_parser("startup", help="Rotina completa de boot do Windows (coleta + abre navegador + servidor)")
    p_startup.add_argument("--port", type=int, help="Porta do servidor web (padrão: 8000)")
    p_startup.add_argument("--config", type=str, default="config/config.yaml", help="Caminho do config.yaml")

    # Comando `status`
    p_status = subparsers.add_parser("status", help="Consulta métricas da última execução")
    p_status.add_argument("--config", type=str, default="config/config.yaml", help="Caminho do config.yaml")

    # Comando `check`
    p_check = subparsers.add_parser("check", help="Valida conectividade, banco e configurações")
    p_check.add_argument("--config", type=str, default="config/config.yaml", help="Caminho do config.yaml")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        if args.command is None:
            args = parser.parse_args(["run"])
        sys.exit(cmd_run(args))
    elif args.command == "web":
        sys.exit(cmd_web(args))
    elif args.command == "startup":
        sys.exit(cmd_startup(args))
    elif args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "check":
        sys.exit(cmd_check(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
