#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from random import choice as randchoice
from itertools import cycle
from pygame import *

from board import PygameBoard, Loc, black, white
from utils import *

game_size = 5
tilesize  = 100

def same_side(p1, p2):
    return p1 and p2 and p1.char==p2.char

class Piece(object):
    def __init__(self, char, board=None, loc=None):
        self.board     = board
        self.loc       = loc
        self.char      = char
        self.highlight = False
        if self.board and self.loc:
            self.place()

    def __repr__(self):
        return self.char

    # def __eq__(self, other):
        # return other and self.char == other.char

    def place(self):
        self.board[self.loc] = self

    def draw(self, rect):
        """Draw piece in `rect`."""
        getattr(self, "draw_"+self.char)(rect)

    def draw_r(self, rect):
        draw.rect(self.board.scr, black, rect.inflate(-20,-20), 4)

    def draw_o(self, rect):
        ts = self.board.tilesize
        draw.circle(self.board.scr, black, rect.center, ts/2-5, 0)
        draw.circle(self.board.scr, white, rect.center, ts/2-10, 0)

    def move(self, loc):
        self.board.move(self.loc, loc)


class GameBoard(PygameBoard):
    def move(self, loc1, loc2):
        t1 = self[loc1]
        t2 = self[loc2]
        if t1 == t2: return     # can't capture own piece
        if t2 in ai_pieces:
            ai_pieces.remove(t2)
        elif t2 in player_pieces:
            player_pieces.remove(t2)
        self.clear(loc2)
        super(GameBoard, self).move(loc1, loc2)


class Game1(object):
    winmsg  = "%s is the winner!"
    drawmsg = "It's a draw!"

    def game_won(self, winner):
        board.message(self.winmsg % winner if winner else self.drawmsg)
        board.wait_exit()

    def run(self):
        """Main loop."""
        for player in cycle(players):
            self.make_move(player)
            if not ai_pieces:
                self.game_won(p1.char)
            if not player_pieces:
                self.game_won(ai.char)

    def ai_move(self, player):
        if ai_pieces:
            p    = randchoice(ai_pieces)
            nbrs = board.neighbour_locs(p)
            pl   = [loc for loc in nbrs if same_side(board[loc], p1)]
            loc  = first(pl) or randchoice(nbrs)
            p.move(loc)

    def make_move(self, player):
        if player == ai:
            self.ai_move(player)
        else:
            self.human_move(player)

    def human_move(self, player):
        hl_loc = None
        while True:
            loc = board.get_click_index()
            if same_side(board[loc], player):
                board.toggle_highlight(loc)
                hl_loc = None if hl_loc else loc

            elif hl_loc and board.dist(loc, hl_loc) < 2:
                board.move(hl_loc, loc)
                board.toggle_highlight(hl_loc)
                break


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg: game_size = int(arg[0])

    board         = GameBoard((game_size, game_size), tilesize)
    p1, ai        = Piece('r'), Piece('o')
    players       = p1, ai
    ai_pieces     = [Piece(ai.char, board, board.random_blank()) for _ in range(3)]
    player_pieces = [Piece(p1.char, board, board.random_blank()) for _ in range(3)]
    Game1().run()
