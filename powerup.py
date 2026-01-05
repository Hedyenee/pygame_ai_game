import pygame
import random


class PowerUp:
    TYPES = ["speed", "shield", "points", "slow", "zap", "ammo"]

    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(50, 750 - self.width)
        self.y = -self.height
        self.speed = 3
        self.type = random.choice(self.TYPES)

        if self.type == "speed":
            self.color = (255, 255, 0)
            self.symbol = "SPD"
        elif self.type == "shield":
            self.color = (0, 200, 255)
            self.symbol = "SHD"
        elif self.type == "points":
            self.color = (0, 255, 0)
            self.symbol = "+50"
        elif self.type == "slow":
            self.color = (180, 130, 255)
            self.symbol = "SLOW"
        elif self.type == "zap":
            self.color = (255, 80, 80)
            self.symbol = "ZAP"
        else:  # ammo
            self.color = (255, 200, 120)
            self.symbol = "AMMO"

    def update(self):
        self.y += self.speed
        return self.y > 600

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 20)
        text = font.render(self.symbol, True, (0, 0, 0))
        screen.blit(text, (self.x + 2, self.y + 6))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def apply_effect(self, player, game):
        if self.type == "speed":
            player.activate_speed_boost()
        elif self.type == "shield":
            player.activate_shield()
        elif self.type == "points":
            player.score += 50
        elif self.type == "slow":
            game.slow_timer = 4.0
        elif self.type == "zap":
            game.zap_closest_obstacle()
        elif self.type == "ammo":
            player.ammo = min(player.max_ammo, player.ammo + 5)
