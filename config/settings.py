"""Zentrale Konfiguration: Bildschirm, Eingaben, NFC, Pfade."""

import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
FULLSCREEN = False  # Für den fertigen Automaten auf True stellen
FPS = 60

PAUSE_KEY = pygame.K_z

# Tastenbelegung der 4 Arcade-Tasten (Pygame-Konstanten oder GPIO-Pin-Nummern)
BUTTON_MAPPING = {
    "A": None,
    "B": None,
    "X": None,
    "Y": None,
}

JOYSTICK_ID = 0

# NFC-Lesegerät
NFC_PORT = "/dev/ttyUSB0"
NFC_POLL_INTERVAL_SEC = 0.5

STATUE_REGISTRY_PATH = "nfc_mapping/statue_registry.json"
PLAYER_PROFILES_PATH = "players/profiles.json"
