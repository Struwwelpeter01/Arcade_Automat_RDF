"""Mittelschwere Pong-KI: verfolgt den Ball mit Reaktionsverzögerung, Tempo-Deckel und Zielungenauigkeit."""

import random

from ai.ai_base import AIBase

REACTION_DELAY = 0.15  # Sekunden, bevor die KI auf eine neue Ballposition reagiert
MAX_SPEED = 260  # langsamer als die menschliche Paddle-Geschwindigkeit (400 px/s)
ERROR_MARGIN = 20  # Zielungenauigkeit in Pixel
DEAD_ZONE = 4  # Toleranz, ab der die KI nicht mehr nachregelt


class MediumAI(AIBase):
    def __init__(self):
        self._reaction_timer = 0.0
        self._target_y = None

    def decide_action(self, game_state):
        """game_state: {"ball_center_y", "paddle_center_y", "dt"}. Gibt -1/0/1 zurück (hoch/stehen/runter)."""
        self._reaction_timer -= game_state["dt"]
        if self._target_y is None or self._reaction_timer <= 0:
            self._target_y = game_state["ball_center_y"] + random.uniform(-ERROR_MARGIN, ERROR_MARGIN)
            self._reaction_timer = REACTION_DELAY

        diff = self._target_y - game_state["paddle_center_y"]
        if abs(diff) < DEAD_ZONE:
            return 0
        return 1 if diff > 0 else -1

    def max_speed(self):
        return MAX_SPEED
