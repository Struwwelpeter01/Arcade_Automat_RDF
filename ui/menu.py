"""Hauptmenü: Liste aller verfügbaren Spiele, Auswahl per Mausklick.

Später ersetzt der NFC-Statuen-Loader diese feste Liste; bis dahin dient sie
zum Testen am PC per Maus.
"""

from collections import namedtuple

import pygame

from core.game_modes import AI_DYNAMIC, AI_EASY, AI_HARD, AI_MEDIUM, SOLO, VS_AI, VS_PLAYER
from games.asteroids.asteroids import AsteroidsGame
from games.breakout.breakout import BreakoutGame
from games.jump_n_run.jump_n_run import JumpNRunGame
from games.pong.pong import PongGame
from games.snake.snake import SnakeGame
from games.tanks.tanks import TankGame
from games.tetris.tetris import TetrisGame

# needs_opponent_choice=False -> game_class(screen) wird direkt gestartet.
# needs_opponent_choice=True -> opponent_options = [(Label, Modus-Konstante, Steuerungstext), ...]
GameEntry = namedtuple("GameEntry", "name game_class needs_opponent_choice opponent_options")

PONG_CONTROLS_AI = "Deine Steuerung: W (hoch) / S (runter)"
PONG_CONTROLS_2P = "Spieler 1: W / S      Spieler 2: Pfeil hoch / runter"

TANK_CONTROLS_AI = "Deine Steuerung: WASD bewegen, Leertaste schießen"
TANK_CONTROLS_2P = "Spieler 1: WASD + Leertaste      Spieler 2: Pfeile + Enter"

TETRIS_CONTROLS_SOLO = "Pfeiltasten bewegen/drehen, Runter = Softdrop, Leertaste = Harddrop"
TETRIS_CONTROLS_AI = "Deine Steuerung: Pfeiltasten, Runter = Softdrop, Leertaste = Harddrop"
TETRIS_CONTROLS_2P = "Spieler 1: A/D/W/S + Shift      Spieler 2: Pfeile + Shift"

GAMES = [
    GameEntry("Snake", SnakeGame, False, None),
    GameEntry(
        "Pong",
        PongGame,
        True,
        [
            ("Leicht (KI)", AI_EASY, PONG_CONTROLS_AI),
            ("Mittel (KI)", AI_MEDIUM, PONG_CONTROLS_AI),
            ("Schwer (KI)", AI_HARD, PONG_CONTROLS_AI),
            ("Dynamisch (KI)", AI_DYNAMIC, PONG_CONTROLS_AI),
            ("2. Spieler", VS_PLAYER, PONG_CONTROLS_2P),
        ],
    ),
    GameEntry("Jump'n'Run", JumpNRunGame, False, None),
    GameEntry("Breakout", BreakoutGame, False, None),
    GameEntry("Asteroids", AsteroidsGame, False, None),
    GameEntry(
        "Tetris",
        TetrisGame,
        True,
        [
            ("Solo", SOLO, TETRIS_CONTROLS_SOLO),
            ("Gegen KI", VS_AI, TETRIS_CONTROLS_AI),
            ("2. Spieler", VS_PLAYER, TETRIS_CONTROLS_2P),
        ],
    ),
    GameEntry(
        "Panzer-Duell",
        TankGame,
        True,
        [
            ("Gegen KI", VS_AI, TANK_CONTROLS_AI),
            ("2. Spieler", VS_PLAYER, TANK_CONTROLS_2P),
        ],
    ),
]

ENTRY_WIDTH = 320
ENTRY_HEIGHT = 50
ENTRY_GAP = 14


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont(None, 48)
        self.entry_font = pygame.font.SysFont(None, 34)
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
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 55)))

        mouse_pos = pygame.mouse.get_pos()
        for rect, entry in zip(self.entry_rects, GAMES):
            hovered = rect.collidepoint(mouse_pos)
            color = (90, 90, 130) if hovered else (60, 60, 90)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            text = self.entry_font.render(entry.name, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=rect.center))
