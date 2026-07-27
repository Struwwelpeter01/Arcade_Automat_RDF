"""Tetris-Spielfeld: reine Spiellogik (Grid, aktueller Stein, Schwerkraft, Linien-Clear,
Garbage-Lines) getrennt vom Input - dieselbe Klasse bedient Solo, 2. Spieler und KI.
"""

import random

from games.tetris.shapes import PIECE_TYPES, SHAPES

COLS = 10
ROWS = 20
CELL_PIXELS = 26

GRAVITY_START = 0.8
GRAVITY_MIN = 0.12
GRAVITY_STEP = 0.06
LINES_PER_LEVEL = 6

LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
GARBAGE_SENT = {1: 0, 2: 1, 3: 2, 4: 4}


class TetrisBoard:
    def __init__(self):
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.gravity_timer = 0.0
        self.pending_garbage = 0
        self.garbage_to_send = 0
        self.piece_id = 0
        self.piece_type = None
        self.rotation = 0
        self.piece_x = 0
        self.piece_y = 0
        self.next_type = random.choice(PIECE_TYPES)
        self._spawn_piece()

    def _spawn_piece(self):
        self.piece_id += 1
        self.piece_type = self.next_type
        self.next_type = random.choice(PIECE_TYPES)
        self.rotation = 0
        self.piece_x = COLS // 2 - 2
        self.piece_y = -2
        if not self.fits(self.piece_x, self.piece_y, self.rotation):
            self.game_over = True

    def piece_cells(self, rotation=None):
        states = SHAPES[self.piece_type]
        return states[(self.rotation if rotation is None else rotation) % len(states)]

    def fits(self, x, y, rotation):
        for cx, cy in self.piece_cells(rotation):
            gx, gy = x + cx, y + cy
            if gx < 0 or gx >= COLS or gy >= ROWS:
                return False
            if gy >= 0 and self.grid[gy][gx] is not None:
                return False
        return True

    def move(self, dx):
        if not self.game_over and self.fits(self.piece_x + dx, self.piece_y, self.rotation):
            self.piece_x += dx

    def rotate(self):
        if self.game_over:
            return
        new_rotation = self.rotation + 1
        if self.fits(self.piece_x, self.piece_y, new_rotation):
            self.rotation = new_rotation

    def soft_drop(self):
        if self.game_over:
            return False
        if self.fits(self.piece_x, self.piece_y + 1, self.rotation):
            self.piece_y += 1
            return True
        self._lock_piece()
        return False

    def hard_drop(self):
        if self.game_over:
            return
        while self.fits(self.piece_x, self.piece_y + 1, self.rotation):
            self.piece_y += 1
        self._lock_piece()

    def _lock_piece(self):
        for cx, cy in self.piece_cells():
            gx, gy = self.piece_x + cx, self.piece_y + cy
            if gy < 0:
                self.game_over = True
                return
            self.grid[gy][gx] = self.piece_type

        cleared = self._clear_lines()
        if cleared:
            self.score += LINE_SCORES.get(cleared, cleared * 200)
            self.lines_cleared += cleared
            self.level = 1 + self.lines_cleared // LINES_PER_LEVEL
            self.garbage_to_send = GARBAGE_SENT.get(cleared, 0)
        else:
            self.garbage_to_send = 0

        self._apply_pending_garbage()
        self._spawn_piece()

    def _clear_lines(self):
        remaining = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(remaining)
        self.grid = [[None] * COLS for _ in range(cleared)] + remaining
        return cleared

    def receive_garbage(self, count):
        self.pending_garbage += count

    def pop_garbage_to_send(self):
        amount = self.garbage_to_send
        self.garbage_to_send = 0
        return amount

    def _apply_pending_garbage(self):
        if self.pending_garbage <= 0:
            return
        for _ in range(self.pending_garbage):
            gap = random.randrange(COLS)
            garbage_row = ["garbage" if c != gap else None for c in range(COLS)]
            removed = self.grid.pop(0)
            if any(cell is not None for cell in removed):
                self.game_over = True
            self.grid.append(garbage_row)
        self.pending_garbage = 0

    def gravity_interval(self):
        return max(GRAVITY_MIN, GRAVITY_START - (self.level - 1) * GRAVITY_STEP)

    def update(self, dt):
        if self.game_over:
            return
        self.gravity_timer += dt
        if self.gravity_timer >= self.gravity_interval():
            self.gravity_timer = 0
            self.soft_drop()
