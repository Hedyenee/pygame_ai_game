import pygame
import time

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = (0, 128, 255)
        self.base_speed = 5
        self.speed = self.base_speed
        self.score = 0
        self.speed_boost_time = 0
        self.shield_time = 0
        self.shield_color = (0, 200, 255)
        
    def draw(self, screen):
        # Dessiner le bouclier si actif
        if self.shield_time > 0:
            pygame.draw.circle(screen, self.shield_color, 
                             (self.x + self.width//2, self.y + self.height//2), 
                             self.width + 5, 3)
        
        # Dessiner le joueur
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Effet visuel pour speed boost
        if self.speed_boost_time > 0:
            for i in range(3):
                offset = (i - 1) * 2
                pygame.draw.rect(screen, (255, 255, 0), 
                               (self.x + offset, self.y + offset, self.width, self.height), 2)
        
    def move(self, keys):
        current_speed = self.speed
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= current_speed
        if keys[pygame.K_RIGHT] and self.x < 750:
            self.x += current_speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= current_speed
        if keys[pygame.K_DOWN] and self.y < 550:
            self.y += current_speed
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update_power_ups(self):
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1/60  # 60 FPS
            if self.speed_boost_time <= 0:
                self.speed = self.base_speed
                self.speed_boost_time = 0
                
        if self.shield_time > 0:
            self.shield_time -= 1/60
            if self.shield_time <= 0:
                self.shield_time = 0
    
    def activate_speed_boost(self):
        self.speed = self.base_speed * 2
        self.speed_boost_time = 5  # 5 secondes
    
    def activate_shield(self):
        self.shield_time = 8  # 8 secondes