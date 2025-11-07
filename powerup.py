import pygame
import random

class PowerUp:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(50, 750 - self.width)
        self.y = -self.height
        self.speed = 3
        self.type = random.choice(['speed', 'shield', 'points'])
        
        if self.type == 'speed':
            self.color = (255, 255, 0)  # Jaune
            self.symbol = "⚡"
        elif self.type == 'shield':
            self.color = (0, 200, 255)  # Cyan
            self.symbol = "🛡️"
        else:
            self.color = (0, 255, 0)  # Vert
            self.symbol = "⭐"
        
    def update(self):
        self.y += self.speed
        return self.y > 600
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Dessiner un symbole
        font = pygame.font.Font(None, 24)
        text = font.render(self.symbol, True, (0, 0, 0))
        screen.blit(text, (self.x + 5, self.y + 3))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def apply_effect(self, player):
        if self.type == 'speed':
            player.activate_speed_boost()
        elif self.type == 'shield':
            player.activate_shield()
        else:  # points
            player.score += 50