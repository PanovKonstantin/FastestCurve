import pygame
from conf import *

class Button:
    def __init__(self, pos, width, height, text, callback) -> None:
        self.pos = pos
        self.width = width
        self.height = height
        self.size = (width, height)
        self.text = text
        self.callback = callback
        self.init_surface()

    def init_surface(self):
        self.surf = pygame.Surface(self.size)
        self.rect = self.surf.get_rect().move(self.pos)
        self.surf.fill((150, 150, 150))
        pygame.draw.rect(self.surf, (100, 100, 100), self.surf.get_rect(), 5)
        padding = (self.width - self.text.get_width())/2
        self.surf.blit(self.text, (padding, 0))
    
    def is_pressed(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN: return False
        if event.button != 1: return False
        return self.rect.collidepoint(event.pos)
    
    def handle_press(self, event):
        if self.is_pressed(event):
            self.callback()
    
    def blit(self):
        screen.blit(self.surf, self.rect)
