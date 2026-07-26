"""Mittelschwere Pong-KI."""

from ai.ai_base import AIBase


class MediumAI(AIBase):
    reaction_delay = 0.15  # Sekunden, bevor die KI auf eine neue Ballposition reagiert
    error_margin = 20  # Zielungenauigkeit in Pixel
    max_speed_value = 260  # langsamer als die menschliche Paddle-Geschwindigkeit (400 px/s)
