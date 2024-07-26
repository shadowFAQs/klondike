import pygame as pg

import gfx

from gamepad import Gamepad
from logic import Game


VERSION = '1.0.0'


def main():
    screen_dims = (240, 160)
    screen = pg.display.set_mode(screen_dims, pg.SCALED)
    clock = pg.time.Clock()
    gfx.load_card_text()

    game = Game()
    gamepad = Gamepad()

    while game.running:
        clock.tick(30)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.quit()
            elif event.type == pg.JOYBUTTONDOWN:
                gamepad.handle_button_press(event.button)
            elif event.type == pg.JOYHATMOTION:  # <- DPAD buttons
                if event.value != (0, 0):  # <- Ignore DPAD "release" events
                    gamepad.handle_dpad_press(event.value)
            elif event.type == pg.JOYAXISMOTION:
                gamepad.handle_joyaxis(event.axis, event.value)

        pressed = gamepad.get_button_press()
        if pressed:
            game.handle_button_press(pressed)

        gfx.draw(screen, game, VERSION)
        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('GBA Klondike')
    main()
