import pygame as pg

from pygame._sdl2 import controller


class Gamepad():
    def __init__(self):
        controller.init()
        self.controller = controller.Controller(0)

        self.button_press = None

    def get_button_press(self) -> str | None:
        button = self.button_press
        self.button_press = None

        return button

    def handle_button_press(self, button: int):
        match button:
            case 0:
                self.button_press = 'B'
            case 1:
                self.button_press = 'A'
            case 2:
                self.button_press = 'Y'
            case 3:
                self.button_press = 'X'
            case 4:  # <- L1 button (doubles L2)
                self.button_press = 'L2'
            case 5:  # <- R1 button (doubles R2)
                self.button_press = 'R2'
            case 7:
                self.button_press = 'START'
            case _:
                pass

    def handle_dpad_press(self, dpad_value: tuple[int]):
        match dpad_value:
            case (0, 1):
                self.button_press = 'UP'
            case (0, -1):
                self.button_press = 'DOWN'
            case (-1, 0):
                self.button_press = 'LEFT'
            case (1, 0):
                self.button_press = 'RIGHT'
            case _:
                pass

    def handle_joyaxis(self, axis: int, value: float):
        """
        L2 and R2 come across as JOYAXISMOTION
        events. When these buttons are pressed,
        an initial event with value ~= -1 is
        sent, then one with value == 1. Upon
        release, another ~-1 event is sent,
        so the positive 1.0 value events are the
        only ones we actually care about here.
        """
        if axis == 2:
            if int(value) == 1:
                self.button_press = 'L2'
        elif axis == 5:
            if int(value) == 1:
                self.button_press = 'R2'
