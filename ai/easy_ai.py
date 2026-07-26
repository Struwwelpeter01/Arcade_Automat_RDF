from ai.ai_base import AIBase


class EasyAI(AIBase):
    def decide_action(self, game_state):
        raise NotImplementedError
