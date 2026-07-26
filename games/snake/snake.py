"""Snake: Solo, Steuerung mit den Pfeiltasten."""

import random

import pygame

from core.game_base import GameBase

CELL_SIZE = 20
MOVE_INTERVAL = 0.12  # Sekunden pro Schritt

DIRECTION_KEYS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}


class SnakeGame(GameBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.cols = screen.get_width() // CELL_SIZE
        self.rows = screen.get_height() // CELL_SIZE
        self.font = pygame.font.SysFont(None, 48)
        self._reset()

    def _reset(self):
        start = (self.cols // 2, self.rows // 2)
        self.snake = [start, (start[0] - 1, start[1]), (start[0] - 2, start[1])]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.food = self._spawn_food()
        self.time_since_move = 0
        self.game_over = False

    def _spawn_food(self):
        while True:
            pos = (random.randrange(self.cols), random.randrange(self.rows))
            if pos not in self.snake:
                return pos

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_over:
            self._reset()
            return

        new_direction = DIRECTION_KEYS.get(event.key)
        if new_direction is None:
            return
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.next_direction = new_direction

    def update(self, dt):
        if self.game_over:
            return

        self.time_since_move += dt
        if self.time_since_move < MOVE_INTERVAL:
            return
        self.time_since_move = 0

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        hits_wall = not (0 <= new_head[0] < self.cols) or not (0 <= new_head[1] < self.rows)
        if hits_wall or new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.food = self._spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill((15, 15, 20))

        for x, y in self.snake:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, (80, 200, 100), rect)

        food_rect = pygame.Rect(self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, (220, 80, 80), food_rect)

        if self.game_over:
            text = self.font.render("Game Over - beliebige Taste", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2)))
