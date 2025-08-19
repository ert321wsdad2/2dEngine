import json
import os
from typing import Any, Dict


class Config:
    """Runtime configuration with persistence to JSON."""

    CONFIG_DIR = os.path.join(os.getcwd(), "config")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

    DEFAULTS: Dict[str, Any] = {
        "lang": "ru",
        "graphics": {
            "scale": 1.0,
        },
        "audio": {
            "master_volume": 1.0,
        },
        "input": {
            # Multiple bindings per action are supported
            "move_up": ["K_w", "K_UP"],
            "move_down": ["K_s", "K_DOWN"],
            "move_left": ["K_a", "K_LEFT"],
            "move_right": ["K_d", "K_RIGHT"],
            "fire": ["MOUSE_LEFT", "JOY_BTN_0"],
            "interact": ["K_e"],
            "pause": ["K_ESCAPE"],
            "quicksave": ["K_F5"],
            "quickload": ["K_F9"],
        },
    }

    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings

    @classmethod
    def load_or_create(cls) -> "Config":
        os.makedirs(cls.CONFIG_DIR, exist_ok=True)
        if not os.path.exists(cls.CONFIG_PATH):
            cfg = cls(DEFAULTS_DEEP_COPY())
            cfg.save()
            return cfg
        with open(cls.CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults to add missing keys
        merged = deep_merge_dicts(DEFAULTS_DEEP_COPY(), data)
        return cls(merged)

    def save(self) -> None:
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)


def deep_merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = deep_merge_dicts(base[key], value)
        else:
            base[key] = value
    return base


def DEFAULTS_DEEP_COPY() -> Dict[str, Any]:
    import copy
    return copy.deepcopy(Config.DEFAULTS)