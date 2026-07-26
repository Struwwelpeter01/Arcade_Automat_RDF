"""Schwere Pong-KI: reagiert schnell und präzise, hoher Tempo-Deckel."""

from ai.ai_base import AIBase


class HardAI(AIBase):
    reaction_delay = 0.05
    error_margin = 6
    max_speed_value = 340
