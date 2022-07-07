from tkinter.messagebox import NO
import pygame
from conf import *
from slide import *
from slider import *
from button import *

class Graph:
    def __init__(self, position=GRAPH_POSITION) -> None:
        self.position = position
        self.size = GRAPH_SIZE
        self.height = GRAPH_HEIGHT
        self.width = GRAPH_WIDTH
        self.slides = [Slide(points=DEFAULT_POINTS3)]
        self.set_selection(0)
        self.is_pause = False

    def handle_drag(self, event, pause, resume):
        for s in self.slides:
            if s.handle_drag(event, pause, resume): 
                return True
        return False
    
    def add_function_curve(self):
        self.add_curve(Slide(False, curve))
    
    def add_bezier3(self):
        if self.selected is None:
            self.add_curve(Slide(points=DEFAULT_POINTS3))
        else:
            start = self.slides[-1].curve.ctrl[0] * GRAPH_STEP / parameters['SCALE']
            end = self.slides[-1].curve.ctrl[-1] * GRAPH_STEP / parameters['SCALE']
            self.add_curve(Slide(points=[start, (end + start)/2, end]))
    
    
    def add_bezier4(self):
        if self.selected is None:
            self.add_curve(Slide(points=DEFAULT_POINTS4))
        else:
            start = self.slides[-1].curve.ctrl[0] * GRAPH_STEP / parameters['SCALE']
            end = self.slides[-1].curve.ctrl[-1] * GRAPH_STEP / parameters['SCALE']
            self.add_curve(Slide(points=[start, (end + start)/4, 3*(end + start)/4, end]))
    
    def add_curve(self, curve):
        self.slides.append(curve)
        self.set_selection(len(self.slides) - 1)
        self.reset()

    def move(self):
        if not self.is_pause:
            for s in self.slides:
                s.move()
    
    def pause(self):
        for s in self.slides:
            s.pause()
        self.is_pause = True
    
    def resume(self):
        for s in self.slides:
            s.resume()
        self.is_pause = False
    
    def reset(self):
        for s in self.slides:
            s.reset()

    def set_selection(self, selected):
        for s in self.slides:
            s.set_not_selected()
        self.selected = selected
        self.slides[self.selected].set_selected()
    
    def select_next(self):
        if self.selected is None: return
        if self.selected == len(self.slides) - 1:
            self.set_selection(0)
        else:
            self.set_selection(self.selected + 1)

    def remove(self):
        self.slides.pop(self.selected)
        if len(self.slides) == 0:
            self.selected = None
        else:
            self.set_selection(len(self.slides) - 1)

    def blit(self):
        step = GRAPH_STEP
        x, y = GRAPH_POS_X, GRAPH_POS_Y
        color = GRAPH_COLOR
        constr_width = GRAPH_WIDTH_CONSTR
        constr_height = GRAPH_HEIGHT_CONSTR
        for i in range(x, constr_width + 1, step):
            x_axis = parameters['SCALE'] * (i - x)/step
            text = my_font10.render(f"{int(x_axis)}", True, BLACK)
            screen.blit(text, (i, constr_height))
            pygame.draw.line(screen, color, (i, y), (i, constr_height))
        for i in range(y, constr_height + 1, step):
            y_axis = parameters['SCALE'] * (constr_height - i)/step
            text = my_font10.render(f"{int(y_axis)}", True, BLACK)
            screen.blit(text, (x-text.get_width()-5, i - 10))
            pygame.draw.line(screen, color, (x, i), (constr_width, i))
        for s in self.slides:
            s.blit()


class Brachistochrone:
    def __init__(self) -> None:
        self.clock = pygame.time.Clock()
        self.running = True
        self.graph = Graph()
        self.init_buttons()
        self.init_sliders()
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_drag(event)
                    self.handle_button_press(event)
            self.draw_window()
        pygame.quit()

    def handle_drag(self, event):
        if self.graph.handle_drag(event, self.graph.pause, self.graph.resume):
            return True
        for s in self.sliders:
            if s.handle_drag(event, self.graph.pause, self.graph.resume):
                return True
        return False

    def handle_button_press(self, event):
        for b in self.buttons:
            if b.handle_press(event):
                return True
        return False

    def init_buttons(self):
        pause_text = my_font.render('pause', True, BLACK)
        resume_text = my_font.render('resume', True, BLACK)
        reset_text = my_font.render('reset', True, BLACK)
        add_bezier3_text = my_font.render('add 3-p bezier', True, BLACK)
        add_bezier4_text = my_font.render('add 4-p bezier', True, BLACK)
        next_text = my_font.render('next', True, BLACK)
        remove_text = my_font.render('remove', True, BLACK)
        column_x = GRAPH_POS_X + GRAPH_WIDTH - 50
        self.buttons = [
            Button((50, 5), 100, 40, pause_text,  self.graph.pause),
            Button((170, 5), 100, 40, resume_text, self.graph.resume),
            Button((290, 5), 100, 40, reset_text, self.graph.reset),
            Button((column_x, 55), 150, 40, add_bezier3_text, self.graph.add_bezier3),
            Button((column_x, 105), 150, 40, add_bezier4_text, self.graph.add_bezier4),
            Button((column_x, 155), 150, 40, next_text, self.graph.select_next),
            Button((column_x, 205), 150, 40, remove_text, self.graph.remove)
        ]
    
    def resume(self):
        self.graph.resume()

    def init_sliders(self):
        column_x = GRAPH_POS_X + GRAPH_WIDTH - 40
        self.sliders = [
            Slider("Gravitational force", (column_x, 265), (150, 50), -20, 20, parameters['G'], self.set_g),
            Slider("Mass", (column_x, 325), (150, 50), 1, 11, parameters['M'], self.set_m),
            Slider("Friction coefficient", (column_x, 385), (150, 50), 0, 1, parameters['MU'], self.set_mu),
            Slider("Scale (cell to meter)", (column_x, 445), (150, 50), 1, 100, parameters['SCALE'], self.set_scale)
        ]

    def set_g(self, g):
        parameters['G'] = g

    def set_m(self, m):
        parameters['M'] = m

    def set_mu(self, mu):
        parameters['MU'] = mu

    def set_scale(self, scale):
        parameters['SCALE'] = scale
        self.graph.reset()

    def draw_window(self):
        screen.fill(WHITE)
        self.graph.move()
        self.graph.blit()
        for b in self.buttons:
            b.blit()
        for s in self.sliders:
            s.blit()
        pygame.display.update()      

if __name__ == "__main__":
    b = Brachistochrone()
    b.run()