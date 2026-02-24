from pathlib import Path

import yaml
from pydantic import BaseModel


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:1.5b"
    temperature: float = 0.7
    max_tokens: int = 512


class DreamConfig(BaseModel):
    enabled: bool = True
    schedule_cron: str = "0 3 * * *"
    max_duration_minutes: int = 45
    pruning_threshold_days: int = 14
    hours_to_review: int = 24


class VigilConfig(BaseModel):
    enabled: bool = True
    innate_rules_path: str | None = None
    max_actions_per_minute: int = 30


class ArenaConfig(BaseModel):
    evaluation_window_days: int = 7
    min_fitness_threshold: float = 0.6


class InterfaceConfig(BaseModel):
    dashboard_enabled: bool = True
    dashboard_port: int = 8080
    dashboard_host: str = "0.0.0.0"


class RomulusConfig(BaseModel):
    name: str = "Romulus"
    version: str = "0.1.0"
    data_dir: str = "data"
    soul_path: str = "soul.md"
    ollama: OllamaConfig = OllamaConfig()
    dream: DreamConfig = DreamConfig()
    vigil: VigilConfig = VigilConfig()
    arena: ArenaConfig = ArenaConfig()
    interfaces: InterfaceConfig = InterfaceConfig()

    @classmethod
    def load(cls, path: str = "config.yaml") -> "RomulusConfig":
        config_path = Path(path)
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}

        return cls(**raw)
