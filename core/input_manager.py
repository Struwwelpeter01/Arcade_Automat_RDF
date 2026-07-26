"""Kapselt Joystick + 4 Tasten, damit Spiele nicht direkt gegen pygame/GPIO programmieren."""


class InputManager:
    def __init__(self):
        self.direction = (0, 0)
        self.buttons_pressed = set()

    def poll(self):
        """Muss pro Frame aufgerufen werden, um Joystick-/Tasten-Zustand zu aktualisieren."""
        raise NotImplementedError

    def is_button_pressed(self, name):
        return name in self.buttons_pressed
