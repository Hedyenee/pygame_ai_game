import pygame
import random

class Obstacle:
    def __init__(self):
        self.width = random.randint(30, 80)
        self.height = random.randint(30, 80)
        self.x = random.randint(0, 800 - self.width)
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.color = (random.randint(200, 255), random.randint(0, 100), random.randint(0, 100))
        
    def update(self):
        self.y += self.speed
        return self.y > 600
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)