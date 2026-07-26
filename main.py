"""Einstiegspunkt des Arcade-Automaten: startet Menü und Haupt-Loop."""

from core.state_machine import StateMachine


def main():
    machine = StateMachine()
    machine.run()


if __name__ == "__main__":
    main()
