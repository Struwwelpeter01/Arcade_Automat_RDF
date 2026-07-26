"""Hauptmenü: Liste aller verfügbaren Spiele, Auswahl per Mausklick.

Später ersetzt der NFC-Statuen-Loader diese feste Liste; bis dahin dient sie
zum Testen am PC per Maus.
"""

from collections import namedtuple

import pygame

from games.jump_n_run.jump_n_run import JumpNRunGame
from games.pong.pong import PongGame
from games.snake.snake import SnakeGame

GameEntry = namedtuple(
    "GameEntry", "name game_class needs_opponent_choice controls_vs_ai controls_vs_player"
)

GAMES = [
    GameEntry("Snake", SnakeGame, False, None, None),
    GameEntry(
        "Pong",
        PongGame,
        True,
        "Deine Steuerung: W (hoch) / S (runter)",
        "Spieler 1: W / S      Spieler 2: Pfeil hoch / runter",
    ),
    GameEntry("Jump'n'Run", JumpNRunGame, False, None, None),
]

ENTRY_WIDTH = 300
ENTRY_HEIGHT = 60
ENTRY_GAP = 20


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont(None, 64)
        self.entry_font = pygame.font.SysFont(None, 40)
        self.entry_rects = self._layout()

    def _layout(self):
        width, height = self.screen.get_size()
        total_height = len(GAMES) * ENTRY_HEIGHT + (len(GAMES) - 1) * ENTRY_GAP
        start_y = height // 2 - total_height // 2
        return [
            pygame.Rect(
                width // 2 - ENTRY_WIDTH // 2,
                start_y + i * (ENTRY_HEIGHT + ENTRY_GAP),
                ENTRY_WIDTH,
                ENTRY_HEIGHT,
            )
            for i in range(len(GAMES))
        ]

    def handle_event(self, event):
        """Gibt den gewählten GameEntry zurück, sobald ein Eintrag angeklickt wurde."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, entry in zip(self.entry_rects, GAMES):
                if rect.collidepoint(event.pos):
                    return entry
        return None

    def draw(self):
        self.screen.fill((20, 20, 30))

        title = self.title_font.render("Arcade Automat", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 100)))

        mouse_pos = pygame.mouse.get_pos()
        for rect, entry in zip(self.entry_rects, GAMES):
            hovered = rect.collidepoint(mouse_pos)
            color = (90, 90, 130) if hovered else (60, 60, 90)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            text = self.entry_font.render(entry.name, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=rect.center))
