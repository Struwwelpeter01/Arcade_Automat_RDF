"""Zwischen-Menü nach der Spielauswahl: Gegner wählen (KI oder 2. Spieler), inkl. Steuerungsanzeige."""

import pygame

from core.game_modes import VS_AI, VS_PLAYER

BUTTON_WIDTH = 360
BUTTON_HEIGHT = 70
BUTTON_GAP = 50


class OpponentMenu:
    def __init__(self, screen, game_entry):
        self.screen = screen
        self.game_entry = game_entry
        self.title_font = pygame.font.SysFont(None, 56)
        self.button_font = pygame.font.SysFont(None, 36)
        self.control_font = pygame.font.SysFont(None, 24)
        self.hint_font = pygame.font.SysFont(None, 24)
        self.ai_button, self.player_button = self._layout()

    def _layout(self):
        width, height = self.screen.get_size()
        center_x = width // 2
        first_center_y = height // 2 - (BUTTON_HEIGHT + BUTTON_GAP) // 2
        ai_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        ai_button.center = (center_x, first_center_y)
        player_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        player_button.center = (center_x, first_center_y + BUTTON_HEIGHT + BUTTON_GAP)
        return ai_button, player_button

    def handle_event(self, event):
        """Gibt VS_AI, VS_PLAYER oder "back" zurück, sonst None."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ai_button.collidepoint(event.pos):
                return VS_AI
            if self.player_button.collidepoint(event.pos):
                return VS_PLAYER
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

    def draw(self):
        width = self.screen.get_width()
        self.screen.fill((20, 20, 30))

        title = self.title_font.render(f"{self.game_entry.name} - Gegner wählen", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(width // 2, 90)))

        self._draw_button(self.ai_button, "KI (Medium)", self.game_entry.controls_vs_ai)
        self._draw_button(self.player_button, "2. Spieler", self.game_entry.controls_vs_player)

        hint = self.hint_font.render("Esc = zurück zum Hauptmenü", True, (170, 170, 170))
        self.screen.blit(hint, hint.get_rect(center=(width // 2, self.player_button.bottom + 60)))

    def _draw_button(self, rect, label, controls_text):
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        color = (90, 90, 130) if hovered else (60, 60, 90)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)

        text = self.button_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=rect.center))

        controls = self.control_font.render(controls_text, True, (190, 190, 190))
        self.screen.blit(controls, controls.get_rect(center=(rect.centerx, rect.bottom + 20)))
