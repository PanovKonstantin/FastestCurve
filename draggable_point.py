import pygame
import numpy as np
import conf


class DraggablePoint:
    def __init__(self, xy, min_x, max_y, position=conf.GRAPH_POSITION) -> None:
        self.xy = xy
        self.min_x = min_x
        self.max_y = max_y
        self.is_dragging = False
        self.position = position
        self.screen_xy = conf.coord_to_screen(self.xy, self.min_x, self.max_y)
        self.init_surface()
        self.update_screen()

    def init_surface(self):
        self.surface = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()
        pygame.draw.circle(self.surface, (0, 0, 255), (5, 5), 5)

    def update_screen(self):
        self.offset = np.array((-5, -5)) + self.position + self.screen_xy
        self.rectangle = self.surface.get_rect().move(self.offset)

    def is_start_drag_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        if event.button != 1:
            return False
        return self.rectangle.collidepoint(event.pos)

    def is_stop_drag_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP:
            return False
        if event.button != 1:
            return False
        return self.is_dragging

    def set_constraints(self, minx, maxx, miny, maxy):
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def is_drag_event(self, event):
        if event.type != pygame.MOUSEMOTION:
            return False
        if not self.is_dragging:
            return False
        xy = event.pos
        if xy[0] < self.minx:
            return False
        if xy[0] > self.maxx:
            return False
        if xy[1] < self.miny:
            return False
        if xy[1] > self.maxy:
            return False
        return True

    def handle_drag(self, event, pause, resume, redraw):
        if self.is_start_drag_event(event):
            pause()
            self.is_dragging = True
            mouse_xy = np.array((event.pos))
            self.mouse_offect = self.screen_xy - mouse_xy
        elif self.is_drag_event(event):
            mouse_xy = np.array((event.pos))
            self.screen_xy = mouse_xy + self.mouse_offect
            self.xy = conf.screen_to_coord(
                self.screen_xy, self.min_x, self.max_y)
            redraw(True)
            self.update_screen()
        elif self.is_stop_drag_event(event):
            redraw()
            resume()
            self.is_dragging = False
            self.mouse_offect = None

    def blit(self):
        conf.screen.blit(self.surface, self.rectangle)
