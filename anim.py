from pyray import *
from settings import *
from enum import IntEnum


class AnimationType(IntEnum):
    REPEATING = 1
    ONESHOT = 2

class Direction(IntEnum):
    LEFT = -1
    RIGHT = 1

class Animation:
    def __init__(self, first, last, cur, step, duration, duration_left, anim_type, row, sprites_in_row, tilesize):
        self.first = first
        self.last = last
        self.cur = cur
        self.step = step
        self.duration = duration
        self.duration_left = duration_left
        self.type = anim_type
        self.row = row
        self.sprites_in_row = sprites_in_row 
        self.done = False
        self.tilesize = tilesize

    def update(self, dt):
        self.duration_left -= dt
        
        if (self.duration_left<=0):
            # print(self.cur, self.type)
            self.duration_left = self.duration
            self.cur += self.step

            if (self.cur > self.last):
                match(self.type):
                    case AnimationType.ONESHOT:
                        self.cur = self.last 
                        self.done = True
                    case AnimationType.REPEATING:
                        self.cur = self.first 

    
    def frame(self, row, y_offset):  
        x = (self.cur % self.sprites_in_row) * self.tilesize
        y =  self.tilesize * row + y_offset

        return Rectangle(x, y, self.tilesize, self.tilesize)

    def reset(self, anim_type=None):
        self.cur = self.first
        self.duration_left = self.duration
        self.done = False

        if anim_type is not None:
            self.type = anim_type