"""Pong: 1 gegen 1. Links W/S, rechts Pfeil hoch/runter."""

import pygame

from core.game_base import GameBase

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 400
BALL_SIZE = 15
BALL_SPEED = 350


class PongGame(GameBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 64)
        self._reset()

    def _reset(self):
        width, height = self.screen.get_size()
        self.left_paddle = pygame.Rect(30, height // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.right_paddle = pygame.Rect(
            width - 30 - PADDLE_WIDTH, height // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT
        )
        self.left_score = 0
        self.right_score = 0
        self._reset_ball(direction=1)

    def _reset_ball(self, direction):
        width, height = self.screen.get_size()
        self.ball = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.ball.center = (width // 2, height // 2)
        self.ball_velocity = [BALL_SPEED * direction, BALL_SPEED * 0.6]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        width, height = self.screen.get_size()
        bounds = self.screen.get_rect()

        if keys[pygame.K_w]:
            self.left_paddle.y -= PADDLE_SPEED * dt
        if keys[pygame.K_s]:
            self.left_paddle.y += PADDLE_SPEED * dt
        if keys[pygame.K_UP]:
            self.right_paddle.y -= PADDLE_SPEED * dt
        if keys[pygame.K_DOWN]:
            self.right_paddle.y += PADDLE_SPEED * dt

        self.left_paddle.clamp_ip(bounds)
        self.right_paddle.clamp_ip(bounds)

        self.ball.x += self.ball_velocity[0] * dt
        self.ball.y += self.ball_velocity[1] * dt

        if self.ball.top <= 0 or self.ball.bottom >= height:
            self.ball_velocity[1] *= -1

        if self.ball.colliderect(self.left_paddle) and self.ball_velocity[0] < 0:
            self.ball_velocity[0] *= -1
        elif self.ball.colliderect(self.right_paddle) and self.ball_velocity[0] > 0:
            self.ball_velocity[0] *= -1

        if self.ball.left <= 0:
            self.right_score += 1
            self._reset_ball(direction=1)
        elif self.ball.right >= width:
            self.left_score += 1
            self._reset_ball(direction=-1)

    def draw(self):
        width, height = self.screen.get_size()
        self.screen.fill((10, 10, 15))
        pygame.draw.rect(self.screen, (255, 255, 255), self.left_paddle)
        pygame.draw.rect(self.screen, (255, 255, 255), self.right_paddle)
        pygame.draw.ellipse(self.screen, (255, 255, 255), self.ball)
        pygame.draw.aaline(self.screen, (80, 80, 80), (width // 2, 0), (width // 2, height))

        score_text = self.font.render(f"{self.left_score}   {self.right_score}", True, (255, 255, 255))
        self.screen.blit(score_text, score_text.get_rect(center=(width // 2, 50)))
