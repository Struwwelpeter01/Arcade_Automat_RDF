"""Tetromino-Formen: pro Typ nur die Basis-Form hinterlegt, die restlichen Rotationen
werden per 90°-Drehung innerhalb der quadratischen Bounding-Box berechnet (statt vier
Zustände von Hand zu pflegen und dabei Tippfehler zu riskieren)."""

PIECE_TYPES = ["I", "O", "T", "S", "Z", "J", "L"]

# Name -> (Bounding-Box-Größe, Zellen der Grundform)
_BASE_SHAPES = {
    "I": (4, [(0, 1), (1, 1), (2, 1), (3, 1)]),
    "O": (2, [(0, 0), (1, 0), (0, 1), (1, 1)]),
    "T": (3, [(1, 0), (0, 1), (1, 1), (2, 1)]),
    "S": (3, [(1, 0), (2, 0), (0, 1), (1, 1)]),
    "Z": (3, [(0, 0), (1, 0), (1, 1), (2, 1)]),
    "J": (3, [(0, 0), (0, 1), (1, 1), (2, 1)]),
    "L": (3, [(2, 0), (0, 1), (1, 1), (2, 1)]),
}

COLORS = {
    "I": (80, 200, 220),
    "O": (230, 210, 60),
    "T": (170, 90, 200),
    "S": (100, 200, 100),
    "Z": (220, 90, 90),
    "J": (90, 110, 220),
    "L": (230, 150, 70),
}


def _rotate(cells, size):
    return [(size - 1 - y, x) for x, y in cells]


def _build_rotation_states():
    states = {}
    for name, (size, cells) in _BASE_SHAPES.items():
        rotations = []
        seen = set()
        current = cells
        for _ in range(4):
            key = frozenset(current)
            if key not in seen:
                rotations.append(current)
                seen.add(key)
            current = _rotate(current, size)
        states[name] = rotations
    return states


SHAPES = _build_rotation_states()
