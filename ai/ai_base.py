"""Gemeinsame Pong-KI-Logik: Ball-Tracking mit Reaktionsverzögerung, Zielungenauigkeit
und Tempo-Deckel. Unterklassen legen nur reaction_delay/error_margin/max_speed_value fest
(oder überschreiben sie als Property, siehe DynamicAI)."""

import random

DEAD_ZONE = 4  # Toleranz in Pixel, ab der die KI nicht mehr nachregelt


class AIBase:
    reaction_delay = 0.15
    error_margin = 20
    max_speed_value = 260

    def __init__(self):
        self._reaction_timer = 0.0
        self._target_y = None

    def decide_action(self, game_state):
        """game_state: {"ball_center_y", "paddle_center_y", "dt"}. Gibt -1/0/1 zurück (hoch/stehen/runter)."""
        self._reaction_timer -= game_state["dt"]
        if self._target_y is None or self._reaction_timer <= 0:
            self._target_y = game_state["ball_center_y"] + random.uniform(-self.error_margin, self.error_margin)
            self._reaction_timer = self.reaction_delay

        diff = self._target_y - game_state["paddle_center_y"]
        if abs(diff) < DEAD_ZONE:
            return 0
        return 1 if diff > 0 else -1

    def max_speed(self):
        return self.max_speed_value

    def on_point_scored(self, ai_scored):
        """Optional: Feedback nach einem Punkt (nur von adaptiven KIs wie DynamicAI genutzt)."""
