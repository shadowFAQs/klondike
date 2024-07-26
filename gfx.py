import pygame as pg

from logic import Card, Game, Pile
from pathlib import Path


# Colors from here: https://github.com/dracula/dracula-theme
BACKGROUND  = pg.Color('#282a36')
SELECTION   = pg.Color('#44475a')
FOREGROUND  = pg.Color('#f8f8f2')
COMMENT     = pg.Color('#6272a4')
CYAN        = pg.Color('#8be9fd')
GREEN       = pg.Color('#50fa7b')
ORANGE      = pg.Color('#ffb86c')
RED         = pg.Color('#ff5555')
YELLOW      = pg.Color('#f1fa8c')
TRANSPARENT = pg.Color('#ff00ff')

# Borders and anchor points
PADDING      = 6
GAP          = 5
STACK_HEIGHT = 9
FACE_DOWN_HT = 4
CARD_DIMS    = pg.Vector2(27, 35)
LIBRARY      = pg.Vector2(PADDING, PADDING + 2)
GRAVEYARD    = pg.Vector2(PADDING + CARD_DIMS.x + GAP, PADDING + 2)
GAME_LABEL   = pg.Vector2(73, 14)
FOUNDATION_1 = pg.Vector2(PADDING + (CARD_DIMS.x + GAP) * 3, PADDING + 2)
FOUNDATION_LABEL = pg.Vector2(149, 3)
TABLEAU_1    = LIBRARY + (0, CARD_DIMS.y + PADDING)

# Images
assets = Path('assets')
CARD_IMG          = pg.image.load(assets / 'card.bmp')
CARD_BACK_IMG     = pg.image.load(assets / 'card_back.bmp')
LABEL_LIBRARY     = pg.image.load(assets / 'label_library.bmp')
LABEL_GRAVEYARD   = pg.image.load(assets / 'label_graveyard.bmp')
LABEL_FOUNDATIONS = pg.image.load(assets / 'label_foundations.bmp')
NEXT_GAME         = pg.image.load(assets / 'next_game.bmp')
NEXT_GAME_SEL     = pg.image.load(assets / 'next_game_selected.bmp')
START_OVER        = pg.image.load(assets / 'start_over.bmp')
START_OVER_SEL    = pg.image.load(assets / 'start_over_selected.bmp')
BROKE             = pg.image.load(assets / 'broke.bmp')
WINNER            = pg.image.load(assets / 'winner.bmp')
KEEP_PLAYING      = pg.image.load(assets / 'keep_playing.bmp')
KEEP_PLAYING_SEL  = pg.image.load(assets / 'keep_playing_selected.bmp')
GAME              = pg.image.load(assets / 'game.bmp')
TEXT              = {}
CARD_IMG.set_colorkey(pg.Color('#ff00ff'))
CARD_BACK_IMG.set_colorkey(pg.Color('#ff00ff'))
LABEL_LIBRARY.set_colorkey(pg.Color('#ff00ff'))
LABEL_GRAVEYARD.set_colorkey(pg.Color('#ff00ff'))
LABEL_FOUNDATIONS.set_colorkey(pg.Color('#ff00ff'))


def draw(screen: pg.Surface, game: Game, version_info: str):
    screen.fill(BACKGROUND)

    draw_board(screen)
    draw_games_played(screen, game.games)
    draw_version_number(screen, version_info)

    for pile in game.piles:
        if pile.empty_focused:  # Draw focus box on empty pile
            base_coord = LIBRARY if game.focus_coords.y == 0 else TABLEAU_1
            box_coords = base_coord + \
                ((CARD_DIMS.x + GAP) * game.focus_coords.x, 0)
            draw_focus_box(screen, RED, box_coords, True)
            break

    if game.library.get_top_card():
        draw_card(screen, game.library.get_top_card(), LIBRARY, False, False)

    if game.graveyard.get_top_card():
        draw_card(screen, game.graveyard.get_top_card(), GRAVEYARD,
            game.graveyard.get_top_card().selected, True)

    draw_foundations(screen, game.foundations)

    draw_tableau_piles(screen, game.tableau, game.selected_card_pile,
                       game.selected_stack_offset)

    draw_labels(screen, game.focus_coords)

    draw_library_count(screen, game.library)

    game.update_money_displayed()
    draw_money(screen, game.money_displayed)

    if game.menu:
        draw_menu(screen, game.win, game.game_over, game.menu_index)


def draw_board(screen: pg.Surface):
    draw_card_slot(screen, LIBRARY)
    draw_card_slot(screen, GRAVEYARD)
    for n in range(4):
        draw_card_slot(screen, get_foundation_coords(n))
    for n in range(7):
        draw_card_slot(screen, TABLEAU_1 + ((CARD_DIMS.x + GAP) * n, 0))


def draw_card(screen: pg.Surface, card: Card, coords: pg.Vector2,
              highlight: bool, draw_selection_top: bool):
    rendered = render_card(card, highlight, draw_selection_top)
    screen.blit(rendered, coords)


def draw_card_slot(surface: pg.Surface, coords: pg.Vector2):
    topleft = coords
    topright = coords + (CARD_DIMS.x, 0)
    bottomright = topright + (0, CARD_DIMS.y)
    bottomleft = topleft + (0, CARD_DIMS.y)

    pg.draw.line(surface, SELECTION, topleft, topright)
    pg.draw.line(surface, SELECTION, topright, bottomright)
    pg.draw.line(surface, SELECTION, bottomright, bottomleft)
    pg.draw.line(surface, SELECTION, bottomleft, topleft)


def draw_focus_box(surface: pg.Surface, color: pg.Color,
                   offset: tuple[int] = (0, 0), complete: bool = True):
    topleft     = pg.Vector2(0, 0) + offset
    topright    = pg.Vector2(CARD_DIMS.x, 0) + offset
    bottomleft  = pg.Vector2(0, CARD_DIMS.y) + offset
    bottomright = CARD_DIMS + offset

    if complete:
        pg.draw.line(surface, color, topleft + (1, 0), topright + (-1, 0))

    pg.draw.line(surface, color, topright + (0, 1), bottomright + (0, -1))
    pg.draw.line(surface, color, bottomright + (-1, 0), bottomleft + (1, 0))
    pg.draw.line(surface, color, bottomleft + (0, -1), topleft + (0, 1))


def draw_foundations(screen: pg.Surface, foundations: list[Pile]):
    for n in range(len(foundations)):
        if foundations[n]:
            draw_card(screen, foundations[n].get_top_card(),
                      get_foundation_coords(n),
                      foundations[n].get_top_card().selected, True)


def draw_games_played(screen: pg.Surface, games: int):
    screen.blit(GAME, GAME_LABEL)
    games_played = '%0*d' % (2, games)  # <- Zero-padding
    game_count = pg.Surface((10, 6))
    game_count.fill(BACKGROUND)
    for n, char in enumerate(games_played):
        game_count.blit(TEXT['money'][char]['pos'], (n * 5, 0))
    screen.blit(game_count, GAME_LABEL + (7, 12))


def draw_labels(screen: pg.Surface, coords: pg.Vector2):
    if coords.y == 0:
        match coords.x:
            case 0:
                screen.blit(LABEL_LIBRARY, LIBRARY + (2, -5))
            case 1:
                screen.blit(LABEL_GRAVEYARD, GRAVEYARD + (-1, -5))
            case _:
                screen.blit(LABEL_FOUNDATIONS, FOUNDATION_LABEL)


def draw_library_count(screen: pg.Surface, library: Pile):
    if library:
        count = str(len(library))
        count_bg = pg.Surface((12, 9))
        count_bg.fill(COMMENT)
        screen.blit(count_bg, LIBRARY + (5, 10))
        count_image = count_bg.copy()
        count_image.fill(FOREGROUND)
        count_image.set_colorkey(FOREGROUND)
        right_align = 7 if len(count) == 1 else 1
        for n in range(len(count)):
            count_image.blit(TEXT[count[n]]['black'], (5 * n + right_align, 1))

        screen.blit(count_image, LIBRARY + (5, 10))


def draw_menu(screen: pg.Surface, win: bool, game_over: bool, menu_index: int):
    if game_over or win:
        menu = pg.Surface((84, 51))  # <- 3-line menu
    else:
        menu = pg.Surface((84, 38))  # <- 2-line menu

    menu.fill(COMMENT)
    pg.draw.rect(menu, BACKGROUND, pg.Rect(0, 0, menu.get_width(),
                                           menu.get_height()), 1)
    pg.draw.rect(menu, SELECTION, pg.Rect(2, 2, menu.get_width() - 4,
                                          menu.get_height() - 4), 1)

    if win:
        menu.blit(WINNER, (24, 8))
        if menu_index:
            menu.blit(NEXT_GAME, (5, 22))
            menu.blit(START_OVER_SEL, (14, 35))
        else:
            menu.blit(NEXT_GAME_SEL, (5, 22))
            menu.blit(START_OVER, (15, 35))
    elif game_over:
        menu.blit(BROKE, (26, 8))
        if menu_index:
            menu.blit(KEEP_PLAYING, (11, 22))
            menu.blit(START_OVER_SEL, (15, 35))
        else:
            menu.blit(KEEP_PLAYING_SEL, (11, 22))
            menu.blit(START_OVER, (15, 35))
    else:
        if menu_index == 0:
            menu.blit(NEXT_GAME_SEL, (5, 9))
            menu.blit(START_OVER, (14, 22))
        else:
            menu.blit(NEXT_GAME, (5, 9))
            menu.blit(START_OVER_SEL, (14, 22))

    screen.blit(menu, (78, 61))


def draw_money(screen: pg.Surface, money: int):
    chars = f'g{money}'

    for n, char in enumerate(chars[::-1]):
        if char.isdigit():
            screen.blit(TEXT['money'][char]['neg' if money < 0 else 'pos'],
                        (233 - 5 * n, 1))
        else:
            screen.blit(TEXT['money'][char], (233 - 5 * n, 1))


def draw_tableau_piles(screen: pg.Surface, tableau: list[Pile],
                       selected_pile: Pile, offset: int):
    for i, pile in enumerate(tableau):
        total_height = 0

        if offset and pile == selected_pile:
            highlighted_cards = pile[offset - 1:]
        else:
            highlighted_cards = []

        for j, card in enumerate(pile):
            if j > 0:
                if pile[j - 1].is_face_up:
                    total_height += STACK_HEIGHT
                else:
                    total_height += FACE_DOWN_HT

            if card in highlighted_cards:
                draw_card(screen, card,
                      TABLEAU_1 + ((CARD_DIMS.x + GAP) * i, total_height),
                      highlight=True,
                      draw_selection_top=card == highlighted_cards[0])
            else:
                draw_card(screen, card,
                          TABLEAU_1 + ((CARD_DIMS.x + GAP) * i, total_height),
                          highlight=card.selected, draw_selection_top=True)


def draw_version_number(screen: pg.Surface, version_info: str):
    for n, char in enumerate(f'v{version_info}'):
        screen.blit(TEXT['version'][char], (n * 5 + 208, 151))


def get_foundation_coords(n: int) -> pg.Vector2:
    return FOUNDATION_1 + ((CARD_DIMS.x + GAP) * n, 0)


def load_card_text():
    global TEXT

    font = pg.image.load(assets / 'font.bmp')
    text = {}

    for n in range(0, 14):
        if n == 0:
            set_character_image(text, '0', 0, font)
        elif n == 1:
            set_character_image(text, 'A', -78, font)
            set_character_image(text, '1', -6, font)
        elif n == 10:  # Special double-width surface for "10"
            temp_r = pg.Surface((10, 7))
            temp_r.blit(font, (-6, 0))
            temp_r.blit(font, (4, 0))
            text['10'] = {'red': temp_r}
            temp_b = pg.Surface((10, 7))
            temp_b.blit(font, (-6, -7))
            temp_b.blit(font, (4, -7))
            text['10']['black'] = temp_b
        else:
            match n:
                case 11:
                    set_character_image(text, 'J', -60, font)
                case 12:
                    set_character_image(text, 'Q', -66, font)
                case 13:
                    set_character_image(text, 'K', -72, font)
                case _:
                    set_character_image(text, str(n), n * -6, font)

    for n, suit in enumerate(['hearts', 'clubs', 'diamonds', 'spades']):
        suit_surface = pg.Surface((7, 7))
        suit_surface.fill(FOREGROUND)
        suit_surface.blit(font, (n * -8, -14))
        text[suit] = suit_surface

    text['money'] = {}
    temp_m = pg.Surface((4, 6))
    for n in range(11):
        temp_neg = temp_m.copy()
        temp_pos = temp_m.copy()
        temp_pos.blit(font, (n * -4, -21))
        temp_neg.blit(font, (n * -4, -27))

        if n == 10:
            text['money']['-'] = temp_neg
            text['money']['g'] = temp_pos
        else:
            text['money'][str(n)] = {'neg': temp_neg, 'pos': temp_pos}

    text['version'] = {}
    temp_v = pg.Surface((4, 6))
    for n in range(12):
        temp = temp_v.copy()
        if n == 10:
            temp.blit(font, (-40, -33))
            text['version']['v'] = temp
        elif n == 11:
            temp.blit(font, (-44, -33))
            text['version']['.'] = temp
        else:
            temp.blit(font, (n * -4, -33))
            text['version'][str(n)] = temp

    TEXT = text


def render_card(card: Card, highlight: bool,
                draw_selection_top: bool) -> pg.Surface:
    surface = CARD_IMG.copy() if card.is_face_up else CARD_BACK_IMG.copy()

    if highlight:
        draw_focus_box(surface, GREEN, complete=draw_selection_top)
    elif card.focused:
        draw_focus_box(surface, ORANGE, complete=True)

    if card.is_face_up:
        rank_target = (2, 2)
        suit_target = (13, 2) if card.rank == 10 else (8, 2)
        surface.blit(TEXT[str(card.display_rank)][card.color], rank_target)
        surface.blit(TEXT[card.suit], suit_target)

    return surface


def set_character_image(text: dict, rank: str, x_offset: int, font: pg.Surface):
    colors = ['red', 'black']
    y_offsets = [0, -7]
    text[rank] = {'red': None, 'black': None}

    for n in range(2):
        surf = pg.Surface((5, 7))
        surf.blit(font, (x_offset, y_offsets[n]))
        text[rank][colors[n]] = surf
