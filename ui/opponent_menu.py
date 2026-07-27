"""Zwischen-Menü nach der Spielauswahl: Modus wählen (Solo/KI-Stufe/2. Spieler je
nach Spiel), inkl. Steuerungsanzeige. Die Optionen kommen vom jeweiligen GameEntry
(ui/menu.py), damit jedes Spiel seine eigene Auswahl mitbringen kann."""

import pygame

BUTTON_WIDTH = 380
BUTTON_HEIGHT = 55
ROW_HEIGHT = 95


class OpponentMenu:
    def __init__(self, screen, game_entry):
        self.screen = screen
        self.game_entry = game_entry
        self.title_font = pygame.font.SysFont(None, 52)
        self.button_font = pygame.font.SysFont(None, 32)
        self.control_font = pygame.font.SysFont(None, 20)
        self.hint_font = pygame.font.SysFont(None, 24)
        self.buttons = self._layout()

    def _layout(self):
        options = self.game_entry.opponent_options
        width, height = self.screen.get_size()
        total_height = (len(options) - 1) * ROW_HEIGHT
        start_y = height // 2 - total_height // 2
        buttons = []
        for i, (label, mode, controls_text) in enumerate(options):
            rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            rect.center = (width // 2, start_y + i * ROW_HEIGHT)
            buttons.append((rect, label, mode, controls_text))
        return buttons

    def handle_event(self, event):
        """Gibt den gewählten Modus-String oder "back" zurück, sonst None."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, _, mode, _ in self.buttons:
                if rect.collidepoint(event.pos):
                    return mode
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

    def draw(self):
        width = self.screen.get_width()
        self.screen.fill((20, 20, 30))

        title = self.title_font.render(f"{self.game_entry.name} - Modus wählen", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(width // 2, 55)))

        mouse_pos = pygame.mouse.get_pos()
        for rect, label, _, controls_text in self.buttons:
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
