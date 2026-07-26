"""Basisklasse, die jedes Spiel implementieren muss, damit die State Machine es laden kann."""

from abc import ABC, abstractmethod


class GameBase(ABC):
    """Gemeinsames Interface für alle Spiele (Snake, Pong, Jump'n'Run, ...)."""

    def __init__(self, screen):
        self.screen = screen

    def handle_event(self, event):
        """Optional: einzelne Events behandeln (z.B. Neustart nach Game Over)."""

    def handle_paused_event(self, event):
        """Optional: Events behandeln, während das Spiel pausiert ist (z.B. Einstellungen ändern)."""

    def draw_pause_extra(self, screen):
        """Optional: zusätzliche UI im Pause-Overlay zeichnen (z.B. aktuelle Einstellungen)."""

    @abstractmethod
    def update(self, dt):
        """Spiellogik pro Frame aktualisieren."""

    @abstractmethod
    def draw(self):
        """Aktuellen Zustand auf self.screen zeichnen."""
