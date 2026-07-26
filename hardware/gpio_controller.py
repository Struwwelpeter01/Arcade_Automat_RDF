"""GPIO-Ansteuerung, falls Joystick/Tasten direkt am Raspberry Pi hängen (statt per USB)."""


class GPIOController:
    def __init__(self, pin_mapping):
        self.pin_mapping = pin_mapping

    def setup(self):
        raise NotImplementedError

    def read_states(self):
        raise NotImplementedError
