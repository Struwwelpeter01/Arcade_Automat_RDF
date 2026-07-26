"""Steuert den Ablauf: Hauptmenü -> Gegnerauswahl (falls nötig) -> Spiel -> Pause -> zurück zum Menü.

Der Zustand eines pausierten Spiels wird beim Zurückkehren ins Menü verworfen,
nicht gespeichert.
"""

import pygame

from config.settings import FPS, FULLSCREEN, PAUSE_KEY, SCREEN_HEIGHT, SCREEN_WIDTH
from core.game_modes import VS_AI, VS_PLAYER
from ui.menu import Menu
from ui.opponent_menu import OpponentMenu

BACK_TO_MENU_KEY = pygame.K_m


class StateMachine:
    def __init__(self):
        pygame.init()
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Arcade Automat")
        self.clock = pygame.time.Clock()

        self.menu = Menu(self.screen)
        self.state = "menu"  # "menu" | "opponent_select" | "game" | "paused"
        self.pending_game_entry = None
        self.opponent_menu = None
        self.current_game = None

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == PAUSE_KEY:
                    self._toggle_pause()
                else:
                    self._handle_event(event)

            if self.state == "game":
                self.current_game.update(dt)

            self._draw()
            pygame.display.flip()

        pygame.quit()

    def _toggle_pause(self):
        if self.state == "game":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "game"

    def _handle_event(self, event):
        if self.state == "menu":
            self._handle_menu_event(event)
        elif self.state == "opponent_select":
            self._handle_opponent_select_event(event)
        elif self.state == "game":
            self.current_game.handle_event(event)
        elif self.state == "paused":
            self._handle_paused_event(event)

    def _handle_menu_event(self, event):
        entry = self.menu.handle_event(event)
        if entry is None:
            return
        if entry.needs_opponent_choice:
            self.pending_game_entry = entry
            self.opponent_menu = OpponentMenu(self.screen, entry)
            self.state = "opponent_select"
        else:
            self.current_game = entry.game_class(self.screen)
            self.state = "game"

    def _handle_opponent_select_event(self, event):
        result = self.opponent_menu.handle_event(event)
        if result is None:
            return
        if result == "back":
            self.pending_game_entry = None
            self.opponent_menu = None
            self.state = "menu"
        elif result in (VS_AI, VS_PLAYER):
            self.current_game = self.pending_game_entry.game_class(self.screen, mode=result)
            self.pending_game_entry = None
            self.opponent_menu = None
            self.state = "game"

    def _handle_paused_event(self, event):
        self.current_game.handle_paused_event(event)
        if self._wants_back_to_menu(event):
            self.current_game = None
            self.state = "menu"

    def _wants_back_to_menu(self, event):
        if event.type == pygame.KEYDOWN and event.key == BACK_TO_MENU_KEY:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._menu_button_rect().collidepoint(event.pos)
        return False

    def _menu_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 30, 280, 50)

    def _draw(self):
        if self.state == "menu":
            self.menu.draw()
        elif self.state == "opponent_select":
            self.opponent_menu.draw()
        elif self.state == "game":
            self.current_game.draw()
        elif self.state == "paused":
            self.current_game.draw()
            self._draw_pause_overlay()
            self.current_game.draw_pause_extra(self.screen)

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont(None, 56)
        title = title_font.render("PAUSIERT", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))

        hint_font = pygame.font.SysFont(None, 28)
        hint = hint_font.render("Z = weiterspielen", True, (200, 200, 200))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15)))

        button_rect = self._menu_button_rect()
        pygame.draw.rect(self.screen, (70, 70, 70), button_rect, border_radius=8)
        button_font = pygame.font.SysFont(None, 32)
        button_text = button_font.render("Zum Hauptmenü (M)", True, (255, 255, 255))
        self.screen.blit(button_text, button_text.get_rect(center=button_rect.center))
