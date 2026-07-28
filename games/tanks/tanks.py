"""Panzer-Duell: 2 Panzer in einer Arena mit zerstörbaren Mauern (Battle-City-Stil).

Gegen KI oder gegen einen 2. Spieler - eine echte Solo-Variante ergibt hier keinen
Sinn, das Genre lebt vom Duell. Wer zuerst getroffen wird, verliert die Runde.
Bewegung ist achsengebunden (keine Diagonalen) - außer das Diagonalfahrt-Powerup
ist gerade aktiv. Von zwei gleichzeitig gehaltenen Richtungstasten gewinnt immer
die zuletzt gedrückte, damit sich Richtungswechsel sauber anfühlen.

Alle 30s spawnt ein zufälliges Powerup, das nach weiteren 30s wieder verschwindet,
falls niemand es einsammelt. Wer es einsammelt, bekommt 15s lang eine Fähigkeit:
Dauerfeuer, Speed-Boost, ein Schutzschild (blockt einen Treffer) oder Diagonalfahrt.
"""

import random

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
DIAGONAL_FACTOR = 0.70710678  # 1/sqrt(2), damit Diagonalfahrt nicht schneller ist

# Powerups
POWERUP_SPAWN_INTERVAL = 30.0
POWERUP_LIFETIME = 30.0
EFFECT_DURATION = 15.0
POWERUP_SIZE = 22

RAPID_FIRE = "rapid_fire"
SPEED_BOOST = "speed"
SHIELD = "shield"
DIAGONAL = "diagonal"
POWERUP_TYPES = [RAPID_FIRE, SPEED_BOOST, SHIELD, DIAGONAL]

RAPID_FIRE_COOLDOWN = 0.08
RAPID_FIRE_MAX_BULLETS = 4
SPEED_BOOST_MULTIPLIER = 1.6

POWERUP_STYLE = {
    RAPID_FIRE: ((240, 210, 60), "R"),
    SPEED_BOOST: ((80, 220, 220), "S"),
    SHIELD: ((90, 140, 240), "SH"),
    DIAGONAL: ((190, 90, 220), "D"),
}
POWERUP_LABELS = {
    RAPID_FIRE: "Dauerfeuer",
    SPEED_BOOST: "Speed-Boost",
    SHIELD: "Schutzschild",
    DIAGONAL: "Diagonalfahrt",
}

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
        self.bullets = []
        self.cooldown = 0.0
        self.effect = None
        self.effect_timer = 0.0

    @property
    def speed(self):
        return TANK_SPEED * SPEED_BOOST_MULTIPLIER if self.effect == SPEED_BOOST else TANK_SPEED

    @property
    def max_bullets(self):
        return RAPID_FIRE_MAX_BULLETS if self.effect == RAPID_FIRE else 1

    @property
    def shoot_cooldown(self):
        return RAPID_FIRE_COOLDOWN if self.effect == RAPID_FIRE else SHOOT_COOLDOWN

    @property
    def diagonal(self):
        return self.effect == DIAGONAL

    def try_shoot(self):
        if self.cooldown <= 0 and len(self.bullets) < self.max_bullets:
            bullet_rect = pygame.Rect(0, 0, BULLET_SIZE, BULLET_SIZE)
            bullet_rect.center = self.rect.center
            dx, dy = DIRECTION_VECTORS[self.direction]
            self.bullets.append({"rect": bullet_rect, "dx": dx, "dy": dy})
            self.cooldown = self.shoot_cooldown

    def apply_effect(self, effect):
        self.effect = effect
        self.effect_timer = EFFECT_DURATION

    def update_effect(self, dt):
        if self.effect is None:
            return
        self.effect_timer -= dt
        if self.effect_timer <= 0:
            self.effect = None
            self.effect_timer = 0.0

    def consume_shield(self):
        if self.effect == SHIELD:
            self.effect = None
            self.effect_timer = 0.0
            return True
        return False


class TankGame(GameBase):
    def __init__(self, screen, mode=VS_PLAYER):
        super().__init__(screen)
        self.mode = mode
        self.font = pygame.font.SysFont(None, 56)
        self.hud_font = pygame.font.SysFont(None, 24)
        self.p1_keymap = {pygame.K_w: UP, pygame.K_s: DOWN, pygame.K_a: LEFT, pygame.K_d: RIGHT}
        self.p2_keymap = {pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT}
        self.p1_reverse = {v: k for k, v in self.p1_keymap.items()}
        self.p2_reverse = {v: k for k, v in self.p2_keymap.items()}
        self._reset()

    def _reset(self):
        self.wall_cells = _build_wall_cells()
        self.ai = TankAI() if self.mode == VS_AI else None
        self.player1 = Tank(CELL * 1.5, CELL * 1.5, DOWN, (90, 200, 90))
        second_color = (200, 90, 90) if self.ai else (90, 150, 220)
        self.player2 = Tank((COLS - 2.5) * CELL, (ROWS - 2.5) * CELL, UP, second_color)
        self.winner = None
        self.p1_key_order = []
        self.p2_key_order = []
        self.powerup = None
        self.powerup_spawn_timer = POWERUP_SPAWN_INTERVAL

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
        self._track_key(event.key, self.p1_keymap, self.p1_key_order)
        if self.ai is None:
            self._track_key(event.key, self.p2_keymap, self.p2_key_order)

    def _track_key(self, key, key_map, order):
        direction = key_map.get(key)
        if direction is None:
            return
        if direction in order:
            order.remove(direction)
        order.append(direction)

    def update(self, dt):
        if self.winner is not None:
            return

        keys = pygame.key.get_pressed()
        self._move_tank(self.player1, dt, self.p1_key_order, self.p1_reverse, keys)

        if self.ai is not None:
            self._apply_ai_action(dt)
        else:
            self._move_tank(self.player2, dt, self.p2_key_order, self.p2_reverse, keys)

        for tank in (self.player1, self.player2):
            tank.cooldown = max(0.0, tank.cooldown - dt)
            tank.update_effect(dt)

        self._update_bullets(self.player1, dt)
        self._update_bullets(self.player2, dt)
        self._check_bullet_hits()
        self._update_powerup(dt)

    def _move_tank(self, tank, dt, order, reverse_map, keys):
        # Tasten, die nicht mehr gedrückt sind, fliegen raus - übrig bleibt die
        # zuletzt gedrückte, noch gehaltene Richtung als Bewegungsziel.
        order[:] = [d for d in order if keys[reverse_map[d]]]
        if not order:
            return

        if tank.diagonal:
            dx = dy = 0
            used_axes = set()
            for direction in reversed(order):
                axis = "x" if direction in (LEFT, RIGHT) else "y"
                if axis in used_axes:
                    continue
                used_axes.add(axis)
                vx, vy = DIRECTION_VECTORS[direction]
                dx += vx
                dy += vy
            tank.direction = order[-1]
            if dx and dy:
                dx *= DIAGONAL_FACTOR
                dy *= DIAGONAL_FACTOR
            self._try_move(tank, dx * tank.speed * dt, dy * tank.speed * dt)
        else:
            direction = order[-1]
            tank.direction = direction
            dx, dy = DIRECTION_VECTORS[direction]
            self._try_move(tank, dx * tank.speed * dt, dy * tank.speed * dt)

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
        self._try_move(self.player2, dx * self.player2.speed * dt, dy * self.player2.speed * dt)

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

    def _update_bullets(self, tank, dt):
        remaining = []
        for bullet in tank.bullets:
            bullet["rect"].x += bullet["dx"] * BULLET_SPEED * dt
            bullet["rect"].y += bullet["dy"] * BULLET_SPEED * dt

            if not self.screen.get_rect().colliderect(bullet["rect"]):
                continue

            hit_wall = False
            for cell in self._cells_overlapping(bullet["rect"]):
                if cell in self.wall_cells:
                    self.wall_cells.discard(cell)
                    hit_wall = True
                    break
            if hit_wall:
                continue

            remaining.append(bullet)
        tank.bullets = remaining

    def _check_bullet_hits(self):
        self._resolve_hits(self.player1, self.player2, "player1")
        if self.winner is None:
            self._resolve_hits(self.player2, self.player1, "ai" if self.ai else "player2")

    def _resolve_hits(self, shooter, target, winner_label):
        remaining = []
        for bullet in shooter.bullets:
            if self.winner is None and bullet["rect"].colliderect(target.rect):
                if target.consume_shield():
                    continue
                self.winner = winner_label
            else:
                remaining.append(bullet)
        shooter.bullets = remaining

    def _update_powerup(self, dt):
        if self.powerup is None:
            self.powerup_spawn_timer -= dt
            if self.powerup_spawn_timer <= 0:
                self._spawn_powerup()
                self.powerup_spawn_timer = POWERUP_SPAWN_INTERVAL
            return

        self.powerup["timer"] -= dt
        if self.powerup["timer"] <= 0:
            self.powerup = None
            return

        for tank in (self.player1, self.player2):
            if tank.rect.colliderect(self.powerup["rect"]):
                tank.apply_effect(self.powerup["type"])
                self.powerup = None
                break

    def _spawn_powerup(self):
        free_cells = [
            (cx, cy)
            for cx in range(1, COLS - 1)
            for cy in range(1, ROWS - 1)
            if (cx, cy) not in self.wall_cells
        ]
        if not free_cells:
            return
        for _ in range(20):
            cx, cy = random.choice(free_cells)
            rect = pygame.Rect(0, 0, POWERUP_SIZE, POWERUP_SIZE)
            rect.center = (cx * CELL + CELL // 2, cy * CELL + CELL // 2)
            if rect.colliderect(self.player1.rect.inflate(CELL, CELL)) or rect.colliderect(
                self.player2.rect.inflate(CELL, CELL)
            ):
                continue
            self.powerup = {"rect": rect, "type": random.choice(POWERUP_TYPES), "timer": POWERUP_LIFETIME}
            return

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

        if self.powerup is not None:
            color, label = POWERUP_STYLE[self.powerup["type"]]
            pygame.draw.rect(self.screen, color, self.powerup["rect"], border_radius=6)
            pygame.draw.rect(self.screen, (20, 20, 20), self.powerup["rect"], 2, border_radius=6)
            icon = self.hud_font.render(label, True, (20, 20, 20))
            self.screen.blit(icon, icon.get_rect(center=self.powerup["rect"].center))

        for tank in (self.player1, self.player2):
            pygame.draw.rect(self.screen, tank.color, tank.rect, border_radius=3)
            if tank.effect == SHIELD:
                pygame.draw.circle(self.screen, (120, 180, 255), tank.rect.center, TANK_SIZE, 2)
            self._draw_barrel(tank)
            for bullet in tank.bullets:
                pygame.draw.rect(self.screen, (255, 230, 120), bullet["rect"])

        label = "KI" if self.ai else "Spieler 2"
        hud = self.hud_font.render(f"Spieler 1 (grün)   vs.   {label}", True, (220, 220, 220))
        self.screen.blit(hud, (20, 20))
        self._draw_effect_status(self.player1, "Spieler 1", 20, 44)
        self._draw_effect_status(self.player2, label, 20, 66)

        if self.winner is not None:
            names = {"player1": "Spieler 1", "player2": "Spieler 2", "ai": "Die KI"}
            text = self.font.render(f"{names[self.winner]} gewinnt! - beliebige Taste", True, (255, 255, 255))
            self.screen.blit(
                text, text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            )

    def _draw_effect_status(self, tank, name, x, y):
        if tank.effect is None:
            return
        text = f"{name}: {POWERUP_LABELS[tank.effect]} ({tank.effect_timer:.0f}s)"
        surface = self.hud_font.render(text, True, (255, 230, 150))
        self.screen.blit(surface, (x, y))

    def _draw_barrel(self, tank):
        dx, dy = DIRECTION_VECTORS[tank.direction]
        start = tank.rect.center
        end = (start[0] + dx * TANK_SIZE, start[1] + dy * TANK_SIZE)
        pygame.draw.line(self.screen, (40, 40, 40), start, end, 5)
