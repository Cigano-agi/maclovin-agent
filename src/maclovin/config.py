"""Configuration manager for maclovin using YAML and Pydantic."""

import os
import pathlib
import yaml
from typing import Optional
from dotenv import load_dotenv

from maclovin.models import AppConfig


def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """
    Carrega e valida o arquivo de configuração YAML.
    Se o arquivo não existir, retorna a configuração padrão.
    """
    # Carrega variáveis de ambiente do .env
    load_dotenv()

    path = pathlib.Path(config_path)
    if not path.exists():
        return AppConfig()

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
            return AppConfig.model_validate(raw_data)
    except Exception as e:
        # Fallback seguro para config padrão se o YAML estiver corrompido
        print(f"[WARN] Erro ao carregar {config_path}: {e}. Utilizando valores padrão.")
        return AppConfig()


def save_config(config: AppConfig, config_path: str = "config/config.yaml") -> None:
    """Salva o modelo de configuração no arquivo YAML especificado."""
    path = pathlib.Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump()
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
