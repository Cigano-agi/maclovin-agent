import pytest
import tempfile
import pathlib
from maclovin.config import load_config, save_config
from maclovin.models import AppConfig


def test_load_valid_config():
    yaml_text = """
version: "1.0"
settings:
  timezone: "America/Sao_Paulo"
  output_dir: "briefings"
  database_path: "data/maclovin.db"
  log_level: "INFO"
ai:
  provider: "gemini"
  model: "gemini-2.5-flash"
  temperature: 0.1
topics:
  - id: "ai-ml"
    name: "Inteligencia Artificial"
    keywords: ["AI", "LLM"]
    active: true
    priority: 1
sources:
  - id: "techcrunch-ai"
    name: "TechCrunch AI"
    ingestion_type: "rss"
    url: "https://techcrunch.com/category/artificial-intelligence/feed/"
    active: true
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        f.write(yaml_text)
        f_path = f.name

    try:
        cfg = load_config(f_path)
        assert isinstance(cfg, AppConfig)
        assert cfg.version == "1.0"
        assert cfg.settings.timezone == "America/Sao_Paulo"
        assert len(cfg.topics) == 1
        assert cfg.topics[0].id == "ai-ml"
        assert len(cfg.sources) == 1
        assert cfg.sources[0].id == "techcrunch-ai"
    finally:
        pathlib.Path(f_path).unlink(missing_ok=True)


def test_load_missing_config_returns_default():
    cfg = load_config("non_existent_file.yaml")
    assert isinstance(cfg, AppConfig)
    assert cfg.settings.timezone == "America/Sao_Paulo"


def test_save_and_reload_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg_path = pathlib.Path(tmp_dir) / "config.yaml"
        original_cfg = AppConfig()
        original_cfg.settings.timezone = "Europe/London"
        save_config(original_cfg, str(cfg_path))

        reloaded = load_config(str(cfg_path))
        assert reloaded.settings.timezone == "Europe/London"
