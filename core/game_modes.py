"""Gemeinsame Konstanten für Gegner-/Modus-Wahl, damit UI, StateMachine und Spiele
dasselbe Vokabular nutzen.

VS_AI/SOLO sind generisch für Spiele mit nur einer KI-Stufe (Panzer-Duell, Tetris);
AI_EASY..AI_DYNAMIC bleiben Pong-spezifisch (dort gibt es 4 Schwierigkeitsstufen).
"""

VS_PLAYER = "vs_player"
VS_AI = "vs_ai"
SOLO = "solo"

AI_EASY = "ai_easy"
AI_MEDIUM = "ai_medium"
AI_HARD = "ai_hard"
AI_DYNAMIC = "ai_dynamic"
