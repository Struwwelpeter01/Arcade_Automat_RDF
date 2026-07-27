"""Asteroids: Solo. Pfeil links/rechts drehen, Pfeil hoch beschleunigen, Leertaste schießen.

Klassisches Asteroids ist reines Score-Attack ohne Gegnerschiff - ein "Gegen-KI"-Modus
würde es eigentlich in ein Schiffs-Duell verwandeln (das übernimmt stattdessen das
Panzer-Duell), deshalb bleibt es hier bei Solo.
"""

import math
import random

import pygame

from core.game_base import GameBase

SHIP_RADIUS = 14
ROTATE_SPEED = 220  # Grad/Sekunde
THRUST = 260
FRICTION = 0.55  # Anteil der Geschwindigkeit, der pro Sekunde erhalten bleibt
MAX_SPEED = 380

BULLET_SPEED = 520
BULLET_LIFETIME = 0.9
MAX_BULLETS = 4

INVULNERABLE_TIME = 2.0
STARTING_LIVES = 3

ASTEROID_RADII = {"large": 40, "medium": 22, "small": 12}
ASTEROID_SPEED_RANGE = (40, 110)
ASTEROID_SCORE = {"large": 20, "medium": 50, "small": 100}
SPLIT_INTO = {"large": "medium", "medium": "small"}


def _wrap(value, maximum):
    return value % maximum


class Asteroid:
    def __init__(self, x, y, size, velocity=None):
        self.x = x
        self.y = y
        self.size = size
        self.radius = ASTEROID_RADII[size]
        if velocity is None:
            angle = random.uniform(0, 360)
            speed = random.uniform(*ASTEROID_SPEED_RANGE)
            rad = math.radians(angle)
            velocity = (math.cos(rad) * speed, math.sin(rad) * speed)
        self.vx, self.vy = velocity

    def update(self, dt, width, height):
        self.x = _wrap(self.x + self.vx * dt, width)
        self.y = _wrap(self.y + self.vy * dt, height)


class Bullet:
    def __init__(self, x, y, angle):
        rad = math.radians(angle)
        self.x = x
        self.y = y
        self.vx = math.sin(rad) * BULLET_SPEED
        self.vy = -math.cos(rad) * BULLET_SPEED
        self.time_left = BULLET_LIFETIME

    def update(self, dt, width, height):
        self.x = _wrap(self.x + self.vx * dt, width)
        self.y = _wrap(self.y + self.vy * dt, height)
        self.time_left -= dt


class AsteroidsGame(GameBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 48)
        self.hud_font = pygame.font.SysFont(None, 28)
        self._reset()

    def _reset(self):
        width, height = self.screen.get_size()
        self.ship_x, self.ship_y = width / 2, height / 2
        self.ship_angle = 0.0
        self.ship_vx = 0.0
        self.ship_vy = 0.0
        self.invulnerable_timer = INVULNERABLE_TIME
        self.lives = STARTING_LIVES
        self.score = 0
        self.game_over = False
        self.bullets = []
        self.wave = 1
        self.asteroids = []
        self._spawn_wave()

    def _spawn_wave(self):
        width, height = self.screen.get_size()
        count = 3 + self.wave
        for _ in range(count):
            while True:
                x, y = random.uniform(0, width), random.uniform(0, height)
                if math.hypot(x - self.ship_x, y - self.ship_y) > 150:
                    break
            self.asteroids.append(Asteroid(x, y, "large"))

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.game_over:
            self._reset()
            return
        if event.key == pygame.K_SPACE and len(self.bullets) < MAX_BULLETS:
            self.bullets.append(Bullet(self.ship_x, self.ship_y, self.ship_angle))

    def update(self, dt):
        if self.game_over:
            return

        width, height = self.screen.get_size()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.ship_angle -= ROTATE_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.ship_angle += ROTATE_SPEED * dt
        if keys[pygame.K_UP]:
            self._apply_thrust(dt)

        self.ship_vx *= FRICTION**dt
        self.ship_vy *= FRICTION**dt
        self.ship_x = _wrap(self.ship_x + self.ship_vx * dt, width)
        self.ship_y = _wrap(self.ship_y + self.ship_vy * dt, height)

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        for bullet in self.bullets:
            bullet.update(dt, width, height)
        self.bullets = [b for b in self.bullets if b.time_left > 0]

        for asteroid in self.asteroids:
            asteroid.update(dt, width, height)

        self._handle_bullet_hits()
        self._handle_ship_collision()

        if not self.asteroids:
            self.wave += 1
            self._spawn_wave()

    def _apply_thrust(self, dt):
        rad = math.radians(self.ship_angle)
        self.ship_vx += math.sin(rad) * THRUST * dt
        self.ship_vy -= math.cos(rad) * THRUST * dt
        speed = math.hypot(self.ship_vx, self.ship_vy)
        if speed > MAX_SPEED:
            self.ship_vx = self.ship_vx / speed * MAX_SPEED
            self.ship_vy = self.ship_vy / speed * MAX_SPEED

    def _handle_bullet_hits(self):
        remaining_bullets = []
        for bullet in self.bullets:
            hit = None
            for asteroid in self.asteroids:
                if math.hypot(bullet.x - asteroid.x, bullet.y - asteroid.y) < asteroid.radius:
                    hit = asteroid
                    break
            if hit is None:
                remaining_bullets.append(bullet)
            else:
                self._destroy_asteroid(hit)
        self.bullets = remaining_bullets

    def _destroy_asteroid(self, asteroid):
        self.asteroids.remove(asteroid)
        self.score += ASTEROID_SCORE[asteroid.size]
        next_size = SPLIT_INTO.get(asteroid.size)
        if next_size:
            for _ in range(2):
                self.asteroids.append(Asteroid(asteroid.x, asteroid.y, next_size))

    def _handle_ship_collision(self):
        if self.invulnerable_timer > 0:
            return
        for asteroid in self.asteroids:
            if math.hypot(self.ship_x - asteroid.x, self.ship_y - asteroid.y) < asteroid.radius + SHIP_RADIUS:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self._respawn_ship()
                return

    def _respawn_ship(self):
        width, height = self.screen.get_size()
        self.ship_x, self.ship_y = width / 2, height / 2
        self.ship_vx = self.ship_vy = 0.0
        self.invulnerable_timer = INVULNERABLE_TIME

    def draw(self):
        width, height = self.screen.get_size()
        self.screen.fill((5, 5, 15))

        for asteroid in self.asteroids:
            pygame.draw.circle(self.screen, (160, 160, 170), (int(asteroid.x), int(asteroid.y)), asteroid.radius, 2)

        for bullet in self.bullets:
            pygame.draw.circle(self.screen, (255, 230, 120), (int(bullet.x), int(bullet.y)), 3)

        if self.invulnerable_timer <= 0 or int(self.invulnerable_timer * 10) % 2 == 0:
            self._draw_ship()

        hud = self.hud_font.render(f"Punkte: {self.score}    Leben: {self.lives}", True, (255, 255, 255))
        self.screen.blit(hud, (20, 20))

        if self.game_over:
            text = self.font.render("Game Over - beliebige Taste", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(width // 2, height // 2)))

    def _draw_ship(self):
        rad = math.radians(self.ship_angle)
        tip = (self.ship_x + math.sin(rad) * SHIP_RADIUS, self.ship_y - math.cos(rad) * SHIP_RADIUS)
        left_rad = math.radians(self.ship_angle + 140)
        right_rad = math.radians(self.ship_angle - 140)
        left = (self.ship_x + math.sin(left_rad) * SHIP_RADIUS, self.ship_y - math.cos(left_rad) * SHIP_RADIUS)
        right = (self.ship_x + math.sin(right_rad) * SHIP_RADIUS, self.ship_y - math.cos(right_rad) * SHIP_RADIUS)
        pygame.draw.polygon(self.screen, (255, 255, 255), [tip, left, right], 2)
