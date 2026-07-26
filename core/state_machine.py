"""Steuert den Ablauf: Hauptmenü -> Spiel -> Pause -> zurück zum Menü.

Der Zustand eines pausierten Spiels wird beim Zurückkehren ins Menü verworfen,
nicht gespeichert.
"""

import pygame

from config.settings import FPS, FULLSCREEN, PAUSE_KEY, SCREEN_HEIGHT, SCREEN_WIDTH
from ui.menu import Menu

BACK_TO_MENU_KEY = pygame.K_m


class StateMachine:
    def __init__(self):
        pygame.init()
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Arcade Automat")
        self.clock = pygame.time.Clock()

        self.menu = Menu(self.screen)
        self.state = "menu"  # "menu" | "game" | "paused"
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
            selected_game_class = self.menu.handle_event(event)
            if selected_game_class is not None:
                self.current_game = selected_game_class(self.screen)
                self.state = "game"
        elif self.state == "game":
            self.current_game.handle_event(event)
        elif self.state == "paused" and self._wants_back_to_menu(event):
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
        elif self.state == "game":
            self.current_game.draw()
        elif self.state == "paused":
            self.current_game.draw()
            self._draw_pause_overlay()

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
