import pygame
from projectile import Projectile

class Player:
    def __init__(self, x, y, name="Joueur", color=(0, 128, 255), controls=None, screen_size=(800, 600)):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.base_speed = 5
        self.speed = self.base_speed
        self.shape = "rect"
        self.score = 0
        self.speed_boost_time = 0
        self.shield_time = 0
        self.shield_color = (0, 200, 255)
        self.name = name
        self.alive = True
        self.ai_enabled = False
        self.ai_extra_hits = 0  # marge d'erreur quand l'IA est active
        self.screen_width, self.screen_height = screen_size
        self.controls = controls or {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "shoot": pygame.K_RCTRL,
        }
        self.spawn_point = (x, y)
        self.max_ammo = 3
        self.ammo = self.max_ammo
        
    def reset(self):
        self.x, self.y = self.spawn_point
        self.score = 0
        self.speed = self.base_speed
        self.speed_boost_time = 0
        self.shield_time = 0
        self.alive = True
        self.ai_enabled = False
        self.ai_extra_hits = 0
        self.ammo = self.max_ammo
        self.shape = "rect"
    
    def draw(self, screen):
        if not self.alive:
            return
        if self.shield_time > 0:
            pygame.draw.circle(
                screen,
                self.shield_color,
                (self.x + self.width // 2, self.y + self.height // 2),
                self.width + 5,
                3,
            )

        if self.shape == "circle":
            pygame.draw.circle(
                screen,
                self.color,
                (self.x + self.width // 2, self.y + self.height // 2),
                self.width // 2,
            )
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        if self.speed_boost_time > 0:
            for i in range(3):
                offset = (i - 1) * 2
                pygame.draw.rect(
                    screen,
                    (255, 255, 0),
                    (self.x + offset, self.y + offset, self.width, self.height),
                    2,
                )
        
    def move(self, keys):
        if not self.alive:
            return
        current_speed = self.speed
        
        if keys[self.controls["left"]] and self.x > 0:
            self.x -= current_speed
        if keys[self.controls["right"]] and self.x < self.screen_width - self.width:
            self.x += current_speed
        if keys[self.controls["up"]] and self.y > 0:
            self.y -= current_speed
        if keys[self.controls["down"]] and self.y < self.screen_height - self.height:
            self.y += current_speed

    def shoot(self):
        """Consume ammo to spawn a projectile travelling upward."""
        if not self.alive or self.ammo <= 0:
            return None
        self.ammo -= 1
        spawn_x = self.x + self.width // 2 - 5
        spawn_y = self.y - 10
        return Projectile(spawn_x, spawn_y, owner=self)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update_power_ups(self):
        if not self.alive:
            return
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1 / 60
            if self.speed_boost_time <= 0:
                self.speed = self.base_speed
                self.speed_boost_time = 0
                
        if self.shield_time > 0:
            self.shield_time -= 1 / 60
            if self.shield_time <= 0:
                self.shield_time = 0
    
    def activate_speed_boost(self):
        if not self.alive:
            return
        self.speed = self.base_speed * 2
        self.speed_boost_time = 5
    
    def activate_shield(self):
        if not self.alive:
            return
        self.shield_time = 8
    
    def eliminate(self):
        self.alive = False
    
    def toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        # Donner une marge d'erreur d'un coup quand l'IA est activée
        self.ai_extra_hits = 1 if self.ai_enabled else 0
