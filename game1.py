#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from random import choice as randchoice
from itertools import cycle
from pygame import *
from pygame import gfxdraw

from board import PygameBoard, Loc, black, white, gray
from utils import *

"""
which version to use?
hl/move should be in Board ?
"""

game_size = 5
tilesize  = 75

def same_side(p1, p2):
    return p1 and p2 and p1.char==p2.char


class BaseTile(object):
    highlight = False
    piece     = None

    def __init__(self, board=None, loc=None, none=False):
        self.board = board
        self.loc   = loc
        self.none  = none   # unmovable-to tile, should not be drawn
        # if self.board and self.loc:
            # self.place()

    def set_none(self):
        self.none = True
        if self.board:
            self.board.make_blank(self.loc)

    @property
    def blank(self):
        return not self.piece and not self.none


class BasePiece(object):
    def __init__(self, char, board=None, loc=None):
        self.char = char
        self.board = board
        self.loc   = loc
        # super(BasePiece, self).__init__(board, loc)
        self.none = False
        if self.board and self.loc:
            self.place()

    def __repr__(self):
        return self.char

    def draw(self):
        """Draw piece."""
        getattr(self, "draw_"+self.char)(self.loc)
        display.update()

    def move(self, loc):
        self.board.move(self.loc, loc)

    def place(self):
        self.board[self.loc].piece = self
        self.draw()


class Piece(BasePiece):
    def draw_r(self, loc):
        B = self.board
        r = Rect(0, 0, tilesize-40, tilesize-40)
        loc = B.tile_locs[loc.y][loc.x]
        print("loc", loc)
        r.center = loc
        draw.rect(B.sfc, (50,50,50), r, 1)
        draw.rect(B.sfc, gray, r.inflate(-4,-4), 0)
        B.scr.blit(B.sfc, (0,0))

    def draw_o(self, loc):
        B = self.board
        loc = B.tile_locs[loc.y][loc.x]
        gfxdraw.filled_circle(B.sfc, loc[0], loc[1], B.tilesize/2-22, (120,120,120))
        gfxdraw.aacircle(B.sfc, loc[0], loc[1], B.tilesize/2-20, black)
        B.scr.blit(B.sfc, (0,0))


class GameBoard(PygameBoard):
    def move(self, loc1, loc2):
        p1 = self[loc1].piece
        p2 = self[loc2].piece
        if p1 == p2: return     # can't capture own piece
        if p2 in ai_pieces:
            ai_pieces.remove(p2)
        elif p2 in player_pieces:
            player_pieces.remove(p2)
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
            print("ai_pieces", ai_pieces)
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
            pl     = [loc for loc in nbrs if same_side(board[loc].piece, p1)]
            blanks = [loc for loc in nbrs if board[loc].blank]
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
            if same_side(board[loc].piece, player):
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
    imax = game_size - 1
    for loc in [(0,0), (0,imax), (imax,0), (imax,imax)]:
        board[loc].set_none()
    p1, ai        = Piece('r'), Piece('o')
    players       = p1, ai
    ai_pieces     = [Piece(ai.char, board, board.random_blank()) for _ in range(2)]
    player_pieces = [Piece(p1.char, board, board.random_blank()) for _ in range(2)]
    Game1().run()
