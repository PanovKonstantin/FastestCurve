from math import sqrt, cos, sin, log10, atan2, pi
import sys, pygame
from unittest.mock import DEFAULT
import numpy as np
SIZE = WIDTH, HEIGHT = 1280, 720
FPS = 60
WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GRAPH_SIZE = GRAPH_WIDTH, GRAPH_HEIGHT = 1280/2, 720
GRAPH_POSITION = GRAPH_POS_X, GRAPH_POS_Y = 50, 50
GRAPH_STEP = 25
GRAPH_COLOR = (100, 100, 100)
GRAPH_WIDTH_CONSTR = int(GRAPH_WIDTH) - (int(GRAPH_WIDTH) % GRAPH_STEP)
GRAPH_HEIGHT_CONSTR = int(GRAPH_HEIGHT) - (int(GRAPH_HEIGHT) % GRAPH_STEP)
VERTICAL_APPROX = 0.001
parameters = {}
parameters['G'] = 9.81
parameters['M'] = 1
parameters['MU'] = 0
parameters['SCALE'] = 1

PLOT_POSITION = PLOT_POS_X, PLOT_POS_Y = GRAPH_POS_X + GRAPH_WIDTH + 175, GRAPH_POS_Y
PLOT_SIZE = PLOT_WIDTH, PLOT_HEIGHT = 400, 75
PLOT_PADDING = 30
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 20)
my_font15 = pygame.font.SysFont('Comic Sans MS', 15)
my_font10 = pygame.font.SysFont('Comic Sans MS', 10)
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Brachistochrone simulation")

T_START = -3/2*pi + 0.1
T_FINISH = pi/2 + 0.1
T_NUM = 10000
POINT_R = 10
def curve(t):
    x = cos(t)
    y = sin(t)
    return np.array((x, y))

def coord_to_screen(xy, minx=0, maxy=0):
    x = xy[0] - minx
    y = -xy[1] + maxy
    return np.array([x, y])

def screen_to_coord(xy, minx=0, maxy=0):
    x = xy[0] + minx
    y = maxy - xy[1] 
    return np.array([x, y])

DEFAULT_POINTS3 = [(0, 200), (100, 0), (200, 200)]
DEFAULT_POINTS4 = [(0, 200), (50, 0), (0, 50), (200, 200)]