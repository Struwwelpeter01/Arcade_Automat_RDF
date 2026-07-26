"""Lädt das passende Spiel-Modul anhand der erkannten NFC-Statue."""

import importlib
import json

from config.settings import STATUE_REGISTRY_PATH


def load_statue_registry():
    with open(STATUE_REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_game_class(game_key):
    """Importiert z.B. games.snake.snake.SnakeGame anhand des Registry-Eintrags."""
    module_path, class_name = game_key.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
