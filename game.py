import pygame
import random
import time
from player import Player
from obstacle import Obstacle
from ai import SimpleAI
from powerup import PowerUp

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Jeu avec IA Améliorée - Score: 0")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.player = Player(375, 500)
        self.obstacles = []
        self.power_ups = []
        self.ai = SimpleAI(self.player, self.obstacles, self.power_ups, 800, 600)
        
        self.obstacle_timer = 0
        self.game_over = False
        self.ai_mode = False
        self.level = 1
        self.start_time = time.time()
        self.power_up_timer = 0
        self.ai_thinking = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_a:
                    self.ai_mode = not self.ai_mode
                    print(f"Mode IA: {'ACTIVÉ' if self.ai_mode else 'DÉSACTIVÉ'}")
        return True
        
    def reset_game(self):
        self.player = Player(375, 500)
        self.obstacles = []
        self.power_ups = []
        self.ai = SimpleAI(self.player, self.obstacles, self.power_ups, 800, 600)
        self.obstacle_timer = 0
        self.game_over = False
        self.level = 1
        self.start_time = time.time()
        self.power_up_timer = 0
        self.ai_thinking = False
        pygame.display.set_caption("Jeu avec IA Améliorée - Score: 0")
        
    def update(self):
        if self.game_over:
            return
            
        # Mettre à jour les power-ups du joueur
        self.player.update_power_ups()
            
        # Augmenter la difficulté avec le temps
        current_time = time.time() - self.start_time
        self.level = max(1, int(current_time // 30) + 1)
        
        # Déplacement du joueur
        if not self.ai_mode:
            keys = pygame.key.get_pressed()
            self.player.move(keys)
        else:
            # Mode IA avec indicateur visuel
            self.ai_thinking = True
            self.ai.make_decision()
            self.ai_thinking = False
        
        # Génération d'obstacles avec vitesse selon le niveau
        self.obstacle_timer += 1
        spawn_rate = max(15, 60 - self.level * 6)  # Un peu plus difficile
        if self.obstacle_timer >= spawn_rate:
            new_obstacle = Obstacle()
            new_obstacle.speed += min(8, self.level // 2)  # Plus rapide
            self.obstacles.append(new_obstacle)
            self.obstacle_timer = 0
            
        # Génération de power-ups occasionnels
        self.power_up_timer += 1
        if self.power_up_timer >= 250 and random.random() < 0.4:  # Plus fréquents
            self.power_ups.append(PowerUp())
            self.power_up_timer = 0
            
        # Mise à jour des obstacles
        obstacles_to_remove = []
        for obstacle in self.obstacles:
            if obstacle.update():
                obstacles_to_remove.append(obstacle)
                self.player.score += 1
                pygame.display.set_caption(f"Jeu avec IA Améliorée - Score: {self.player.score} - Niveau: {self.level}")
                
        for obstacle in obstacles_to_remove:
            self.obstacles.remove(obstacle)
            
        # Mise à jour des power-ups
        for power_up in self.power_ups[:]:
            if power_up.update():
                self.power_ups.remove(power_up)
            elif self.player.get_rect().colliderect(power_up.get_rect()):
                power_up.apply_effect(self.player)
                self.power_ups.remove(power_up)
            
        # Détection de collision avec les obstacles (sauf si bouclier actif)
        for obstacle in self.obstacles:
            if (self.player.get_rect().colliderect(obstacle.get_rect()) and 
                self.player.shield_time <= 0):
                self.game_over = True
                
    def draw(self):
        # Fond avec dégradé qui change avec le niveau
        r = min(100, self.level * 12)
        g = min(50, self.level * 5)
        b = min(150, self.level * 20)
        self.screen.fill((r, g, b))
        
        # Dessiner le joueur
        self.player.draw(self.screen)
        
        # Dessiner les obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Dessiner les power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen)
            
        # Afficher les informations
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        level_text = self.font.render(f"Niveau: {self.level}", True, (255, 255, 0))
        self.screen.blit(level_text, (10, 50))
        
        mode_color = (0, 255, 0) if self.ai_mode else (255, 100, 100)
        mode_text = self.font.render(f"Mode: {'IA INTELLIGENTE' if self.ai_mode else 'MANUEL'}", True, mode_color)
        self.screen.blit(mode_text, (10, 90))
        
        # Indicateur de pensée de l'IA
        if self.ai_mode and self.ai_thinking:
            think_text = self.small_font.render("IA en réflexion...", True, (255, 255, 0))
            self.screen.blit(think_text, (10, 130))
        
        # Afficher les effets actifs
        y_offset = 150
        if self.player.speed_boost_time > 0:
            boost_text = self.small_font.render(f"⚡ Vitesse x2: {self.player.speed_boost_time:.1f}s", True, (0, 255, 0))
            self.screen.blit(boost_text, (10, y_offset))
            y_offset += 25
            
        if self.player.shield_time > 0:
            shield_text = self.small_font.render(f"🛡️ Bouclier: {self.player.shield_time:.1f}s", True, (0, 200, 255))
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 25
        
        # Instructions
        instructions = self.small_font.render("A: Mode IA | ESPACE: Redémarrer | Flèches: Déplacer", True, (200, 200, 200))
        self.screen.blit(instructions, (200, 570))
        
        # Statistiques IA
        if self.ai_mode:
            stats_text = self.small_font.render(f"Obstacles: {len(self.obstacles)} | Power-ups: {len(self.power_ups)}", True, (200, 200, 255))
            self.screen.blit(stats_text, (500, 10))
        
        if self.game_over:
            # Overlay semi-transparent
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            score_final = self.font.render(f"Score Final: {self.player.score}", True, (255, 255, 255))
            level_final = self.font.render(f"Niveau Atteint: {self.level}", True, (255, 255, 0))
            restart_text = self.font.render("Appuyez sur ESPACE pour recommencer", True, (200, 200, 0))
            
            self.screen.blit(game_over_text, (400 - game_over_text.get_width()//2, 200))
            self.screen.blit(score_final, (400 - score_final.get_width()//2, 250))
            self.screen.blit(level_final, (400 - level_final.get_width()//2, 300))
            self.screen.blit(restart_text, (400 - restart_text.get_width()//2, 350))
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()