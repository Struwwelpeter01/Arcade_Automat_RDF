"""Overlay während eines Spiels: Punktestand, Spielmodus, aktive KI-Schwierigkeit."""


class HUD:
    def draw(self, screen, game_info):
        raise NotImplementedError
