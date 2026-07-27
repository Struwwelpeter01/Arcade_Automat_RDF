"""Panzer-KI: bewegt sich auf den Spieler zu, weicht Mauern grob aus und schießt,
sobald eine freie Schusslinie (Reihe/Spalte ohne Mauer dazwischen) besteht.

Kein A*-Pfadfinding, nur ein einfacher Achsen-Heuristik-Ansatz - reicht für die
handgebaute, recht offene Arena aber aus und bleibt dadurch nachvollziehbar/schlagbar.
Nutzt nicht ai/ai_base.py, weil das auf Pongs Ball-Tracking zugeschnitten ist -
hier ist der Aktionsraum (Richtung/Schuss in einer Arena mit Mauern) ein anderer.

decide_action gibt zurück:
- eine Richtung (UP/DOWN/LEFT/RIGHT): dorthin bewegen (und hinschauen)
- ("aim", Richtung): den Panzer erst in diese Richtung drehen, dann schießen -
  wichtig, weil "schießen" sonst in die zuletzt bewegte (evtl. falsche) Richtung
  gefeuert hätte, ohne den Panzer vorher auf das Ziel auszurichten
- None: nichts tun
"""

import random

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"
_DIRECTIONS = (UP, DOWN, LEFT, RIGHT)
_DELTAS = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}


class TankAI:
    def __init__(self):
        self._wander_direction = random.choice(_DIRECTIONS)
        self._wander_timer = 0.0

    def decide_action(self, state):
        fire_direction = self._line_of_fire_direction(state)
        if fire_direction is not None:
            return ("aim", fire_direction)

        self_rect = state["self_rect"]
        target_rect = state["target_rect"]
        cell = state["cell_size"]
        dx = target_rect.centerx - self_rect.centerx
        dy = target_rect.centery - self_rect.centery

        if abs(dx) > cell and self._cell_free(state, RIGHT if dx > 0 else LEFT):
            return RIGHT if dx > 0 else LEFT
        if abs(dy) > cell and self._cell_free(state, DOWN if dy > 0 else UP):
            return DOWN if dy > 0 else UP

        return self._wander(state)

    def _line_of_fire_direction(self, state):
        self_rect = state["self_rect"]
        target_rect = state["target_rect"]
        cell = state["cell_size"]
        wall_cells = state["wall_cells"]

        same_row = abs(self_rect.centery - target_rect.centery) < cell
        same_col = abs(self_rect.centerx - target_rect.centerx) < cell

        col_a, row_a = self_rect.centerx // cell, self_rect.centery // cell
        col_b, row_b = target_rect.centerx // cell, target_rect.centery // cell

        if same_row and col_a != col_b:
            step = 1 if col_b > col_a else -1
            if all((c, row_a) not in wall_cells for c in range(col_a, col_b, step)):
                return RIGHT if col_b > col_a else LEFT

        if same_col and row_a != row_b:
            step = 1 if row_b > row_a else -1
            if all((col_a, r) not in wall_cells for r in range(row_a, row_b, step)):
                return DOWN if row_b > row_a else UP

        return None

    def _cell_free(self, state, direction):
        cell = state["cell_size"]
        col = state["self_rect"].centerx // cell
        row = state["self_rect"].centery // cell
        dx, dy = _DELTAS[direction]
        target = (col + dx, row + dy)
        in_bounds = 0 <= target[0] < state["cols"] and 0 <= target[1] < state["rows"]
        return in_bounds and target not in state["wall_cells"]

    def _wander(self, state):
        self._wander_timer -= state["dt"]
        if self._wander_timer <= 0 or not self._cell_free(state, self._wander_direction):
            self._wander_direction = random.choice(_DIRECTIONS)
            self._wander_timer = random.uniform(0.5, 1.5)
        return self._wander_direction
