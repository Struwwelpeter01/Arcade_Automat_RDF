"""Gemeinsames Interface für alle KI-Gegner, damit jedes Spiel dieselbe Schnittstelle nutzt."""

from abc import ABC, abstractmethod


class AIBase(ABC):
    @abstractmethod
    def decide_action(self, game_state):
        """Liefert die nächste Aktion (z.B. Richtung -1/0/1) basierend auf dem Spielzustand."""

    def max_speed(self):
        """Maximale Bewegungsgeschwindigkeit der KI in Pixel/Sekunde."""
        return 300
