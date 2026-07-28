"""Panzer-Duell: 2 Panzer in einer Arena mit zerstörbaren Mauern (Battle-City-Stil).

Gegen KI oder gegen einen 2. Spieler - eine echte Solo-Variante ergibt hier keinen
Sinn, das Genre lebt vom Duell. Wer zuerst getroffen wird, verliert die Runde.
Bewegung ist achsengebunden (keine Diagonalen) - außer das Diagonalfahrt-Powerup
ist gerade aktiv. Von zwei gleichzeitig gehaltenen Richtungstasten gewinnt immer
die zuletzt gedrückte, damit sich Richtungswechsel sauber anfühlen.

Alle 10-15s spawnt ein zufälliges Powerup (fair verteilt über einen Shuffle-Bag,
damit nicht zufällig ewig derselbe Typ ausbleibt), das nach 30s ungenutzt wieder
verschwindet. Wer es einsammelt, bekommt 15s lang eine Fähigkeit:
- Dauerfeuer: Feuertaste halten = durchgehend schnelles Schießen
- Speed-Boost: schneller fahren
- Schutzschild: blockt genau einen Treffer
- Diagonalfahrt: einzige Ausnahme von der Achsenbindung
Zwei Powerups wirken stattdessen auf den GEGNER (Sabotage statt Selbstbuff):
- Vergrößerung: der Gegner wird größer (leichteres Ziel)
- Invertierte Steuerung: alle Richtungstasten des Gegners sind vertauscht

Ohne Powerup kann trotzdem schon mit moderater Feuerrate geschossen werden -
man ist nicht mehr blockiert, nur weil die eigene letzte Kugel noch fliegt.
Easter Egg: Sind alle zerstörbaren Mauern weg, fliegen Kugeln am Bildschirmrand
auf die gegenüberliegende Seite weiter, statt zu verschwinden.
"""

import random

import pygame

from ai.tank_ai import TankAI
from core.game_base import GameBase
from core.game_modes import VS_AI, VS_PLAYER

CELL = 32
COLS = 40  # 40 * 32 = 1280, füllt das verbreiterte Fenster passgenau aus
ROWS = 24

TANK_SIZE = 24
TANK_SPEED = 170
BULLET_SPEED = 420
BULLET_SIZE = 6
SHOOT_COOLDOWN = 0.25
BASE_MAX_BULLETS = 3  # so blockiert die eigene fliegende Kugel nicht den nächsten Schuss

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"
DIRECTION_VECTORS = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}
OPPOSITE_DIRECTION = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
DIAGONAL_FACTOR = 0.70710678  # 1/sqrt(2), damit Diagonalfahrt nicht schneller ist

# Powerups
POWERUP_SPAWN_INTERVAL_RANGE = (10.0, 15.0)
POWERUP_LIFETIME = 30.0
EFFECT_DURATION = 15.0
POWERUP_SIZE = 22

RAPID_FIRE = "rapid_fire"
SPEED_BOOST = "speed"
SHIELD = "shield"
DIAGONAL = "diagonal"
ENLARGE = "enlarge"
INVERT = "invert"
POWERUP_TYPES = [RAPID_FIRE, SPEED_BOOST, SHIELD, DIAGONAL, ENLARGE, INVERT]
DEBUFF_TYPES = {ENLARGE, INVERT}  # wirken auf den Gegner statt auf den Einsammler

RAPID_FIRE_COOLDOWN = 0.08
RAPID_FIRE_MAX_BULLETS = 6
SPEED_BOOST_MULTIPLIER = 1.6
ENLARGE_SCALE = 1.8

POWERUP_STYLE = {
    RAPID_FIRE: ((240, 210, 60), "R"),
    SPEED_BOOST: ((80, 220, 220), "S"),
    SHIELD: ((90, 140, 240), "SH"),
    DIAGONAL: ((190, 90, 220), "D"),
    ENLARGE: ((255, 90, 90), "L"),
    INVERT: ((255, 150, 40), "I"),
}
WINNER_NAMES = {"player1": "Spieler 1", "player2": "Spieler 2", "ai": "Die KI"}

POWERUP_LABELS = {
    RAPID_FIRE: "Dauerfeuer",
    SPEED_BOOST: "Speed-Boost",
    SHIELD: "Schutzschild",
    DIAGONAL: "Diagonalfahrt",
    ENLARGE: "Vergrößert",
    INVERT: "Invertiert",
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
        self.effect = None  # Selbstbuff: rapid_fire/speed/shield/diagonal
        self.effect_timer = 0.0
        self.debuff = None  # vom Gegner verursacht: enlarge/invert
        self.debuff_timer = 0.0
        self.unlimited_bullets = False  # Easter Egg: gesetzt, sobald alle Mauern weg sind

    @property
    def speed(self):
        return TANK_SPEED * SPEED_BOOST_MULTIPLIER if self.effect == SPEED_BOOST else TANK_SPEED

    @property
    def max_bullets(self):
        if self.unlimited_bullets:
            return float("inf")
        return RAPID_FIRE_MAX_BULLETS if self.effect == RAPID_FIRE else BASE_MAX_BULLETS

    @property
    def shoot_cooldown(self):
        return RAPID_FIRE_COOLDOWN if self.effect == RAPID_FIRE else SHOOT_COOLDOWN

    @property
    def diagonal(self):
        return self.effect == DIAGONAL

    @property
    def inverted(self):
        return self.debuff == INVERT

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

    def apply_debuff(self, debuff):
        if self.debuff == ENLARGE and debuff != ENLARGE:
            self._resize(TANK_SIZE)
        self.debuff = debuff
        self.debuff_timer = EFFECT_DURATION
        if debuff == ENLARGE:
            self._resize(int(TANK_SIZE * ENLARGE_SCALE))

    def update_effect(self, dt):
        if self.effect is not None:
            self.effect_timer -= dt
            if self.effect_timer <= 0:
                self.effect = None
                self.effect_timer = 0.0
        if self.debuff is not None:
            self.debuff_timer -= dt
            if self.debuff_timer <= 0:
                if self.debuff == ENLARGE:
                    self._resize(TANK_SIZE)
                self.debuff = None
                self.debuff_timer = 0.0

    def consume_shield(self):
        if self.effect == SHIELD:
            self.effect = None
            self.effect_timer = 0.0
            return True
        return False

    def _resize(self, size):
        center = self.rect.center
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = center


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
        self.last_winner = None  # bleibt über _reset() hinweg erhalten, damit er dauerhaft im HUD steht
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
        self._powerup_bag = []
        self.powerup_spawn_timer = random.uniform(*POWERUP_SPAWN_INTERVAL_RANGE)

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

        # Dauerfeuer: Taste halten löst automatisch weitere Schüsse aus (statt nur bei KEYDOWN).
        if self.player1.effect == RAPID_FIRE and keys[pygame.K_SPACE]:
            self.player1.try_shoot()
        if self.ai is None and self.player2.effect == RAPID_FIRE and keys[pygame.K_RETURN]:
            self.player2.try_shoot()

        walls_gone = not self.wall_cells
        for tank in (self.player1, self.player2):
            tank.cooldown = max(0.0, tank.cooldown - dt)
            tank.update_effect(dt)
            tank.unlimited_bullets = walls_gone

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
            facing = order[-1]
            if dx and dy:
                dx *= DIAGONAL_FACTOR
                dy *= DIAGONAL_FACTOR
        else:
            facing = order[-1]
            dx, dy = DIRECTION_VECTORS[facing]

        if tank.inverted:
            dx, dy = -dx, -dy
            facing = OPPOSITE_DIRECTION[facing]

        tank.direction = facing
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
        screen_rect = self.screen.get_rect()
        wrap = not self.wall_cells  # Easter Egg: alle Mauern weg -> Kugeln laufen am Rand um
        remaining = []
        for bullet in tank.bullets:
            rect = bullet["rect"]
            rect.x += bullet["dx"] * BULLET_SPEED * dt
            rect.y += bullet["dy"] * BULLET_SPEED * dt

            if not screen_rect.colliderect(rect):
                if not wrap:
                    continue
                if rect.right < screen_rect.left:
                    rect.left = screen_rect.right
                elif rect.left > screen_rect.right:
                    rect.right = screen_rect.left
                if rect.bottom < screen_rect.top:
                    rect.top = screen_rect.bottom
                elif rect.top > screen_rect.bottom:
                    rect.bottom = screen_rect.top

            hit_wall = False
            for cell in self._cells_overlapping(rect):
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
                self.last_winner = winner_label
            else:
                remaining.append(bullet)
        shooter.bullets = remaining

    def _update_powerup(self, dt):
        if self.powerup is None:
            self.powerup_spawn_timer -= dt
            if self.powerup_spawn_timer <= 0:
                self._spawn_powerup()
                self.powerup_spawn_timer = random.uniform(*POWERUP_SPAWN_INTERVAL_RANGE)
            return

        self.powerup["timer"] -= dt
        if self.powerup["timer"] <= 0:
            self.powerup = None
            return

        for tank, opponent in ((self.player1, self.player2), (self.player2, self.player1)):
            if tank.rect.colliderect(self.powerup["rect"]):
                self._apply_powerup(tank, opponent, self.powerup["type"])
                self.powerup = None
                break

    def _apply_powerup(self, picker, opponent, powerup_type):
        if powerup_type in DEBUFF_TYPES:
            opponent.apply_debuff(powerup_type)
        else:
            picker.apply_effect(powerup_type)

    def _next_powerup_type(self):
        # Shuffle-Bag statt random.choice: garantiert, dass jeder Typ einmal
        # drankommt, bevor sich einer wiederholt - kein Typ bleibt lange aus.
        if not self._powerup_bag:
            self._powerup_bag = POWERUP_TYPES.copy()
            random.shuffle(self._powerup_bag)
        return self._powerup_bag.pop()

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
            self.powerup = {"rect": rect, "type": self._next_powerup_type(), "timer": POWERUP_LIFETIME}
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
                pygame.draw.circle(self.screen, (120, 180, 255), tank.rect.center, tank.rect.width, 2)
            if tank.debuff == ENLARGE:
                pygame.draw.rect(self.screen, (255, 60, 60), tank.rect, 2, border_radius=3)
            if tank.debuff == INVERT:
                pygame.draw.rect(self.screen, (255, 140, 0), tank.rect, 2, border_radius=3)
            self._draw_barrel(tank)
            for bullet in tank.bullets:
                pygame.draw.rect(self.screen, (255, 230, 120), bullet["rect"])

        label = "KI" if self.ai else "Spieler 2"
        hud = self.hud_font.render(f"Spieler 1 (grün)   vs.   {label}", True, (220, 220, 220))
        self.screen.blit(hud, (20, 20))
        self._draw_effect_status(self.player1, "Spieler 1", 20, 44)
        self._draw_effect_status(self.player2, label, 20, 66)

        if self.last_winner is not None:
            last_text = self.hud_font.render(
                f"Letzter Sieger: {WINNER_NAMES[self.last_winner]}", True, (255, 220, 120)
            )
            self.screen.blit(last_text, last_text.get_rect(topright=(self.screen.get_width() - 20, 20)))

        if self.winner is not None:
            text = self.font.render(
                f"{WINNER_NAMES[self.winner]} gewinnt! - beliebige Taste", True, (255, 255, 255)
            )
            self.screen.blit(
                text, text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            )

    def _draw_effect_status(self, tank, name, x, y):
        parts = []
        if tank.effect is not None:
            parts.append(f"{POWERUP_LABELS[tank.effect]} ({tank.effect_timer:.0f}s)")
        if tank.debuff is not None:
            parts.append(f"{POWERUP_LABELS[tank.debuff]} ({tank.debuff_timer:.0f}s)")
        if not parts:
            return
        surface = self.hud_font.render(f"{name}: " + ", ".join(parts), True, (255, 230, 150))
        self.screen.blit(surface, (x, y))

    def _draw_barrel(self, tank):
        dx, dy = DIRECTION_VECTORS[tank.direction]
        start = tank.rect.center
        end = (start[0] + dx * tank.rect.width, start[1] + dy * tank.rect.width)
        pygame.draw.line(self.screen, (40, 40, 40), start, end, 5)
