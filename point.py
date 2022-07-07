from math import sqrt, degrees
import time
import pygame
from conf import *

class Point:
    def __init__(self, curve, table) -> None:
        self.curve = curve
        self.table = table
        self.table_length = len(self.table['p'])
        self.is_pause = False
        self.selected = False
        self.reset()
        self.init_surface()

    def init_surface(self):
        color = RED if self.selected else (100, 100, 100)
        self.surface = pygame.Surface((POINT_R*2, POINT_R*2), pygame.SRCALPHA, 32)
        self.surface = self.surface.convert_alpha()
        pygame.draw.circle(self.surface, color, (POINT_R, POINT_R), POINT_R)
        self.set_rectangle()

    def reset(self):
        self.index = 0
        self.position = self.table['p'][0]
        self.velocity = 0
        self.start_energy = self.get_total()
        self.t = time.time()
        self.k = 0
        self.init_plots()
    
    def init_plots(self):
        pos = np.array(PLOT_POSITION)
        inc = np.array([0, PLOT_PADDING + PLOT_HEIGHT])
        self.acceleration_plot = PlotGraph([self.t, 0], pos, "Acceleration")
        self.velocity_plot = PlotGraph([self.t, 0], pos + inc, "Velocity")
        self.kinetic_energy_plot = PlotGraph([self.t, self.get_kintetic()], pos + inc*2, "Kinetic energy")
        self.potential_energy_plot = PlotGraph([self.t, self.get_potential()], pos + inc*3, "Potential energy")
        self.total_energy_plot = PlotGraph([self.t, self.get_total()], pos + inc*4, "Total energy")
        self.total_energy_loss_plot = PlotGraph([self.t, self.get_total_energy_loss()], pos + inc*5, "Total energy loss")

    def measure_time(self):
        t = time.time()
        self.time_diff = t-self.t
        self.t = t
    
    def find_next_position(self):
        step = 1 if self.position > self.get_pos() else -1
        while self.get_pos(step) * step <= self.position * step:
            self.index += step
            if (self.check_overflow_max()): break
            if (self.check_overflow_zero()): break

    def check_overflow_max(self):
        if self.index == self.table_length:
            self.index = self.table_length - 1
            self.position = self.table['p'][self.index]
            self.velocity = -self.velocity
            return True
        return False

    def check_overflow_zero(self):
        if self.index == -1:
            self.index = 0
            self.position = self.table['p'][0]
            self.velocity = -self.velocity
            return True
        return False

    def move(self):
        self.update_movement()
        self.find_next_position()
        self.set_rectangle()
        self.plot()
    
    def update_movement(self):
        self.measure_time()
        self.k = self.table['slope'][self.index]
        self.update_acceleration()
        self.update_velocity_with_acceleration()
        self.update_friction()
        # self.update_velocity_with_friction()
        self.position += self.velocity * self.time_diff
    
    def update_acceleration(self):
        self.acceleration = -parameters['G'] * self.k

    def update_velocity_with_acceleration(self):
        self.velocity += self.acceleration * self.time_diff

    def update_friction(self):
        k_sin = sqrt(1 - pow(self.k, 2))
        Fn =  parameters['M'] * parameters['G'] * k_sin
        self.friction = parameters['MU'] * Fn
    
    def update_velocity_with_friction(self):
        if self.friction * self.time_diff > abs(self.velocity): 
            self.velocity = 0
        elif self.velocity > 0: 
            self.velocity -= self.friction * self.time_diff
        else: 
            self.velocity += self.friction * self.time_diff

    def set_rectangle(self):
        self.rectangle = self.surface.get_rect()
        self.rectangle = self.rectangle.move(-POINT_R, -POINT_R)
        self.rectangle = self.rectangle.move(GRAPH_POSITION)
        xy = self.get_xy() * GRAPH_STEP / parameters['SCALE']
        xy = coord_to_screen(xy, self.table['min_x'], self.table['max_y'])
        self.rectangle = self.rectangle.move(xy)
    
    def plot(self):
        self.acceleration_plot.plot([self.t, self.acceleration])
        self.velocity_plot.plot([self.t, self.velocity])
        self.kinetic_energy_plot.plot([self.t, self.get_kintetic()])
        self.potential_energy_plot.plot([self.t, self.get_potential()])
        self.total_energy_plot.plot([self.t, self.get_total()])
        self.total_energy_loss_plot.plot([self.t, self.get_total_energy_loss()])

    def blit(self):
        screen.blit(self.surface, self.rectangle)
        if self.selected:
            self.acceleration_plot.blit()
            self.velocity_plot.blit()
            self.kinetic_energy_plot.blit()
            self.potential_energy_plot.blit()
            self.total_energy_plot.blit()
            self.total_energy_loss_plot.blit()

    def get_xy(self):
        return self.table['xy'][self.index]

    def get_pos(self, offset=0):
        index = self.index + offset
        if index >= self.table_length: index -= self.table_length
        elif index < 0: index += self.table_length
        return self.table['p'][index]
    
    def get_k(self):
        return self.k
    
    def get_kintetic(self):
        return self.velocity**2 * parameters['M'] / 2

    def get_potential(self):
        return parameters['M'] * parameters['G'] * (self.get_xy()[1] - self.table['min_y'])

    def get_total(self):
        return self.get_potential() + self.get_kintetic()
    
    def get_total_energy_loss(self):
        return self.start_energy - self.get_total()

    def pause(self):
        self.is_pause = True
        self.pause_offset = time.time() - self.t

    def set_selected(self):
        self.selected = True
        self.init_surface()
    
    def set_not_selected(self):
        self.selected = False
        self.init_surface()

    def resume(self):
        self.is_pause = False
        offset = time.time() - self.t
        self.acceleration_plot.time_offset += offset
        self.velocity_plot.time_offset += offset
        self.kinetic_energy_plot.time_offset += offset
        self.potential_energy_plot.time_offset += offset
        self.total_energy_plot.time_offset += offset
        self.t = time.time() - self.pause_offset
    

class PlotGraph:
    def __init__(self, initial_value, pos, name, scale=1) -> None:
        self.pos = pos
        self.scale = scale
        self.name = name
        self.initial_time = initial_value[0]
        self.time_offset = 0
        self.time_scale = 10
        self.values = [initial_value]
        self.reset_surface()
    
    def reset_surface(self):
        self.surface = pygame.Surface(PLOT_SIZE, pygame.SRCALPHA, 32)
        self.rectangle = self.surface.get_rect().move(self.pos)

    def plot(self, new_value):
        self.values.append(new_value - np.array([self.time_offset, 0]))
        self.rescale()
        self.surface = pygame.Surface(PLOT_SIZE, pygame.SRCALPHA, 32)
        self.rectangle = self.surface.get_rect().move(self.pos)
        line = [self.transform(v) for v in self.values]
        pygame.draw.aalines(self.surface, BLACK, False, line)
        if (line[-1][0] > self.surface.get_width()):
            self.scale = 1
            self.rescale()
            self.values = self.values[-2:]
            self.initial_time = self.values[0][0]
    
    def rescale(self):
        while abs(self.values[-1][1]) >= self.scale/2: self.scale *= 5

    
    def transform(self, value):
        new_value = [0, 0]
        new_value[0] = (value[0] - self.initial_time) * self.time_scale
        new_value[1] = (-value[1] / self.scale) * PLOT_HEIGHT + PLOT_HEIGHT/2
        return new_value

    def blit(self):
        step = 25
        x, y = self.rectangle.x, self.rectangle.y
        color = GRAPH_COLOR
        constr_width = int(self.surface.get_width()) - (int(self.surface.get_width()) % step)
        constr_height = int(self.surface.get_height()) - (int(self.surface.get_height()) % step)
        current_value = self.values[-1][1]
        if abs(current_value) < 0:
            current_value = round(current_value, 6)
        else:
            current_value = round(current_value, 2)
        name = my_font.render(self.name + f':   {current_value}', True, BLACK)
        screen.blit(name, self.rectangle.move(0, -30))
        for i in range(0, constr_width + 1, step):
            pygame.draw.line(screen, color, (x + i, y), (x + i, y + constr_height))
        for i in range(0, constr_height + 1, step):
            y_axis = self.scale * (constr_height/2 - i) / constr_height
            if abs(y_axis) > 1:
                y_axis = int(y_axis)
            else:
                y_axis = round(y_axis, 2)
            text = my_font10.render(f"{y_axis}", True, BLACK)
            screen.blit(text, (x - 10 - text.get_width(), y + i- 10))
            pygame.draw.line(screen, color, (x, y + i), (x + constr_width, y + i))
        screen.blit(self.surface, self.rectangle)