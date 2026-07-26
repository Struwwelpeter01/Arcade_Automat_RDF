from ai.ai_base import AIBase


class HardAI(AIBase):
    def decide_action(self, game_state):
        raise NotImplementedError
