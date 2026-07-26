"""Jump'n'Run: Dino-Clone (Chrome-Offline-Spiel), solo. Springen mit Pfeil hoch."""

import random

import pygame

from core.game_base import GameBase

GROUND_Y_OFFSET = 100
GRAVITY = 1800
JUMP_SPEED = -700
PLAYER_SIZE = 40
OBSTACLE_WIDTH = 25
OBSTACLE_HEIGHT_RANGE = (30, 60)
BASE_SPEED = 350
SPEED_PER_SCORE = 5
JUMP_KEYS = (pygame.K_UP, pygame.K_SPACE)


class JumpNRunGame(GameBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 48)
        self._reset()

    def _reset(self):
        width, height = self.screen.get_size()
        self.ground_y = height - GROUND_Y_OFFSET
        self.player = pygame.Rect(80, self.ground_y - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_y = 0
        self.on_ground = True
        self.obstacles = []
        self.spawn_timer = 1.0
        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            self._reset()
            return

        if event.key in JUMP_KEYS and self.on_ground:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False

    def update(self, dt):
        if self.game_over:
            return

        self.velocity_y += GRAVITY * dt
        self.player.y += self.velocity_y * dt
        if self.player.y >= self.ground_y - self.player.height:
            self.player.y = self.ground_y - self.player.height
            self.velocity_y = 0
            self.on_ground = True

        speed = BASE_SPEED + self.score * SPEED_PER_SCORE

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_obstacle()
            self.spawn_timer = random.uniform(0.9, 1.8)

        for obstacle in self.obstacles:
            obstacle.x -= speed * dt
        self.obstacles = [o for o in self.obstacles if o.right > 0]

        if any(self.player.colliderect(o) for o in self.obstacles):
            self.game_over = True
            return

        self.score += dt * 10

    def _spawn_obstacle(self):
        width = self.screen.get_width()
        height = random.randint(*OBSTACLE_HEIGHT_RANGE)
        self.obstacles.append(pygame.Rect(width, self.ground_y - height, OBSTACLE_WIDTH, height))

    def draw(self):
        width = self.screen.get_width()
        self.screen.fill((230, 230, 230))
        pygame.draw.line(self.screen, (50, 50, 50), (0, self.ground_y), (width, self.ground_y), 2)
        pygame.draw.rect(self.screen, (60, 60, 60), self.player)

        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, (40, 120, 40), obstacle)

        score_text = self.font.render(f"Punkte: {int(self.score)}", True, (30, 30, 30))
        self.screen.blit(score_text, (20, 20))

        if self.game_over:
            text = self.font.render("Game Over - beliebige Taste", True, (200, 30, 30))
            self.screen.blit(text, text.get_rect(center=(width // 2, self.screen.get_height() // 2)))
