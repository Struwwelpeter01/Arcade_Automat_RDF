"""Leichte Pong-KI: reagiert langsam und ungenau, niedriger Tempo-Deckel."""

from ai.ai_base import AIBase


class EasyAI(AIBase):
    reaction_delay = 0.35
    error_margin = 50
    max_speed_value = 170
