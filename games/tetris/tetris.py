"""Tetris: Solo, gegen eine KI oder gegen einen 2. Spieler.

Versus-Modus wie in modernen Tetris-Duellen (z.B. Tetris 99): wer 2+ Reihen auf
einmal räumt, schickt dem Gegner Müll-Reihen (garbage lines) rein. Verliert, wer
zuerst über den oberen Rand hinaus stapelt.
"""

import pygame

from ai.tetris_ai import TetrisAI
from core.game_base import GameBase
from core.game_modes import SOLO, VS_AI, VS_PLAYER
from games.tetris.board import CELL_PIXELS, COLS, ROWS, TetrisBoard
from games.tetris.shapes import COLORS

BOARD_WIDTH = COLS * CELL_PIXELS
BOARD_HEIGHT = ROWS * CELL_PIXELS
BOARD_GAP = 60

LEFT_KEYS = {
    pygame.K_a: ("move", -1),
    pygame.K_d: ("move", 1),
    pygame.K_w: ("rotate", None),
    pygame.K_s: ("soft_drop", None),
}
ARROW_KEYS = {
    pygame.K_LEFT: ("move", -1),
    pygame.K_RIGHT: ("move", 1),
    pygame.K_UP: ("rotate", None),
    pygame.K_DOWN: ("soft_drop", None),
}


class TetrisGame(GameBase):
    def __init__(self, screen, mode=SOLO):
        super().__init__(screen)
        self.mode = mode
        self.font = pygame.font.SysFont(None, 44)
        self.hud_font = pygame.font.SysFont(None, 22)
        self._reset()

    def _reset(self):
        self.board_left = TetrisBoard()
        self.board_right = TetrisBoard() if self.mode != SOLO else None
        self.ai = TetrisAI() if self.mode == VS_AI else None
        self.finished = False
        self._layout_boards()

    def _layout_boards(self):
        width, height = self.screen.get_size()
        top = (height - BOARD_HEIGHT) // 2
        if self.board_right is None:
            self.left_offset = ((width - BOARD_WIDTH) // 2, top)
            self.right_offset = None
        else:
            total_width = BOARD_WIDTH * 2 + BOARD_GAP
            start_x = (width - total_width) // 2
            self.left_offset = (start_x, top)
            self.right_offset = (start_x + BOARD_WIDTH + BOARD_GAP, top)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.finished:
            self._reset()
            return

        if self.mode == VS_PLAYER:
            self._dispatch(self.board_left, LEFT_KEYS, event.key)
            self._dispatch(self.board_right, ARROW_KEYS, event.key)
            if event.key == pygame.K_LSHIFT:
                self.board_left.hard_drop()
            if event.key == pygame.K_RSHIFT:
                self.board_right.hard_drop()
        else:
            self._dispatch(self.board_left, ARROW_KEYS, event.key)
            if event.key == pygame.K_SPACE:
                self.board_left.hard_drop()

    def _dispatch(self, board, key_map, key):
        action = key_map.get(key)
        if action is None:
            return
        name, arg = action
        if name == "move":
            board.move(arg)
        elif name == "rotate":
            board.rotate()
        elif name == "soft_drop":
            board.soft_drop()

    def update(self, dt):
        if self.finished:
            return

        self.board_left.update(dt)
        if self.board_right is not None:
            self.board_right.update(dt)
        if self.ai is not None:
            self.ai.control(self.board_right, dt)

        self._exchange_garbage()
        self._check_finished()

    def _exchange_garbage(self):
        if self.board_right is None:
            return
        sent_left = self.board_left.pop_garbage_to_send()
        if sent_left:
            self.board_right.receive_garbage(sent_left)
        sent_right = self.board_right.pop_garbage_to_send()
        if sent_right:
            self.board_left.receive_garbage(sent_right)

    def _check_finished(self):
        if self.board_right is None:
            self.finished = self.board_left.game_over
        else:
            self.finished = self.board_left.game_over or self.board_right.game_over

    def draw(self):
        self.screen.fill((15, 15, 20))
        solo = self.board_right is None
        self._draw_board(self.board_left, self.left_offset, "Du" if solo else "Spieler 1")
        if self.board_right is not None:
            label = "KI" if self.ai else "Spieler 2"
            self._draw_board(self.board_right, self.right_offset, label)

        if self.finished:
            text = self.font.render(self._result_text(), True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(self.screen.get_width() // 2, 30)))

    def _result_text(self):
        if self.board_right is None:
            return "Game Over - beliebige Taste"
        left_lost, right_lost = self.board_left.game_over, self.board_right.game_over
        if left_lost and right_lost:
            return "Unentschieden - beliebige Taste"
        winner = ("Die KI" if self.ai else "Spieler 2") if left_lost else "Spieler 1"
        return f"{winner} gewinnt - beliebige Taste"

    def _draw_board(self, board, offset, label):
        ox, oy = offset
        frame = pygame.Rect(ox - 4, oy - 4, BOARD_WIDTH + 8, BOARD_HEIGHT + 8)
        pygame.draw.rect(self.screen, (60, 60, 70), frame, 2)

        for row in range(ROWS):
            for col in range(COLS):
                cell = board.grid[row][col]
                if cell is not None:
                    self._draw_cell(ox, oy, col, row, self._color_for(cell))

        for cx, cy in board.piece_cells():
            gx, gy = board.piece_x + cx, board.piece_y + cy
            if gy >= 0:
                self._draw_cell(ox, oy, gx, gy, COLORS[board.piece_type])

        name = self.hud_font.render(f"{label}  |  Punkte: {board.score}", True, (220, 220, 220))
        self.screen.blit(name, (ox, oy - 26))

        if board.game_over:
            overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (ox, oy))

    def _color_for(self, cell):
        return (120, 120, 120) if cell == "garbage" else COLORS[cell]

    def _draw_cell(self, ox, oy, col, row, color):
        rect = pygame.Rect(ox + col * CELL_PIXELS, oy + row * CELL_PIXELS, CELL_PIXELS - 1, CELL_PIXELS - 1)
        pygame.draw.rect(self.screen, color, rect)
