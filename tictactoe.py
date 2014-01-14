#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from random import choice as randchoice
from itertools import cycle
from pygame import *

from board import PygameBoard, Loc
from utils import *

game_size = 5
tilesize  = 100
players   = u'X', u'○'
ai        = u'○'


class TictactoeBoard(PygameBoard):
    def completed(self, line, player):
        """Entire `line` completed by `player`."""
        return all(self[loc] == player for loc in line)

    def win_moves(self, player):
        """Yield all win moves for `player`."""
        for line in self.win_lines:
            n = sum(self[loc] == player for loc in line)
            blank = [loc for loc in line if not self[loc]]
            if len(blank) == 1 and n == game_size-1:
                yield blank[0]

    def make_win_lines(self):
        """Create a list of winning lines."""
        winlines, diag1, diag2 = [], [], []
        size = game_size

        for n in range(size):
            winlines.append( [Loc(m, n) for m in range(size)] )
            winlines.append( [Loc(n, m) for m in range(size)] )

            diag1.append(Loc(n, n))
            diag2.append(Loc(size-n-1, n))

        self.win_lines = winlines + [diag1, diag2]


class Tictactoe(object):
    winmsg  = "%s is the winner!"
    drawmsg = "It's a draw!"

    def check_end(self, player):
        """Check if `player` has won the game; check for a draw."""
        for line in board.win_lines:
            if board.completed(line, player):
                self.game_won(player)

        if board.filled(): self.game_won(None)

    def game_won(self, winner):
        board.message(self.winmsg % winner if winner else self.drawmsg)
        board.wait_exit()

    def run(self):
        """Main loop."""
        board.make_win_lines()

        for player in cycle(players):
            move = self.get_move(player)
            board[move] = player
            self.check_end(player)

    def ai_move(self, player):
        win_moves = list(board.win_moves(player))
        if win_moves:
            return first(win_moves)
        else:
            return board.random_blank()

    def get_move(self, player):
        if player == ai:
            return self.ai_move(player)
        else:
            while True:
                loc = board.get_click_index()
                if not board[loc]:
                    return loc


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg: game_size = int(arg[0])
    board = TictactoeBoard((game_size, game_size))
    Tictactoe().run()
