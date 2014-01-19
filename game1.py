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
hl/move should be in Board
"""

game_size = 5
tilesize  = 75

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
    def draw_r(self, loc):
        r = Rect(0,0, tilesize-40, tilesize-40, center=loc)
        # draw.rect(self.board.scr, (50,50,50), rect.inflate(-40,-40), 4)
        draw.rect(self.board.scr, (50,50,50), r, 4)

    def draw_o(self, loc):
        ts = self.board.tilesize
        # draw.circle(self.board.scr, (170,170,170), rect.center, ts/2-18, 0)
        # draw.circle(self.board.scr, (100,100,100), rect.center, ts/2-19, 0)
        draw.circle(self.board.scr, (70,70,70), loc, ts/2-20, 0)
        draw.circle(self.board.scr, white, loc, ts/2-25, 0)


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

    def make_move(self, player):
        if player == ai:
            self.ai_move(player)
        else:
            self.human_move(player)

    def ai_move(self, player):
        """Capture player piece if possible, otherwise move to a blank if possible, or try another piece."""
        shuffle(ai_pieces)
        for p in ai_pieces:
            nbrs   = board.neighbour_locs(p)
            pl     = [loc for loc in nbrs if same_side(board[loc], p1)]
            blanks = [loc for loc in nbrs if board[loc] and board[loc].blank]
            loc    = first(pl) or randchoice(blanks) if blanks else None
            if loc:
                p.move(loc)
                break

    def human_move(self, player):
        """ Select a piece and then move a highlighted piece.

            select logic:
             - only player's piece can be selected
             - click on a piece to select, click again to deselect
             - move if a piece is selected AND clicked on a valid location
             - if a piece is already selected and clicked on a new player's piece, the old one is
               deselected
        """
        hl_loc = None
        while True:
            loc = board.get_click_index()
            if same_side(board[loc], player):
                board.toggle_highlight(loc)

                if hl_loc and hl_loc != loc:
                    board.toggle_highlight(hl_loc)

                if hl_loc==loc : hl_loc = None
                else           : hl_loc = loc

            elif hl_loc and board.dist(loc, hl_loc) < 2:
                if not board[loc].none:
                    # capture piece or move to a blank tile
                    board.toggle_highlight(hl_loc)
                    board.move(hl_loc, loc)
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
