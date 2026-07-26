"""Pong: 1 gegen 1 oder gegen eine KI (leicht/mittel/schwer/dynamisch).

Links immer W/S, rechts entweder Pfeil hoch/runter (2. Spieler) oder die KI.
Im Pause-Menü lässt sich die Ballgeschwindigkeit mit den Pfeiltasten links/rechts
anpassen; die Paddle-Geschwindigkeit bleibt davon unberührt.
"""

import pygame

from ai.dynamic_ai import DynamicAI
from ai.easy_ai import EasyAI
from ai.hard_ai import HardAI
from ai.medium_ai import MediumAI
from core.game_base import GameBase
from core.game_modes import AI_DYNAMIC, AI_EASY, AI_HARD, AI_MEDIUM, VS_PLAYER

AI_CLASSES = {
    AI_EASY: EasyAI,
    AI_MEDIUM: MediumAI,
    AI_HARD: HardAI,
    AI_DYNAMIC: DynamicAI,
}

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 400
BALL_SIZE = 15
BALL_SPEED = 350

MIN_SPEED_MULTIPLIER = 0.4
MAX_SPEED_MULTIPLIER = 2.5
SPEED_STEP = 0.2


class PongGame(GameBase):
    def __init__(self, screen, mode=VS_PLAYER):
        super().__init__(screen)
        self.mode = mode
        ai_class = AI_CLASSES.get(mode)
        self.ai = ai_class() if ai_class else None
        self.font = pygame.font.SysFont(None, 64)
        self.pause_font = pygame.font.SysFont(None, 28)
        self.ball_speed_multiplier = 1.0
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
        speed = BALL_SPEED * self.ball_speed_multiplier
        self.ball_velocity = [speed * direction, speed * 0.6]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        width, height = self.screen.get_size()
        bounds = self.screen.get_rect()

        if keys[pygame.K_w]:
            self.left_paddle.y -= PADDLE_SPEED * dt
        if keys[pygame.K_s]:
            self.left_paddle.y += PADDLE_SPEED * dt

        if self.ai is not None:
            self._move_ai_paddle(dt)
        else:
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
            if self.ai is not None:
                self.ai.on_point_scored(ai_scored=True)
            self._reset_ball(direction=1)
        elif self.ball.right >= width:
            self.left_score += 1
            if self.ai is not None:
                self.ai.on_point_scored(ai_scored=False)
            self._reset_ball(direction=-1)

    def _move_ai_paddle(self, dt):
        game_state = {
            "ball_center_y": self.ball.centery,
            "paddle_center_y": self.right_paddle.centery,
            "dt": dt,
        }
        direction = self.ai.decide_action(game_state)
        self.right_paddle.y += direction * self.ai.max_speed() * dt

    def handle_paused_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RIGHT:
            self._change_ball_speed(SPEED_STEP)
        elif event.key == pygame.K_LEFT:
            self._change_ball_speed(-SPEED_STEP)

    def _change_ball_speed(self, delta):
        old_multiplier = self.ball_speed_multiplier
        new_multiplier = round(min(MAX_SPEED_MULTIPLIER, max(MIN_SPEED_MULTIPLIER, old_multiplier + delta)), 2)
        if new_multiplier == old_multiplier:
            return
        ratio = new_multiplier / old_multiplier
        self.ball_velocity = [self.ball_velocity[0] * ratio, self.ball_velocity[1] * ratio]
        self.ball_speed_multiplier = new_multiplier

    def draw_pause_extra(self, screen):
        width, height = screen.get_size()
        text = self.pause_font.render(
            f"<- / -> : Ballgeschwindigkeit ({self.ball_speed_multiplier:.1f}x)", True, (200, 200, 200)
        )
        screen.blit(text, text.get_rect(center=(width // 2, height // 2 + 110)))

    def draw(self):
        width, height = self.screen.get_size()
        self.screen.fill((10, 10, 15))
        pygame.draw.rect(self.screen, (255, 255, 255), self.left_paddle)
        pygame.draw.rect(self.screen, (255, 255, 255), self.right_paddle)
        pygame.draw.ellipse(self.screen, (255, 255, 255), self.ball)
        pygame.draw.aaline(self.screen, (80, 80, 80), (width // 2, 0), (width // 2, height))

        score_text = self.font.render(f"{self.left_score}   {self.right_score}", True, (255, 255, 255))
        self.screen.blit(score_text, score_text.get_rect(center=(width // 2, 50)))
