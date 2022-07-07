from math import floor
from re import T
import pygame
from draggable_point import DraggablePoint
from conf import *

class Slider:
    def __init__(self, name, pos, size, min_value, max_value, init_value, callback) -> None:
        self.name = name
        self.pos = pos
        self.size = size
        self.min_v = min_value
        self.max_v = max_value
        self.v = init_value
        self.callback = callback
        self.init_surface()
        self.init_drag_point()
    
    def init_surface(self):
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()
        self.rectangle = self.surface.get_rect().move(self.pos)
        self.start = np.array((0, self.size[1]/2))
        self.end = np.array((self.size[0], self.size[1]/2))
        text = my_font15.render(self.name, True, BLACK)
        self.surface.blit(text, (0, -4))
        pygame.draw.line(self.surface, BLACK, self.start, self.end, 3)
        n = 10
        for i in range(0, n):
            xy = self.start + (self.end - self.start)*(i/10) + 5

            start = xy + np.array([0, -5])
            end = xy + np.array([0, 5])
            pygame.draw.line(self.surface, BLACK, start, end, 1)

            y_axis = (self.min_v + i * (self.max_v - self.min_v)/n)
            if (abs(y_axis) < 1): text = "{:.1f}".format(y_axis)
            else: text = f"{floor(y_axis)}"
            text = my_font10.render(text, True, BLACK)
            self.surface.blit(text, xy + np.array([-text.get_width()/2, 5]))


    def init_drag_point(self):
        self.xy = np.array((self.value_to_screen(self.v), self.size[1]/2))
        self.screen_xy = self.rectangle.move(self.xy)
        self.drag = DraggablePoint(screen_to_coord(self.screen_xy) + np.array([5, 0]), 0, 0, 0)
        self.drag.set_constraints(self.pos[0], self.pos[0] + self.size[0],
                                  self.pos[1], self.pos[1] + self.size[1])

    def value_to_screen(self, value):
        return self.size[0] * (value - self.min_v) / (self.max_v - self.min_v)
    
    def screen_to_value(self, screen_x):
        return self.min_v + (screen_x - self.pos[0])  * (self.max_v - self.min_v)/ self.size[0]

    def blit(self):
        screen.blit(self.surface, self.rectangle)
        self.drag.blit()
    
    def reset(self, quick=False):
        self.screen_xy = self.drag.screen_xy
        self.screen_xy[1] = self.pos[1] + self.size[1]/2
        self.v = self.screen_to_value(self.screen_xy[0])
        self.callback(self.v)

    def handle_drag(self, event, pause, resume):
        return self.drag.handle_drag(event, pause, resume, self.reset)