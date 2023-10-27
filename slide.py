import numpy as np
from point import Point
from bezier import Bezier
from conf import parameters, GRAPH_STEP


class Slide:
    def __init__(self, equation=None, points=[]) -> None:
        self.equation = equation
        self.points = np.array(points)*parameters['SCALE']/GRAPH_STEP
        self.is_pause = False
        self.selected = False
        self.init_curve()
        self.init_point()

    def init_curve(self):
        self.curve = Bezier(self.points)

    def init_point(self):
        self.point = Point(self.curve, self.curve.table)

    def move(self):
        self.point.move()

    def blit(self):
        self.curve.blit()
        self.point.blit()

    def handle_drag(self, event, pause, resume):
        return self.curve.handle_drag(event, pause, resume)

    def pause(self):
        if not self.is_pause:
            self.is_pause = True
            self.point.pause()

    def resume(self):
        if self.is_pause:
            self.is_pause = False
            self.point.resume()

    def reset(self):
        self.curve.redraw()
        self.point.reset()

    def set_selected(self):
        self.selected = True
        self.point.set_selected()
        self.curve.set_selected()

    def set_not_selected(self):
        self.selected = False
        self.point.set_not_selected()
        self.curve.set_not_selected()
