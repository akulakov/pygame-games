#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from itertools import cycle
from pygame import *

from board import PygameBoard, Loc
from utils import *

game_size = 5
tilesize  = 100
players   = u'X', u'○'
ai        = u'○'


class Game2Board(PygameBoard):
    pass

class Game2(object):
    winmsg  = "%s is the winner!"
    drawmsg = "It's a draw!"

    def check_end(self, player):
        if board.filled():
            self.game_won(None)

    def game_won(self, winner):
        board.message(self.winmsg % winner if winner else self.drawmsg)
        board.wait_exit()

    def run(self):
        """Main loop."""
        for player in cycle(players):
            move = self.get_move(player)
            board[move] = player
            self.check_end(player)

    def ai_move(self, player):
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
    if arg:
        game_size = int(arg[0])
    board = Game2Board((game_size, game_size), tilesize)
    Game2().run()
