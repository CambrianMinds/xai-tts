import os
import json
import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

COST_PER_1M_CHARS = 15.0  # Approx $15 per 1 million characters

APP_DIR = Path.home() / ".xai_tts"
SESSIONS_DIR = APP_DIR / "sessions"
PROJECTS_DIR = APP_DIR / "projects"
HISTORY_FILE = APP_DIR / "history.json"

@dataclass
class SynthesisHistoryItem:
    text: str
    voice: str
    speed: float
    output_path: str
    cost: float
    timestamp: str
    format: str = "mp3"
    language: str = "auto"

@dataclass
class AppConfig:
    api_key: str = ""
    default_voice: str = "rex"
    default_speed: float = 1.0
    default_language: str = "auto"
    theme: str = "textual-dark"
    play_after_synthesis: bool = True
    project_dir: str = ""
    
    @classmethod
    def load(cls) -> "AppConfig":
        config_path = APP_DIR / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        return cls(**{k:v for k,v in data.items() if k in cls.__dataclass_fields__})
            except Exception:
                pass
        return cls()
        
    def save(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with open(APP_DIR / "config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(asdict(self), f)

def get_history() -> List[SynthesisHistoryItem]:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [SynthesisHistoryItem(**item) for item in data]
        except Exception:
            pass
    return []

def add_history(item: SynthesisHistoryItem):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    history = get_history()
    history.append(item)
    # keep last 50
    history = history[-50:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(h) for h in history], f, indent=2)

def clear_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def calculate_cost(text: str) -> float:
    return (len(text) / 1_000_000) * COST_PER_1M_CHARS
