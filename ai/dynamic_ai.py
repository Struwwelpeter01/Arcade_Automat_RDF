"""Dynamische Pong-KI: startet bei einem mittleren Skill-Wert und verschiebt sich
während des Spiels Richtung "leichter" oder "schwerer" - härter, wenn der Spieler
gerade trifft, leichter, wenn die KI selbst trifft. So bleibt das Spiel über eine
Partie hinweg spannend statt entweder trivial oder irgendwann unschlagbar zu werden.

Der Skill-Wert lebt nur im laufenden PongGame-Objekt: sobald das Spiel verlassen
(zurück ins Hauptmenü) oder der Automat neu gestartet wird, entsteht beim nächsten
Start eine frische DynamicAI-Instanz - der Ausgangswert wird also nie dauerhaft
gespeichert und automatisch "zurückgesetzt".
"""

from ai.ai_base import AIBase

INITIAL_SKILL = 0.5  # 0.0 = leicht, 1.0 = schwer - der "Ausgangswert"
SKILL_STEP = 0.15  # Anpassung pro Punkt

# (Wert bei skill 0.0, Wert bei skill 1.0) - siehe EasyAI/HardAI als Referenz für die Grenzen
REACTION_DELAY_RANGE = (0.35, 0.05)
ERROR_MARGIN_RANGE = (50, 6)
MAX_SPEED_RANGE = (170, 340)


def _lerp(value_range, t):
    low, high = value_range
    return low + (high - low) * t


class DynamicAI(AIBase):
    def __init__(self):
        super().__init__()
        self.skill = INITIAL_SKILL

    @property
    def reaction_delay(self):
        return _lerp(REACTION_DELAY_RANGE, self.skill)

    @property
    def error_margin(self):
        return _lerp(ERROR_MARGIN_RANGE, self.skill)

    @property
    def max_speed_value(self):
        return _lerp(MAX_SPEED_RANGE, self.skill)

    def on_point_scored(self, ai_scored):
        if ai_scored:
            self.skill = max(0.0, self.skill - SKILL_STEP)
        else:
            self.skill = min(1.0, self.skill + SKILL_STEP)
