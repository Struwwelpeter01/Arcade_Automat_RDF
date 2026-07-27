"""Panzer-Duell: 2 Panzer in einer Arena mit zerstörbaren Mauern (Battle-City-Stil).

Gegen KI oder gegen einen 2. Spieler - eine echte Solo-Variante ergibt hier keinen
Sinn, das Genre lebt vom Duell. Wer zuerst getroffen wird, verliert die Runde.
Bewegung ist absichtlich achsengebunden (keine Diagonalen), wie im Original.
"""

import pygame

from ai.tank_ai import TankAI
from core.game_base import GameBase
from core.game_modes import VS_AI, VS_PLAYER

CELL = 32
COLS = 32
ROWS = 24

TANK_SIZE = 24
TANK_SPEED = 170
BULLET_SPEED = 420
BULLET_SIZE = 6
SHOOT_COOLDOWN = 0.25

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"
DIRECTION_VECTORS = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}

# Mauerblöcke (x, y, breite, höhe in Zellen) - werden 180°-symmetrisch gespiegelt,
# damit die Arena für beide Startecken fair ist.
WALL_BLOCKS = [
    (4, 4, 3, 1),
    (4, 4, 1, 4),
    (10, 9, 4, 2),
    (15, 3, 1, 5),
    (2, 15, 5, 1),
    (17, 17, 3, 3),
]


def _build_wall_cells():
    blocks = list(WALL_BLOCKS)
    blocks += [(COLS - x - w, ROWS - y - h, w, h) for x, y, w, h in WALL_BLOCKS]
    cells = set()
    for x, y, w, h in blocks:
        for cx in range(x, x + w):
            for cy in range(y, y + h):
                cells.add((cx, cy))
    return cells


class Tank:
    def __init__(self, x, y, direction, color):
        self.rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
        self.direction = direction
        self.color = color
        self.bullet = None
        self.cooldown = 0.0

    def try_shoot(self):
        if self.bullet is None and self.cooldown <= 0:
            bullet_rect = pygame.Rect(0, 0, BULLET_SIZE, BULLET_SIZE)
            bullet_rect.center = self.rect.center
            dx, dy = DIRECTION_VECTORS[self.direction]
            self.bullet = {"rect": bullet_rect, "dx": dx, "dy": dy}
            self.cooldown = SHOOT_COOLDOWN


class TankGame(GameBase):
    def __init__(self, screen, mode=VS_PLAYER):
        super().__init__(screen)
        self.mode = mode
        self.font = pygame.font.SysFont(None, 56)
        self.hud_font = pygame.font.SysFont(None, 24)
        self._reset()

    def _reset(self):
        self.wall_cells = _build_wall_cells()
        self.ai = TankAI() if self.mode == VS_AI else None
        self.player1 = Tank(CELL * 1.5, CELL * 1.5, DOWN, (90, 200, 90))
        second_color = (200, 90, 90) if self.ai else (90, 150, 220)
        self.player2 = Tank((COLS - 2.5) * CELL, (ROWS - 2.5) * CELL, UP, second_color)
        self.winner = None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.winner is not None:
            self._reset()
            return
        if event.key == pygame.K_SPACE:
            self.player1.try_shoot()
        if self.ai is None and event.key == pygame.K_RETURN:
            self.player2.try_shoot()

    def update(self, dt):
        if self.winner is not None:
            return

        keys = pygame.key.get_pressed()
        self._move_tank(
            self.player1, dt, keys, {pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT}
        )

        if self.ai is not None:
            self._apply_ai_action(dt)
        else:
            self._move_tank(
                self.player2,
                dt,
                keys,
                {pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT},
            )

        for tank in (self.player1, self.player2):
            tank.cooldown = max(0.0, tank.cooldown - dt)

        self._update_bullet(self.player1, dt)
        self._update_bullet(self.player2, dt)
        self._check_bullet_hits()

    def _move_tank(self, tank, dt, keys, key_map):
        for key, direction in key_map.items():
            if keys[key]:
                tank.direction = direction
                dx, dy = DIRECTION_VECTORS[direction]
                self._try_move(tank, dx * TANK_SPEED * dt, dy * TANK_SPEED * dt)
                break

    def _apply_ai_action(self, dt):
        action = self.ai.decide_action(self._ai_state(dt))
        if action is None:
            return
        if isinstance(action, tuple):
            _, aim_direction = action
            self.player2.direction = aim_direction
            self.player2.try_shoot()
            return
        self.player2.direction = action
        dx, dy = DIRECTION_VECTORS[action]
        self._try_move(self.player2, dx * TANK_SPEED * dt, dy * TANK_SPEED * dt)

    def _try_move(self, tank, dx, dy):
        new_rect = tank.rect.move(dx, dy)
        if not self.screen.get_rect().contains(new_rect):
            return
        if self._blocked(new_rect, tank):
            return
        tank.rect = new_rect

    def _blocked(self, rect, mover):
        other = self.player2 if mover is self.player1 else self.player1
        if rect.colliderect(other.rect):
            return True
        return any(cell in self.wall_cells for cell in self._cells_overlapping(rect))

    def _cells_overlapping(self, rect):
        min_col, max_col = rect.left // CELL, (rect.right - 1) // CELL
        min_row, max_row = rect.top // CELL, (rect.bottom - 1) // CELL
        return [(c, r) for c in range(min_col, max_col + 1) for r in range(min_row, max_row + 1)]

    def _update_bullet(self, tank, dt):
        bullet = tank.bullet
        if bullet is None:
            return
        bullet["rect"].x += bullet["dx"] * BULLET_SPEED * dt
        bullet["rect"].y += bullet["dy"] * BULLET_SPEED * dt

        if not self.screen.get_rect().colliderect(bullet["rect"]):
            tank.bullet = None
            return

        for cell in self._cells_overlapping(bullet["rect"]):
            if cell in self.wall_cells:
                self.wall_cells.discard(cell)
                tank.bullet = None
                return

    def _check_bullet_hits(self):
        if self.player1.bullet and self.player1.bullet["rect"].colliderect(self.player2.rect):
            self.winner = "player1"
        if self.player2.bullet and self.player2.bullet["rect"].colliderect(self.player1.rect):
            self.winner = "ai" if self.ai else "player2"

    def _ai_state(self, dt):
        return {
            "self_rect": self.player2.rect,
            "target_rect": self.player1.rect,
            "wall_cells": self.wall_cells,
            "cell_size": CELL,
            "cols": COLS,
            "rows": ROWS,
            "dt": dt,
        }

    def draw(self):
        self.screen.fill((25, 25, 20))
        for cx, cy in self.wall_cells:
            rect = pygame.Rect(cx * CELL, cy * CELL, CELL, CELL)
            pygame.draw.rect(self.screen, (150, 100, 70), rect)
            pygame.draw.rect(self.screen, (110, 70, 45), rect, 2)

        for tank in (self.player1, self.player2):
            pygame.draw.rect(self.screen, tank.color, tank.rect, border_radius=3)
            self._draw_barrel(tank)
            if tank.bullet:
                pygame.draw.rect(self.screen, (255, 230, 120), tank.bullet["rect"])

        label = "KI" if self.ai else "Spieler 2"
        hud = self.hud_font.render(f"Spieler 1 (grün)   vs.   {label}", True, (220, 220, 220))
        self.screen.blit(hud, (20, 20))

        if self.winner is not None:
            names = {"player1": "Spieler 1", "player2": "Spieler 2", "ai": "Die KI"}
            text = self.font.render(f"{names[self.winner]} gewinnt! - beliebige Taste", True, (255, 255, 255))
            self.screen.blit(
                text, text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            )

    def _draw_barrel(self, tank):
        dx, dy = DIRECTION_VECTORS[tank.direction]
        start = tank.rect.center
        end = (start[0] + dx * TANK_SIZE, start[1] + dy * TANK_SIZE)
        pygame.draw.line(self.screen, (40, 40, 40), start, end, 5)
