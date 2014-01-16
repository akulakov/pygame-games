# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import sys
import math
from time import sleep
from random import choice as randchoice

import pygame
from pygame import *

from utils import ujoin, range1, enumerate1, first, nl, space, iround

red        = (255,0,0)
green      = (0,255,0)
blue       = (0,0,255)
dark_blue  = (0,0,128)
light_blue = (150,150,250)
white      = (255,255,255)
gray       = (170,170,170)
black      = (0,0,0)
pink       = (255,200,200)

def pploc(loc):
    return loc.x+1, loc.y+1


class BaseTile(object):
    """ Base tile that sets a convenience attribute according to the name of the class, e.g. Blank
        will have tile.blank=True set automatically.
    """
    def __init__(self, loc=None):
        self.loc = loc
        setattr(self, self.__class__.__name__.lower(), True)


class Loc(object):
    """ Location on game board; note that we should not modify the location in place to avoid many
        hard to track errors; `moved()` creates and returns a new instance.
    """
    def __init__(self, x, y):
        self.loc = x, y
        self.x, self.y = x, y

    def __repr__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)

    def __eq__(self, other):
        return self.loc == getattr(other, "loc", None)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.loc)

    def moved(self, x, y):
        """ Return a new Loc moved according to delta modifiers `x` and `y`,
            e.g. 1,0 to move right.
        """
        return Loc(self.x + x, self.y + y)

Dir = Loc   # Directions (e.g. 0,1=right) work the same way but should have a different name for clarity

class BaseBoard(object):
    """ Base Board for regular and stackable boards.

        TODO: add various scrolling and visual area options.
    """
    stackable         = False
    board_initialized = False

    def __init__(self, size, num_grid=False, padding=(0, 0), pause_time=0.2, screen_sep=5):
        if isinstance(size, int):
            size = size, size   # handle square board

        self.width, self.height = size

        self.num_grid    = num_grid
        self.xpad        = padding[0]
        self.ypad        = padding[1]
        self.pause_time  = pause_time
        self.screen_sep  = screen_sep
        self.init_tiles  = False

        self.tiletpl     = "%%%ds" % (padding[0] + 1)
        self.directions()

    def __iter__(self):
        return ( self[Loc(x, y)] for y in range(self.height) for x in range(self.width) )

    def tiles(self, *attrs):
        return [ t for t in self if all(getattr(t, attr) for attr in attrs) ]

    def tiles_not(self, *attrs):
        return [ t for t in self if all(not getattr(t, attr) for attr in attrs) ]

    def locations(self, *attrs):
        locs = (Loc(x, y) for y in range(self.height) for x in range(self.width))
        return [ l for l in locs if all(getattr(self[l], attr) for attr in attrs) ]

    def locations_not(self, *attrs):
        locs = (Loc(x, y) for y in range(self.height) for x in range(self.width))
        return [ l for l in locs if all(not getattr(self[l], attr) for attr in attrs) ]

    def ploc(self, tile_loc):
        """Parse location out of tile-or-loc `tile_loc`."""
        # print("tile_loc", tile_loc)
        if isinstance(tile_loc, Loc) : return tile_loc
        else                         : return tile_loc.loc

    def draw(self, pause=None):
        pause = pause or self.pause_time
        print(nl * self.screen_sep)

        if self.num_grid:
            print(space, space*(self.xpad + 1), ujoin( range1(self.width), space, self.tiletpl ), nl * self.ypad)

        for n, row in enumerate1(self.board):
            args = [self.tiletpl % n] if self.num_grid else []
            if self.stackable:
                row = (tile[-1] for tile in row)
            args = [space] + args + [ujoin(row, space, self.tiletpl), nl * self.ypad]
            print(*args)

        self.status()
        sleep(pause)

    def status(self):
        pass

    def valid(self, loc):
        return bool( loc.x >= 0 and loc.y >= 0 and loc.x <= self.width-1 and loc.y <= self.height-1 )

    def directions(self):
        """Create list and dict of eight directions, going from up clockwise."""
        dirs          = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        self.dirlist  = [Dir(*d) for d in (dirs[0], dirs[2], dirs[4], dirs[6])]
        self.dirlist2 = [Dir(*d) for d in dirs]
        self.dirnames = dict(zip(self.dirlist2, "up ru right rd down ld left lu".split()))

    def neighbour_locs(self, tile_loc):
        """Return the list of neighbour locations of `tile`."""
        x, y = self.ploc(tile_loc)
        coords = (-1,0,1)
        locs = set((x+n, y+m) for n in coords for m in coords) - set( [(x,y)] )
        locs = [ Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) ]
        return [loc for loc in locs if self[loc] is not None]

    def neighbours(self, tile_loc):
        """Return the list of neighbours of `tile`."""
        return [self[loc] for loc in self.neighbour_locs(tile_loc)]

    def neighbour_cross_locs(self, tile_loc):
        """Return a generator of neighbour 'cross' (i.e. no diagonal) locations of `tile`."""
        x, y = self.ploc(tile_loc)
        locs = ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
        locs = [ Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) ]
        return [loc for loc in locs if self[loc] is not None]

    def cross_neighbours(self, tile_loc):
        """Return the generator of 'cross' (i.e. no diagonal) neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_cross_locs(tile_loc))

    def make_tile(self, loc):
        """Make a tile using `self.def_tile`. If def_tile is simply a string, return it, otherwise instantiate with x, y as arguments."""
        tile = self.def_tile
        return tile if self._def_tile_str or tile is None else tile(loc)

    def move(self, tile_loc, newloc):
        loc          = self.ploc(tile_loc)
        item         = self[loc]
        self[newloc] = item
        self[loc]    = self.make_tile(loc)

        if hasattr(item, "loc"):
            item.loc = newloc

    def nextloc(self, tile_loc, dir, n=1, wrap=False):
        """Return location next to `tile_loc` point in direction `dir`."""
        loc = self.ploc(tile_loc)

        x   = loc.x + dir.x*n
        y   = loc.y + dir.y*n

        if wrap:
            while not self.valid(Loc(x,y)):
                if x > (self.width - 1)  : x -= self.width
                elif x < 0               : x += self.width

                if y > (self.height - 1) : y -= self.height
                elif y < 0               : y += self.height

        loc = Loc(x, y)
        return loc if self.valid(loc) else None

    def next_tile(self, tile_loc, dir, n=1):
        loc = self.nextloc(tile_loc, dir, n)
        return self[loc] if loc else None

    def dist(self, tile_loc1, tile_loc2):
        l1, l2 = self.ploc(tile_loc1), self.ploc(tile_loc2)
        return math.sqrt( abs(l2.x - l1.x)**2 + abs(l2.y - l1.y)**2  )

    def ray(self, tile, dir, n=0):
        """ Generate a 'ray' of tiles from `tile` start in `dir` direction for `n` tiles; if n is
            0, to the end of board, excluding `start`.
        """
        while True:
            tile = self.next_tile(tile, dir)
            if tile   : yield tile
            else      : break
            if n == 1 : break
            if n: n -= 1

    def reset(self):
        self.board_initialized = False
        self.init_board()


class Board(BaseBoard):
    def __init__(self, size, def_tile, **kwargs):
        super(Board, self).__init__(size, **kwargs)

        try              : self._def_tile_str = isinstance(def_tile, basestring)
        except NameError : self._def_tile_str = isinstance(def_tile, str)

        self.def_tile = def_tile
        xrng, yrng    = range(self.width), range(self.height)
        self.board    = [ [None for x in xrng] for y in yrng ]

    def __getitem__(self, loc):
        self.init_board()
        return self.board[loc.y][loc.x]

    def __setitem__(self, tile_loc, item):
        self.init_board()
        loc = self.ploc(tile_loc)
        self.board[loc.y][loc.x] = item

    def __delitem__(self, tile_loc):
        loc = self.ploc(tile_loc)
        self.board[loc.y][loc.x] = self.make_tile(loc)

    def empty(self, tile_loc):
        loc = self.ploc(tile_loc)
        if self._def_tile_str:
            return bool(self[loc] == self.def_tile)
        else:
            return isinstance(self[loc], self.def_tile)

    def init_board(self):
        """ To allow tiles that place themselves on the board, board is first initialized with None values in __init__,
            then on the first __setitem__ or __getitem__, init_board() runs; self.board_initialized needs to be set
            immediately to avoid recursion.
        """
        if not self.board_initialized:
            self.board_initialized = True
            xrng, yrng = range(self.width), range(self.height)
            self.board = [ [self.make_tile(Loc(x, y)) for x in xrng] for y in yrng ]


class StackableBoard(BaseBoard):
    stackable = True

    def __init__(self, size, def_tile, **kwargs):
        super(StackableBoard, self).__init__(size, **kwargs)

        try              : self._def_tile_str = isinstance(def_tile, basestring)
        except NameError : self._def_tile_str = isinstance(def_tile, str)

        self.def_tile = def_tile
        xrng, yrng    = range(self.width), range(self.height)
        self.board    = [ [[None] for x in xrng] for y in yrng ]

    def __getitem__(self, loc):
        self.init_board()
        return self.board[loc.y][loc.x][-1]

    def __setitem__(self, tile_loc, item):
        self.init_board()
        loc = self.ploc(tile_loc)
        self.board[loc.y][loc.x].append(item)

    def __delitem__(self, tile_loc):
        loc = self.ploc(tile_loc)
        del self.board[loc.y][loc.x][-1]

    def empty(self, tile_loc):
        return len( self.items(self.ploc(tile_loc)) ) == 1

    def init_board(self):
        if not self.board_initialized:
            self.board_initialized = True
            xrng, yrng = range(self.width), range(self.height)
            self.board = [ [ [self.make_tile( Loc(x, y) )] for x in xrng] for y in yrng ]

    def items(self, tile_loc):
        loc = self.ploc(tile_loc)
        return self.board[loc.y][loc.x]

    def get_instance(self, cls, tile_loc, default=None):
        """Get first instance of `cls` from `tile_loc` location."""
        return first([i for i in self.items(tile_loc) if isinstance(i, cls)], default)

    def move(self, tile_loc, newloc):
        item = self[tile_loc] if isinstance(tile_loc, Loc) else tile_loc

        loc = self.ploc(tile_loc)
        self[newloc] = item
        self.items(loc).remove(item)

        if hasattr(item, "loc"):
            item.loc = newloc


class PygameBoard(Board):
    def __init__(self, size, tilesize=100, message_font=None, glyph_font=None, margin=50, circle=False, tile_cls=None):
        Board.__init__(self, size, tile_cls)
        from pygame import font, display
        font.init()
        message_font      = message_font or (None, 60)
        glyph_font        = glyph_font or (None, 70)
        self.message_font = font.Font(message_font[0], message_font[1])
        self.glyph_font   = font.Font(glyph_font[0], glyph_font[1])
        n                 = tilesize + 1
        self.margin       = margin
        self.scr          = display.set_mode((size[0]*n + margin*2, size[1]*n + margin*2))

        self.scr.fill(white)
        self.tilesize  = tilesize
        self.circle    = circle
        self.tile_locs = [[ (iround(margin+x+tilesize/2) , iround(margin+y+tilesize/2))
                              for x in range(0, size[0]*n, n)]
                              for y in range(0, size[1]*n, n)]
        self.gui_tiles = [[self.mkgui_tile(x, y, tilesize, tilesize)
                              for x in range(0, size[0]*n, n)]
                              for y in range(0, size[1]*n, n)]
        display.flip()

    def mkgui_tile(self, x, y, width, height):
        ts = self.tilesize
        m = self.margin
        if self.circle:
            c = draw.circle(self.scr, white, (iround(m+x+ts/2), iround(m+y+ts/2)), iround(ts/2-5), 0)
            return draw.circle(self.scr, black, (iround(m+x+ts/2), iround(m+y+ts/2)), iround(ts/2-5), 1)
        else:
            draw.rect(self.scr, white, (x + m, y + m, width, height), 0)
            return draw.rect(self.scr, black, (x + m, y + m, width, height), 1)

    def test_unicode(self):
        t = u"""
             ▣ ▲ ▷ ◇ ◉ ◎ ●  ☀  ★  ☘  ☺  ☼
        """.replace('\t', ' '*2).split('\n')
        self.message(t[1], (300,100))
        self.message(t[2], (300,200))

    def __contains__(self, loc):
        return loc.y < len(self.gui_tiles) and loc.x < len(self.gui_tiles[0])

    def __setitem__(self, loc, piece):
        super(PygameBoard, self).__setitem__(loc, piece)
        if piece:
            rect = self.gui_tiles[loc.y][loc.x]
            if isinstance(piece, (str, unicode)):
                self.draw_glyph(piece, rect.center)
            else:
                piece.draw(rect)
            display.update()

    def move(self, loc1, loc2):
        # print("loc1", pploc(loc1))
        # print("loc2", pploc(loc2))
        # print("self[loc1]", self[loc1])
        # print("self[loc2]", self[loc2])
        self[loc2] = self[loc1]
        self[loc2].highlight = False
        self[loc2].loc = loc2
        self.clear(loc1)

    def is_highlighted(self, loc):
        return self[loc].highlight

    def toggle_highlight(self, loc):
        if self[loc]:
            r     = self.gui_tiles[loc.y][loc.x]
            ts    = self.tilesize
            color = white if self[loc].highlight else light_blue
            x, y = r.topleft
            draw.rect(self.scr, color, (x+1, y+1, ts-2, ts-2), 3)
            self[loc].highlight = not self[loc].highlight
            display.update()

    def clear(self, loc):
        x, y      = loc
        ts        = self.tilesize
        r         = self.gui_tiles[y][x]
        self[loc] = ''
        # self.mkgui_tile(r.topleft[0], r.topleft[1], ts, ts)
        draw.rect(self.scr, white, (r.topleft[0], r.topleft[1], ts, ts), 0)
        draw.rect(self.scr, black, (r.topleft[0], r.topleft[1], ts, ts), 1)
        display.update()

    def wait_exit(self):
        while True:
            ev = event.wait()
            if ev.type == QUIT or ev.type == MOUSEBUTTONDOWN or ev.type == KEYDOWN:
                sys.exit()

    def get_click_index(self):
        """Get location of clicked tile."""
        while True:
            ev = event.wait()
            if ev.type == QUIT:
                sys.exit(); pygame.quit()
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                sys.exit(); pygame.quit()
            if ev.type == MOUSEBUTTONDOWN:
                n = self.tilesize + 1
                m = self.margin
                loc = Loc(int((ev.pos[0]-m) / n), int((ev.pos[1]-m) / n))
                if loc in self:
                    return loc

    def draw_glyph(self, char, center, color=(0,0,0), bgcolor=(255,255,255)):
        """UNUSED, Draw glyph `char` at `loc`."""
        char = self.glyph_font.render(unicode(char), 1, color, bgcolor)
        rect = char.get_rect()
        rect.center = center
        display.update(self.scr.blit(char, rect))

    def message(self, txt, center=None, color=None, bgcolor=None, border=None, border_size=4, board_center=True):
        """Display message on screen."""
        color   = color or (0,0,0)
        bgcolor = bgcolor or (235,235,235)
        border  = border or (100,100,100)
        txt     = self.message_font.render(txt, 1, color, bgcolor)
        rect    = txt.get_rect()

        if board_center and not center:
            i = display.Info()
            center = i.current_w / 2, i.current_h / 2
        rect.center = center

        border_size += 8
        draw.rect(self.scr, bgcolor, rect.inflate(border_size, border_size))
        # print("rect", rect)
        draw.rect(self.scr, border, rect.inflate(border_size, border_size))
        # print("rect", rect)
        display.update()
        display.update(self.scr.blit(txt, rect))

    def filled(self):
        return not any(tile is None for tile in self)

    def random_blank(self):
        locs = [loc for loc in self.locations() if self[loc] and self[loc].blank]
        return randchoice(locs) if locs else None
