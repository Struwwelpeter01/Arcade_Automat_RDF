"""Breakout: Solo, Steuerung mit Pfeil links/rechts.

Klassisches Breakout ist ein geteiltes Spielfeld mit einem Ball - ein "Duell"-Modus
würde zwei komplett getrennte Spielfelder brauchen und den Spielcharakter verändern,
deshalb bleibt es hier (wie Snake) bei Solo.
"""

import math

import pygame

from core.game_base import GameBase

PADDLE_WIDTH = 110
PADDLE_HEIGHT = 16
PADDLE_SPEED = 500
BALL_SIZE = 14
BALL_SPEED = 320

BRICK_COLS = 10
BRICK_ROWS = 5
BRICK_GAP = 6
BRICK_TOP_MARGIN = 60
BRICK_SIDE_MARGIN = 40
BRICK_HEIGHT = 24

ROW_COLORS = [
    (220, 80, 80),
    (220, 150, 70),
    (220, 210, 70),
    (110, 200, 90),
    (90, 150, 220),
]

STARTING_LIVES = 3


class BreakoutGame(GameBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 48)
        self.hud_font = pygame.font.SysFont(None, 28)
        width, _ = screen.get_size()
        self.brick_width = (width - 2 * BRICK_SIDE_MARGIN - (BRICK_COLS - 1) * BRICK_GAP) / BRICK_COLS
        self._reset()

    def _reset(self):
        width, height = self.screen.get_size()
        self.paddle = pygame.Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.paddle.midbottom = (width // 2, height - 30)
        self.lives = STARTING_LIVES
        self.score = 0
        self.game_over = False
        self.won = False
        self._spawn_bricks()
        self._reset_ball()

    def _spawn_bricks(self):
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = BRICK_SIDE_MARGIN + col * (self.brick_width + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)
                rect = pygame.Rect(x, y, self.brick_width, BRICK_HEIGHT)
                self.bricks.append((rect, ROW_COLORS[row % len(ROW_COLORS)], (BRICK_ROWS - row) * 10))

    def _reset_ball(self):
        width, height = self.screen.get_size()
        self.ball = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.ball.center = (width // 2, height - 80)
        self.ball_velocity = [BALL_SPEED * 0.6, -math.sqrt(BALL_SPEED**2 - (BALL_SPEED * 0.6) ** 2)]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and (self.game_over or self.won):
            self._reset()

    def update(self, dt):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()
        width, height = self.screen.get_size()

        if keys[pygame.K_LEFT]:
            self.paddle.x -= PADDLE_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.paddle.x += PADDLE_SPEED * dt
        self.paddle.clamp_ip(self.screen.get_rect())

        self.ball.x += self.ball_velocity[0] * dt
        self.ball.y += self.ball_velocity[1] * dt

        if self.ball.left <= 0 or self.ball.right >= width:
            self.ball_velocity[0] *= -1
        if self.ball.top <= 0:
            self.ball_velocity[1] *= -1

        if self.ball.colliderect(self.paddle) and self.ball_velocity[1] > 0:
            self._bounce_off_paddle()

        self._handle_brick_hit()

        if self.ball.top > height:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

        if not self.bricks:
            self.won = True

    def _bounce_off_paddle(self):
        offset = (self.ball.centerx - self.paddle.centerx) / (PADDLE_WIDTH / 2)
        offset = max(-0.9, min(0.9, offset))
        vx = BALL_SPEED * offset
        vy = -math.sqrt(max(BALL_SPEED**2 - vx**2, 0.0))
        self.ball_velocity = [vx, vy]

    def _handle_brick_hit(self):
        brick_rects = [b[0] for b in self.bricks]
        hit_index = self.ball.collidelist(brick_rects)
        if hit_index == -1:
            return
        rect, _, points = self.bricks.pop(hit_index)
        self.score += points
        if abs(self.ball.centerx - rect.centerx) > abs(self.ball.centery - rect.centery):
            self.ball_velocity[0] *= -1
        else:
            self.ball_velocity[1] *= -1

    def draw(self):
        width, height = self.screen.get_size()
        self.screen.fill((15, 15, 20))

        for rect, color, _ in self.bricks:
            pygame.draw.rect(self.screen, color, rect, border_radius=3)

        pygame.draw.rect(self.screen, (230, 230, 230), self.paddle, border_radius=4)
        pygame.draw.ellipse(self.screen, (230, 230, 230), self.ball)

        hud = self.hud_font.render(f"Punkte: {self.score}    Leben: {self.lives}", True, (255, 255, 255))
        self.screen.blit(hud, (20, 20))

        if self.game_over:
            text = self.font.render("Game Over - beliebige Taste", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(width // 2, height // 2)))
        elif self.won:
            text = self.font.render("Gewonnen! - beliebige Taste", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(width // 2, height // 2)))
