"""Tetris-KI: bewertet für jeden neuen Stein alle Rotationen/Spalten mit einer
Heuristik (Höhe, Löcher, Unebenheit, geräumte Reihen) und steuert dann Schritt für
Schritt auf die beste gefundene Position zu.

Kein Ausblick auf den nächsten Stein, nur der aktuelle - reicht aber für eine
ordentliche, schlagbare KI. Nutzt nicht ai/ai_base.py, weil das auf Pongs
Ball-Tracking zugeschnitten ist; hier ist der Aktionsraum (Stein drehen/verschieben)
ein anderer.
"""

from games.tetris.board import COLS, ROWS
from games.tetris.shapes import SHAPES

HEIGHT_WEIGHT = -0.51
HOLES_WEIGHT = -0.76
BUMPINESS_WEIGHT = -0.18
LINES_WEIGHT = 0.76

MOVE_INTERVAL = 0.06  # Sekunden zwischen einzelnen KI-Zügen


class TetrisAI:
    def __init__(self):
        self._known_piece_id = -1
        self._target_rotation = 0
        self._target_x = 0
        self._timer = 0.0

    def control(self, board, dt):
        if board is None or board.game_over:
            return

        if board.piece_id != self._known_piece_id:
            self._known_piece_id = board.piece_id
            self._target_rotation, self._target_x = self._choose_target(board)

        self._timer -= dt
        if self._timer > 0:
            return
        self._timer = MOVE_INTERVAL

        if board.rotation != self._target_rotation:
            board.rotate()
        elif board.piece_x < self._target_x:
            board.move(1)
        elif board.piece_x > self._target_x:
            board.move(-1)
        else:
            board.soft_drop()

    def _choose_target(self, board):
        best_score = None
        best = (board.rotation, board.piece_x)
        rotation_count = len(SHAPES[board.piece_type])

        for rotation in range(rotation_count):
            for x in range(-2, COLS + 2):
                if not board.fits(x, 0, rotation):
                    continue
                landing_y = self._simulate_drop(board, x, rotation)
                grid_after = self._place(board, x, landing_y, rotation)
                score = self._evaluate(grid_after)
                if best_score is None or score > best_score:
                    best_score = score
                    best = (rotation, x)

        return best

    def _simulate_drop(self, board, x, rotation):
        y = 0
        while board.fits(x, y + 1, rotation):
            y += 1
        return y

    def _place(self, board, x, y, rotation):
        grid = [row[:] for row in board.grid]
        for cx, cy in SHAPES[board.piece_type][rotation]:
            gx, gy = x + cx, y + cy
            if 0 <= gy < ROWS and 0 <= gx < COLS:
                grid[gy][gx] = board.piece_type
        return grid

    def _evaluate(self, grid):
        heights = self._column_heights(grid)
        aggregate_height = sum(heights)
        holes = self._count_holes(grid, heights)
        bumpiness = sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))
        lines_cleared = sum(1 for row in grid if all(cell is not None for cell in row))

        return (
            HEIGHT_WEIGHT * aggregate_height
            + HOLES_WEIGHT * holes
            + BUMPINESS_WEIGHT * bumpiness
            + LINES_WEIGHT * lines_cleared
        )

    def _column_heights(self, grid):
        heights = []
        for col in range(COLS):
            height = 0
            for row in range(ROWS):
                if grid[row][col] is not None:
                    height = ROWS - row
                    break
            heights.append(height)
        return heights

    def _count_holes(self, grid, heights):
        holes = 0
        for col in range(COLS):
            top_row = ROWS - heights[col]
            for row in range(top_row + 1, ROWS):
                if grid[row][col] is None:
                    holes += 1
        return holes
