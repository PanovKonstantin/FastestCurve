import numpy as np
import pygame
from draggable_point import DraggablePoint
import point
import conf


class Bezier:
    def __init__(self, ctrl) -> None:
        self.ctrl = ctrl
        self.selected = False
        self.table = {}
        self.gen_table()
        self.init_surface()
        self.ctrl_drag = [DraggablePoint(
            xy * conf.GRAPH_STEP / conf.parameters['SCALE'], self.table['min_x'], self.table['max_y']) for xy in self.ctrl]
        for c in self.ctrl_drag:
            c.set_constraints(conf.GRAPH_POS_X,
                              conf.GRAPH_POS_X + conf.GRAPH_WIDTH_CONSTR - conf.GRAPH_STEP*2,
                              conf.GRAPH_POS_Y,
                              conf.GRAPH_POS_Y + conf.GRAPH_HEIGHT_CONSTR - conf.GRAPH_STEP*2)

    def gen_table(self):
        self.gen_ts()
        self.gen_xy()
        self.gen_path()
        self.gen_slope()

    def gen_ts(self, t=conf.T_NUM):
        self.table['ts'] = np.linspace(0, 1, t)

    def gen_xy(self):
        self.table['xy'] = []
        if len(self.ctrl) == 3:
            for t in self.table['ts']:
                a = self.intrplt(self.ctrl[0], self.ctrl[1], t)
                b = self.intrplt(self.ctrl[1], self.ctrl[2], t)
                self.table['xy'].append(self.intrplt(a, b, t))
        elif len(self.ctrl) == 4:
            for t in self.table['ts']:
                xy = pow((1 - t), 3) * self.ctrl[0]
                xy += 3 * pow(1 - t, 2) * t * (self.ctrl[1])
                xy += 3 * pow(t, 2) * (1 - t) * (self.ctrl[2])
                xy += pow(t, 3) * self.ctrl[3]
                self.table['xy'].append(xy)
        self.measure_szie()

    def gen_path(self):
        self.table['p'] = []
        self.table['p'].append(0)
        for i in range(1, len(self.table['xy'])):
            p1, p2 = self.table['xy'][i], self.table['xy'][i-1]
            diff_path = np.linalg.norm(p1 - p2)
            self.table['p'].append(self.table['p'][-1] + diff_path)

    def gen_slope(self):
        self.table['slope'] = []
        for i in range(0, len(self.table['xy']) - 1):
            xy1 = self.table['xy'][i]
            xy2 = self.table['xy'][i + 1]
            dx = (xy2[0] - xy1[0])
            dy = (xy2[1] - xy1[1])
            if dx == 0:
                dx = 0.00000001
            k = dy / dx
            theta = k / (np.sqrt(1 + k**2))
            if xy2[0] < xy1[0]:
                theta = -theta
            self.table['slope'].append(theta)
        self.table['slope'].append(self.table['slope'][-1])

    def redraw(self, quick=False):
        self.ctrl = [p.xy * conf.parameters['SCALE'] /
                     conf.GRAPH_STEP for p in self.ctrl_drag]
        if quick:
            self.gen_ts(100)
            self.gen_xy()
        else:
            self.gen_table()
        self.init_surface()

    def intrplt(self, a, b, t):
        return a + t*(b - a)

    def measure_szie(self):
        ys = [xy[1] for xy in self.table['xy']]
        self.table['min_x'] = 0
        self.table['max_y'] = conf.GRAPH_HEIGHT/2
        self.table['min_y'] = min(ys)

    def init_surface(self):
        self.surface = pygame.Surface(conf.GRAPH_SIZE, pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()
        if (len(self.table['xy']) >= 2):
            minx = self.table['min_x']
            maxy = self.table['max_y']
            xys = self.table['xy']
            line = [conf.coord_to_screen(
                xy * conf.GRAPH_STEP / conf.parameters['SCALE'], minx, maxy) for xy in xys]
            pygame.draw.aalines(self.surface, conf.BLACK, False, line)

    def handle_drag(self, event, pause, resume):
        for p in self.ctrl_drag:
            if p.handle_drag(event, pause, resume, self.redraw):
                return True
        return False

    def set_selected(self):
        self.selected = True

    def set_not_selected(self):
        self.selected = False

    def blit(self):
        conf.screen.blit(self.surface, conf.GRAPH_POSITION)
        if self.selected:
            for c in self.ctrl_drag:
                c.blit()
        else:
            self.ctrl_drag[0].blit()
            self.ctrl_drag[-1].blit()
