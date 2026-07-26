"""Passt die Schwierigkeit während des Spiels an die Leistung des Spielers an."""

from ai.ai_base import AIBase


class DynamicAI(AIBase):
    def __init__(self):
        self.skill_level = 0.5  # 0.0 = leicht, 1.0 = schwer; wird laufend angepasst

    def decide_action(self, game_state):
        raise NotImplementedError

    def adjust_to_player(self, player_performance):
        raise NotImplementedError
