"""Zwischen-Menü nach der Spielauswahl: KI-Schwierigkeit oder 2. Spieler wählen,
inkl. Steuerungsanzeige."""

import pygame

from core.game_modes import AI_DYNAMIC, AI_EASY, AI_HARD, AI_MEDIUM, VS_PLAYER

BUTTON_WIDTH = 360
BUTTON_HEIGHT = 55
ROW_HEIGHT = 95

OPTIONS = [
    ("Leicht (KI)", AI_EASY),
    ("Mittel (KI)", AI_MEDIUM),
    ("Schwer (KI)", AI_HARD),
    ("Dynamisch (KI)", AI_DYNAMIC),
    ("2. Spieler", VS_PLAYER),
]


class OpponentMenu:
    def __init__(self, screen, game_entry):
        self.screen = screen
        self.game_entry = game_entry
        self.title_font = pygame.font.SysFont(None, 52)
        self.button_font = pygame.font.SysFont(None, 32)
        self.control_font = pygame.font.SysFont(None, 22)
        self.hint_font = pygame.font.SysFont(None, 24)
        self.buttons = self._layout()

    def _layout(self):
        width, height = self.screen.get_size()
        total_height = (len(OPTIONS) - 1) * ROW_HEIGHT
        start_y = height // 2 - total_height // 2
        buttons = []
        for i, (label, mode) in enumerate(OPTIONS):
            rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            rect.center = (width // 2, start_y + i * ROW_HEIGHT)
            buttons.append((rect, label, mode))
        return buttons

    def handle_event(self, event):
        """Gibt den gewählten Modus-String oder "back" zurück, sonst None."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, _, mode in self.buttons:
                if rect.collidepoint(event.pos):
                    return mode
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

    def draw(self):
        width = self.screen.get_width()
        self.screen.fill((20, 20, 30))

        title = self.title_font.render(f"{self.game_entry.name} - Gegner wählen", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(width // 2, 60)))

        mouse_pos = pygame.mouse.get_pos()
        for rect, label, mode in self.buttons:
            controls_text = (
                self.game_entry.controls_vs_player if mode == VS_PLAYER else self.game_entry.controls_vs_ai
            )
            self._draw_button(rect, label, controls_text, mouse_pos)

        hint = self.hint_font.render("Esc = zurück zum Hauptmenü", True, (170, 170, 170))
        self.screen.blit(hint, hint.get_rect(center=(width // 2, self.buttons[-1][0].bottom + 50)))

    def _draw_button(self, rect, label, controls_text, mouse_pos):
        hovered = rect.collidepoint(mouse_pos)
        color = (90, 90, 130) if hovered else (60, 60, 90)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)

        text = self.button_font.render(label, True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=rect.center))

        controls = self.control_font.render(controls_text, True, (190, 190, 190))
        self.screen.blit(controls, controls.get_rect(center=(rect.centerx, rect.bottom + 14)))
