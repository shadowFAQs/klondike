from random import sample
from typing import Iterator, Optional

import pygame as pg


class Card():
    def __init__(self, suit: str, rank: int):
        self.suit = suit
        self.rank = rank
        self.color = 'red' if self.suit in ['hearts', 'diamonds'] else 'black'
        self.is_face_up = False
        self.display_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                             'J', 'Q', 'K'][self.rank - 1]
        self.focused = False
        self.selected = False

    def __repr__(self) -> str:
        return f'{self.display_rank}{self.suit[0]}'

    def deselect(self):
        self.selected = False

    def flip(self):
        self.is_face_up = not self.is_face_up

    def focus(self):
        self.focused = True

    def reset(self):
        self.focused = False
        self.selected = False
        self.is_face_up = False

    def select(self):
        self.selected = True

    def unfocus(self):
        self.focused = False


class Pile():
    def __init__(self, name: str):
        self.name = name

        self.cards = []
        self.empty_focused = False
        self.has_focus = False  # <- Set during initial "get focus" event

    def __bool__(self) -> bool:
        return bool(self.cards)

    def __getitem__(self, index: int) -> Card:
        return self.cards[index]

    def __iter__(self) -> Iterator:
        return iter(self.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def __repr__(self) -> str:
        return f'{self.name} ({len(self.cards)} cards): {self.cards}'

    def draw(self) -> Card | None:
        if self.cards:
            return self.cards.pop()
        else:
            return None

    def focus(self, stack_offset: int = 0) -> Card|None:
        if self.get_type() == 'tableau':
            if self.cards:
                self.empty_focused = False

                if not self.has_focus:
                    self.has_focus = True

                focused_index = len(self.cards) - 1 + stack_offset
                focused_card = self.cards[focused_index]
                focused_card.focus()
                return focused_card
            else:
                self.empty_focused = True
                return None
        else:
            if self.cards:
                focused_card = self.get_top_card()
                focused_card.focus()
                return focused_card
            else:
                self.empty_focused = True
                return None

    def get_card_with_offset(self, offset: int) -> Card|None:
        try:
            return self.cards[len(self.cards) - 1 + offset]
        except IndexError:
            return None

    def get_type(self) -> str:
        return self.name.split(' ')[0].lower()

    def get_top_card(self) -> Card|None:
        try:
            return self.cards[-1]
        except IndexError:
            return None

    def place(self, card: Card):
        self.cards.append(card)

    def pop(self, index: int = -1) -> Card:
        return self.cards.pop(index)

    def shuffle(self):
        self.cards = sample(self.cards, k=len(self.cards))

    def unfocus(self, stack_offset: int):
        self.empty_focused = False
        self.has_focus = False

        focused_index = len(self.cards) - 1 + stack_offset
        if self.cards:
            self.cards[focused_index].unfocus()


class Game():
    def __init__(self):
        self.bank = 100
        self.face_down_cards = 0
        self.game_earnings = 0
        self.game_over = False
        self.games = 0
        self.menu = False
        self.menu_index = 0
        self.money = 0
        self.money_displayed = 100
        self.piles = []
        self.running = True
        self.selected_card = None
        self.selected_card_pile = None
        self.win = False

        self.new()

        self.focus_coords = pg.Vector2(0, 0)
        self.focus_areas = [
            [self.library, self.graveyard, None] + self.foundations,
             self.tableau
        ]
        self.focus_stack_offset = 0
        self.selected_stack_offset = 0

        self.move_focus(pg.Vector2(0, 0))

    def check_win(self):
        self.update_money()

        if self.face_down_cards == 0:
            if not self.win:
                self.win = True
                self.game_earnings = 5 * 52
                self.update_money()

            self.game_over = False
            self.menu = True
        else:
            if self.money <= 0 and self.menu:
                self.game_over = True
                self.win = False
            else:
                self.game_over = False

    def clear_stack_offsets(self):
        self.focus_stack_offset = 0
        self.selected_stack_offset = 0

    def deal(self):
        for i in range(7):
            for j in range(i, 7):
                self.tableau[j].place(self.library.draw())
                self.face_down_cards += 1

        for pile in self.tableau:
            pile.get_top_card().flip()
            self.face_down_cards -= 1

        self.update_money()
        self.games += 1

    def deselect(self):
        if self.selected_card:
            self.selected_card.deselect()
            self.selected_card = None

        self.selected_card_pile = None

    def draw(self):
        if self.library:  # <- Handle empty library
            self.graveyard.place(self.library.draw())
            self.graveyard.get_top_card().flip()
            self.set_focus(pg.Vector2(1, 0))
        else:
            if 0:  # TODO: Add this option in a menu?
                self.recycle_library()
                self.set_focus(pg.Vector2(0, 0))

        self.deselect()

    def flip_card_above_selected(self):
        revealed_card = self.selected_card_pile.get_top_card()
        if revealed_card:
            if not revealed_card.is_face_up:
                revealed_card.flip()
                self.face_down_cards -= 1

                self.check_win()

    def get_focused_pile(self) -> Pile:
        return self.focus_areas[
            int(self.focus_coords.y)][int(self.focus_coords.x)
        ]

    def get_foundation_cards(self) -> list[Card]:
        cards = []
        for pile in self.piles:
            if pile.get_type() == 'foundation':
                cards += pile.cards

        return cards

    def handle_button_press(self, pressed: str):
        match pressed:
            case 'A':
                self.press_A()
            case 'B':
                self.press_B()
            case 'X':
                self.press_X()
            case 'Y':
                pass
            case 'L2':
                self.press_L2()
            case 'R2':
                self.press_R2()
            case 'UP':
                self.press_UP()
            case 'DOWN':
                self.press_DOWN()
            case 'LEFT':
                self.press_LEFT()
            case 'RIGHT':
                self.press_RIGHT()
            case 'START':
                self.press_START()
            case _:
                print(f'Unhandled button press: {pressed}')

    def init_library(self):
        for suit in ['hearts', 'clubs', 'diamonds', 'spades']:
            for rank in range(1, 14):
                self.library.cards.append(Card(suit, rank))

    def is_legal_move(self, card: Card, target: Pile) -> bool:
        if target.get_type() == 'foundation':
            if self.selected_stack_offset:
                return False  # <- Can't move multiple cards to a foundation!
            if target.cards:
                top_card = target.get_top_card()
                if card.suit == top_card.suit and \
                    card.rank == top_card.rank + 1:
                    return True
            elif card.rank == 1:
                return True
        elif target.get_type() == 'tableau':
            if card.rank == 1:  # <- Can't put Aces on tableau piles
                return False

            top_card = target.get_top_card()
            if top_card:
                if top_card.color != card.color and \
                card.rank == top_card.rank - 1:
                    return True
            else:
                if card.rank == 13:  # <- King to empty tableau
                    return True

        return False

    def move_focus(self, direction: pg.Vector2):
        self.get_focused_pile().unfocus(self.focus_stack_offset)
        self.focused_card = None

        self.focus_coords += direction

        if self.focus_coords.x > len(self.focus_areas[0]) - 1:
            self.focus_coords.x = 0
        elif self.focus_coords.x < 0:
            self.focus_coords.x = len(self.focus_areas[0]) - 1

        if self.focus_coords.y < 0:  # TODO: Rewrite me as a clamp
            self.focus_coords.y = 1
        elif self.focus_coords.y > 1:
            self.focus_coords.y = 0

        if self.focus_coords == (2, 0):  # <- Spot b/w graveyard and foundations
            if direction.x == 1:
                self.focus_coords.x = 3
            elif direction.x == -1:
                self.focus_coords.x = 1
            else:
                self.focus_coords = pg.Vector2(1, 0)

        self.focus_stack_offset = 0
        self.update_focus()

    def move_selected_card(self, target_pile: Optional[Pile] = None):
        if target_pile is None:
            target_pile = self.get_focused_pile()

        target_pile.unfocus(self.focus_stack_offset)

        if self.selected_stack_offset:
            while self.selected_stack_offset < 0:
                target_pile.place(
                    self.selected_card_pile.pop(self.selected_stack_offset - 1))
                self.selected_stack_offset += 1

        target_pile.place(self.selected_card_pile.pop())
        self.selected_card_pile.unfocus(self.focus_stack_offset)
        self.clear_stack_offsets()
        self.update_focus()

        self.update_money()

    def new(self):
        self.library     = Pile('Library')
        self.graveyard   = Pile('Graveyard')
        self.tableau     = [Pile(f'Tableau {n}') for n in range(7)]
        self.foundations = [Pile(f'Foundation {n}') for n in range(4)]
        self.piles = [self.library, self.graveyard] + self.foundations \
                    + self.tableau

        self.init_library()
        self.library.shuffle()
        self.deal()

    def next_game(self):
        self.menu = False
        self.bank += self.game_earnings
        self.game_earnings = 0
        self.game_over = False
        self.win = False

        if self.focused_card:
            self.focused_card.unfocus()

        self.face_down_cards = 0
        self.focus_stack_offset = 0
        self.deselect()

        for pile in self.piles[1:]:  # <- Don't collect from library
            while pile.cards:
                card = pile.pop()
                card.reset()
                self.library.place(card)

        self.library.shuffle()
        self.deal()

        self.set_focus(pg.Vector2(0, 0))

    def offset_focus(self, offset: int):
        self.get_focused_pile().get_card_with_offset(
            self.focus_stack_offset).unfocus()
        self.focus_stack_offset += offset

    def press_A(self):
        if self.menu:
            if self.win:
                self.next_game()
                return
            elif self.game_over:
                if self.menu_index:
                    self.start_over()
                else:
                    self.menu = False
            else:
                if self.menu_index:
                    self.start_over()
                else:
                    self.next_game()
            return

        if self.selected_card:
            if self.selected_card == self.focused_card:
                self.deselect()
            else:
                if self.is_legal_move(self.selected_card,
                                      self.get_focused_pile()):
                    self.move_selected_card()
                    if self.selected_card_pile.get_type() == 'tableau':
                        self.flip_card_above_selected()  # <- Don't flip cards
                                                         #    in graveyard!
                self.deselect()
        else:
            if self.get_focused_pile() == self.library:
                self.draw()
            else:
                self.select(self.focused_card)

    def press_B(self):
        if self.menu:
            self.toggle_menu()
        else:
            self.deselect()
            self.update_focus()

    def press_DOWN(self):
        if self.menu:
            self.menu_index = int(not self.menu_index)
            return

        focused_pile = self.get_focused_pile()
        if focused_pile.cards and focused_pile.get_type() == 'tableau':
            if focused_pile == self.selected_card_pile:
                self.move_focus(pg.Vector2(0, 1))
                return

            if self.focus_stack_offset < 0:
                focused_pile.unfocus(self.focus_stack_offset)
                self.focus_stack_offset += 1
                self.update_focus()
            else:
                self.move_focus(pg.Vector2(0, 1))
        else:
            self.move_focus(pg.Vector2(0, 1))

    def press_L2(self):
        if not self.menu:
            self.draw()

    def press_LEFT(self):
        if not self.menu:
            self.move_focus(pg.Vector2(-1, 0))

    def press_R2(self):
        if not self.menu:
            self.shortcut_to_foundation()

    def press_RIGHT(self):
        if not self.menu:
            self.move_focus(pg.Vector2(1, 0))

    def press_START(self):
        self.toggle_menu()

    def press_UP(self):
        if self.menu:
            self.menu_index = int(not self.menu_index)
            return

        focused_pile = self.get_focused_pile()
        if focused_pile.cards and focused_pile.get_type() == 'tableau':
            if focused_pile == self.selected_card_pile:
                self.move_focus(pg.Vector2(0, -1))
                return

            if abs(self.focus_stack_offset) < len(focused_pile.cards) - 1:
                if focused_pile.get_card_with_offset(
                    self.focus_stack_offset - 1).is_face_up:
                    focused_pile.unfocus(self.focus_stack_offset)
                    self.offset_focus(-1)
                    self.update_focus()
                else:  # <- No more face-up cards above focused card
                    self.move_focus(pg.Vector2(0, -1))
            else:
                self.move_focus(pg.Vector2(0, -1))
        else:
            self.move_focus(pg.Vector2(0, -1))

    def press_X(self):
        self.deselect()

        pile = self.get_focused_pile()
        if pile.get_type() == 'tableau':
            if len(pile) == 1:
                self.select(pile)
            elif len(pile) > 1:
                self.clear_stack_offsets()
                self.offset_focus(
                    (len([c for c in pile if c.is_face_up]) - 1) * -1)
                self.update_focus()
                self.select(self.focused_card)

    def quit(self):
        self.running = False

    def recycle_library(self):
        """Not used in Vegas style Klondike"""
        while self.graveyard:
            card = self.graveyard.pop()
            card.flip()
            card.unfocus()
            self.library.place(card)

    def select(self, to_select: Card|Pile):
        if isinstance(to_select, Pile):
            to_select = to_select.get_top_card()

        if to_select:  # <- Handle empty tableau pile
            to_select.select()
            self.selected_card = to_select
            self.selected_card_pile = self.get_focused_pile()
            self.selected_stack_offset = self.focus_stack_offset

    def set_focus(self, coords: pg.Vector2):
        self.get_focused_pile().unfocus(self.focus_stack_offset)
        self.focus_coords = coords
        self.move_focus(pg.Vector2(0, 0))

    def shortcut_to_foundation(self):
        if self.focused_card:
            if self.focused_card.is_face_up:
                for foundation in self.foundations:
                    if self.is_legal_move(self.focused_card, foundation):
                        self.select(self.focused_card)
                        self.move_selected_card(foundation)
                        if self.selected_card_pile.get_type() == 'tableau':
                            self.flip_card_above_selected()

                        self.selected_card.unfocus()
                        self.deselect()
                        break

    def start_over(self):
        self.bank = 100
        self.money_displayed = 100
        self.games = 0
        self.game_earnings = 0
        self.next_game()

    def toggle_menu(self):
        self.menu_index = 0
        self.menu = not self.menu
        self.check_win()

    def update_focus(self):
        self.focused_card = self.get_focused_pile().focus(
            self.focus_stack_offset)

    def update_money(self):
        self.game_earnings = -52 + 5 * len(self.get_foundation_cards())
        self.money = self.bank + self.game_earnings

    def update_money_displayed(self):
        if self.money_displayed < self.money:
            self.money_displayed += 1
        elif self.money_displayed > self.money:
            self.money_displayed -= 1
