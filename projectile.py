import pygame


class Projectile:
    def __init__(self, x, y, owner=None, speed=12):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 18
        self.speed = speed
        self.color = (255, 255, 200)
        self.owner = owner

    def update(self):
        self.y -= self.speed
        return self.y + self.height < 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
