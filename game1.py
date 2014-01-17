#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from random import choice as randchoice
from itertools import cycle
from pygame import *

from board import PygameBoard, Loc, black, white, gray
from utils import *

"""
which version to use?
ai move to blank tile only
ai go to next piece if nowhere to move for current
fix 'capture piece'
"""

game_size = 5
tilesize  = 100

def same_side(p1, p2):
    return p1 and p2 and p1.char==p2.char


class BaseTile(object):
    blank     = True
    highlight = False
    char      = None
    tile      = True

    def __init__(self, board=None, loc=None, none=True):
        self.board = board
        self.loc   = loc
        self.none  = none   # unmovable-to tile, should not be drawn
        if self.board and self.loc:
            self.place()

    def set_none(self):
        self.none = True
        self.blank = False
        if self.board:
            self.board.make_blank(self.loc)

    def place(self):
        self.board[self.loc] = self


class BasePiece(BaseTile):
    blank = False
    tile  = False

    def __init__(self, char, board=None, loc=None):
        self.char = char
        super(BasePiece, self).__init__(board, loc)
        self.none = False

    def __repr__(self):
        return self.char

    def draw(self, rect):
        """Draw piece in `rect`."""
        getattr(self, "draw_"+self.char)(rect)

    def move(self, loc):
        self.board.move(self.loc, loc)


class Piece(BasePiece):
    def draw_r(self, rect):
        draw.rect(self.board.scr, (50,50,50), rect.inflate(-40,-40), 4)

    def draw_o(self, rect):
        ts = self.board.tilesize
        # draw.circle(self.board.scr, (170,170,170), rect.center, ts/2-18, 0)
        # draw.circle(self.board.scr, (100,100,100), rect.center, ts/2-19, 0)
        draw.circle(self.board.scr, (70,70,70), rect.center, ts/2-20, 0)
        draw.circle(self.board.scr, white, rect.center, ts/2-25, 0)


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
        shuffle(ai_pieces)
        for p in ai_pieces:
            nbrs   = board.neighbour_locs(p)
            pl     = [loc for loc in nbrs if same_side(board[loc], p1)]
            blanks = [loc for loc in nbrs if board[loc] and board[loc].blank]
            print("blanks", blanks)
            loc    = first(pl) or randchoice(blanks) if blanks else None
            print("loc", loc)
            if loc:
                p.move(loc)
                break

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
                if hl_loc:
                    board.toggle_highlight(hl_loc)
                if hl_loc != loc:
                    board.toggle_highlight(loc)
                hl_loc = loc

            elif hl_loc and board.dist(loc, hl_loc) < 2:
                if not board[loc].none:
                    board.move(hl_loc, loc)
                    board.toggle_highlight(hl_loc)
                    break


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg: game_size = int(arg[0])

    board = GameBoard((game_size, game_size), tilesize, circle=0, tile_cls=BaseTile)
    for tile in board:
        tile.none = False  # make all tiles active

    imax = game_size - 1
    for loc in [(0,0), (0,imax), (imax,0), (imax,imax)]:
        board[loc].set_none()
    p1, ai        = Piece('r'), Piece('o')
    players       = p1, ai
    ai_pieces     = [Piece(ai.char, board, board.random_blank()) for _ in range(3)]
    player_pieces = [Piece(p1.char, board, board.random_blank()) for _ in range(3)]
    Game1().run()
