import random
import math
import pygame  

class SimpleAI:
    def __init__(self, player, obstacles, power_ups, screen_width=800, screen_height=600):
        self.player = player
        self.obstacles = obstacles
        self.power_ups = power_ups
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.last_direction = None
        self.escape_attempts = 0
        
    def make_decision(self):
        # Mettre à jour la position du joueur pour l'IA
        player_rect = self.player.get_rect()
        
        # 1. Détection des dangers IMMÉDIATS
        immediate_dangers = self.find_immediate_dangers()
        
        # 2. Détection des dangers PROCHES
        near_dangers = self.find_near_dangers()
        
        # 3. Priorité absolue: Éviter les collisions immédiates
        if immediate_dangers:
            self.handle_immediate_danger(immediate_dangers)
            self.escape_attempts += 1
            return
            
        # 4. Priorité haute: Éviter les obstacles proches
        if near_dangers:
            self.avoid_obstacles(near_dangers)
            self.escape_attempts = 0
            return
            
        # 5. Réinitialiser les tentatives d'échappement si pas de danger
        self.escape_attempts = 0
        
        # 6. Chercher les power-ups intéressants
        good_power_up = self.find_good_power_up()
        if good_power_up:
            self.chase_power_up(good_power_up)
            return
            
        # 7. Comportement intelligent: se positionner stratégiquement
        self.smart_positioning()
    
    def find_immediate_dangers(self):
        """Trouve les obstacles qui vont collisionner dans moins de 1 seconde"""
        immediate_dangers = []
        player_rect = self.player.get_rect()
        
        for obstacle in self.obstacles:
            # Calculer le temps avant collision
            time_to_collision = self.calculate_time_to_collision(obstacle)
            
            # Vérifier si collision imminente
            will_collide = self.will_collide(obstacle, player_rect)
            
            if will_collide and time_to_collision < 1.0:  # Moins de 1 seconde
                immediate_dangers.append({
                    'obstacle': obstacle,
                    'time': time_to_collision,
                    'danger_level': 10 - time_to_collision  # Plus c'est proche, plus c'est dangereux
                })
        
        # Trier par niveau de danger
        immediate_dangers.sort(key=lambda x: x['danger_level'], reverse=True)
        return immediate_dangers
    
    def find_near_dangers(self):
        """Trouve les obstacles qui sont proches et sur une trajectoire dangereuse"""
        near_dangers = []
        player_rect = self.player.get_rect()
        
        for obstacle in self.obstacles:
            time_to_collision = self.calculate_time_to_collision(obstacle)
            will_collide = self.will_collide(obstacle, player_rect)
            
            if will_collide and time_to_collision < 3.0:  # Moins de 3 secondes
                near_dangers.append({
                    'obstacle': obstacle,
                    'time': time_to_collision,
                    'danger_level': 5 - time_to_collision
                })
            elif self.is_near_trajectory(obstacle) and time_to_collision < 4.0:
                # Obstacle proche de la trajectoire
                near_dangers.append({
                    'obstacle': obstacle,
                    'time': time_to_collision,
                    'danger_level': 3 - time_to_collision
                })
        
        near_dangers.sort(key=lambda x: x['danger_level'], reverse=True)
        return near_dangers
    
    def calculate_time_to_collision(self, obstacle):
        """Calcule le temps avant collision avec l'obstacle"""
        if obstacle.speed <= 0:
            return float('inf')
            
        distance_y = obstacle.y - (self.player.y + self.player.height)
        return distance_y / obstacle.speed
    
    def will_collide(self, obstacle, player_rect):
        """Vérifie si l'obstacle va collisionner avec le joueur"""
        obstacle_rect = obstacle.get_rect()
        
        # Vérifier chevauchement en X
        x_overlap = (obstacle_rect.x < player_rect.x + player_rect.width and 
                    obstacle_rect.x + obstacle_rect.width > player_rect.x)
        
        # Vérifier que l'obstacle est au-dessus et se dirige vers le joueur
        coming_toward = obstacle.y < player_rect.y + player_rect.height
        
        return x_overlap and coming_toward
    
    def is_near_trajectory(self, obstacle):
        """Vérifie si l'obstacle est proche de la trajectoire du joueur"""
        player_center_x = self.player.x + self.player.width / 2
        obstacle_center_x = obstacle.x + obstacle.width / 2
        
        distance_x = abs(player_center_x - obstacle_center_x)
        safe_distance = (self.player.width + obstacle.width) / 2 + 20
        
        return distance_x < safe_distance
    
    def handle_immediate_danger(self, dangers):
        """Gère les dangers immédiats - priorité MAXIMALE"""
        if not dangers:
            return
            
        most_dangerous = dangers[0]['obstacle']
        
        # Essayer différentes stratégies d'évitement
        if self.escape_attempts < 3:
            # Stratégie normale: éviter côté avec plus d'espace
            self.evade_to_safest_side(most_dangerous)
        else:
            # Stratégie d'urgence: mouvement aléatoire rapide
            self.emergency_evasion()
    
    def evade_to_safest_side(self, obstacle):
        """Évite vers le côté le plus sûr"""
        left_space = self.player.x  # Espace à gauche
        right_space = self.screen_width - (self.player.x + self.player.width)  # Espace à droite
        
        obstacle_center = obstacle.x + obstacle.width / 2
        player_center = self.player.x + self.player.width / 2
        
        # Vérifier s'il y a d'autres obstacles sur les côtés
        left_clear = self.is_side_clear('left')
        right_clear = self.is_side_clear('right')
        
        if left_clear and right_clear:
            # Les deux côtés sont libres, choisir le plus spacieux
            if left_space > right_space and player_center > obstacle_center:
                self.move_left()
            else:
                self.move_right()
        elif left_clear:
            self.move_left()
        elif right_clear:
            self.move_right()
        else:
            # Aucun côté libre - mouvement d'urgence
            self.emergency_evasion()
    
    def is_side_clear(self, side, look_ahead=100):
        """Vérifie si un côté est libre d'obstacles"""
        check_x = 0
        check_width = 0
        
        if side == 'left':
            check_x = max(0, self.player.x - look_ahead)
            check_width = look_ahead
        else:  # right
            check_x = self.player.x + self.player.width
            check_width = look_ahead
        
        check_rect = pygame.Rect(check_x, self.player.y, check_width, self.player.height)
        
        for obstacle in self.obstacles:
            if check_rect.colliderect(obstacle.get_rect()):
                return False
        return True
    
    def avoid_obstacles(self, dangers):
        """Évite les obstacles proches de manière intelligente"""
        if not dangers:
            return
            
        # Analyser tous les dangers pour trouver la meilleure direction
        best_direction = self.analyze_escape_directions(dangers)
        
        if best_direction == 'left':
            self.move_left()
        elif best_direction == 'right':
            self.move_right()
        elif best_direction == 'wait':
            # Rester sur place peut être la meilleure option
            pass
        else:
            # Aucune bonne option - mouvement prudent
            self.prudent_movement()
    
    def analyze_escape_directions(self, dangers):
        """Analyse les directions d'échappement possibles"""
        left_score = 0
        right_score = 0
        wait_score = 0
        
        for danger in dangers:
            obstacle = danger['obstacle']
            obstacle_center = obstacle.x + obstacle.width / 2
            player_center = self.player.x + self.player.width / 2
            
            if obstacle_center < player_center:
                # Obstacle vient de gauche - mieux vaut aller à droite
                right_score += danger['danger_level']
            else:
                # Obstacle vient de droite - mieux vaut aller à gauche
                left_score += danger['danger_level']
            
            # Parfois rester sur place est mieux si l'obstacle va passer sur les côtés
            if abs(obstacle_center - player_center) > obstacle.width:
                wait_score += danger['danger_level'] / 2
        
        # Vérifier la disponibilité des directions
        if not self.is_side_clear('left'):
            left_score = -100
        if not self.is_side_clear('right'):
            right_score = -100
        
        # Choisir la meilleure direction
        if left_score > right_score and left_score > wait_score:
            return 'left'
        elif right_score > left_score and right_score > wait_score:
            return 'right'
        elif wait_score > left_score and wait_score > right_score:
            return 'wait'
        else:
            return 'right'  # Par défaut
    
    def find_good_power_up(self):
        """Trouve les power-ups intéressants à attraper"""
        good_power_ups = []
        
        for power_up in self.power_ups:
            # Calculer la valeur du power-up
            value = self.calculate_power_up_value(power_up)
            
            # Vérifier si c'est safe d'aller le chercher
            if value > 2 and self.is_power_up_safe(power_up):
                good_power_ups.append({
                    'power_up': power_up,
                    'value': value
                })
        
        if good_power_ups:
            # Prendre le power-up le plus valuable
            best_power_up = max(good_power_ups, key=lambda x: x['value'])
            return best_power_up['power_up']
        
        return None
    
    def calculate_power_up_value(self, power_up):
        """Calcule la valeur d'un power-up"""
        base_values = {
            'shield': 5,    # Très valuable - protection
            'speed': 3,     # Moyennement valuable
            'points': 1     # Peu valuable
        }
        
        base_value = base_values.get(power_up.type, 1)
        
        # Ajuster selon la distance
        distance = self.calculate_distance_to_power_up(power_up)
        distance_factor = max(0.1, 1.0 - (distance / 500))  # Plus c'est proche, mieux c'est
        
        # Ajuster selon les besoins actuels
        need_factor = 1.0
        if power_up.type == 'shield' and self.player.shield_time < 2:
            need_factor = 2.0  # Besoin urgent de bouclier
        elif power_up.type == 'speed' and self.player.speed_boost_time < 2:
            need_factor = 1.5  # Besoin de vitesse
        
        return base_value * distance_factor * need_factor
    
    def calculate_distance_to_power_up(self, power_up):
        """Calcule la distance jusqu'au power-up"""
        dx = power_up.x - self.player.x
        dy = power_up.y - self.player.y
        return math.sqrt(dx*dx + dy*dy)
    
    def is_power_up_safe(self, power_up):
        """Vérifie s'il est safe d'aller chercher le power-up"""
        # Vérifier les obstacles sur le chemin
        path_rect = self.calculate_path_to_power_up(power_up)
        
        for obstacle in self.obstacles:
            if self.will_collide(obstacle, path_rect):
                time_to_power_up = self.calculate_time_to_power_up(power_up)
                time_to_obstacle = self.calculate_time_to_collision(obstacle)
                
                if time_to_obstacle < time_to_power_up + 1.0:  # Marge de sécurité
                    return False
        
        return True
    
    def calculate_path_to_power_up(self, power_up):
        """Calcule le rectangle représentant le chemin vers le power-up"""
        x1 = min(self.player.x, power_up.x)
        x2 = max(self.player.x + self.player.width, power_up.x + power_up.width)
        y1 = min(self.player.y, power_up.y)
        y2 = max(self.player.y + self.player.height, power_up.y + power_up.height)
        
        return pygame.Rect(x1, y1, x2 - x1, y2 - y1)
    
    def calculate_time_to_power_up(self, power_up):
        """Calcule le temps nécessaire pour atteindre le power-up"""
        horizontal_distance = abs((power_up.x + power_up.width/2) - 
                                 (self.player.x + self.player.width/2))
        vertical_distance = abs((power_up.y + power_up.height/2) - 
                               (self.player.y + self.player.height/2))
        
        time_horizontal = horizontal_distance / self.player.speed
        time_vertical = vertical_distance / self.player.speed
        
        return max(time_horizontal, time_vertical)
    
    def chase_power_up(self, power_up):
        """Poursuit un power-up de manière intelligente"""
        power_up_center_x = power_up.x + power_up.width / 2
        player_center_x = self.player.x + self.player.width / 2
        
        # Se déplacer progressivement vers le power-up
        if power_up_center_x > player_center_x + 10:  # Marge pour éviter les oscillations
            self.move_right()
        elif power_up_center_x < player_center_x - 10:
            self.move_left()
        # Sinon, rester aligné
    
    def smart_positioning(self):
        """Se positionne stratégiquement sur l'écran"""
        screen_center = self.screen_width / 2
        player_center = self.player.x + self.player.width / 2
        
        # Préférer le centre pour avoir plus d'options d'évitement
        if abs(player_center - screen_center) > 100:
            # Trop éloigné du centre, se rapprocher
            if player_center < screen_center:
                self.move_right()
            else:
                self.move_left()
        else:
            # Près du centre, faire de petits mouvements stratégiques
            if random.random() < 0.01:  # 1% de chance par frame
                if random.choice([True, False]):
                    self.small_move_left()
                else:
                    self.small_move_right()
    
    def prudent_movement(self):
        """Mouvement prudent quand aucune bonne option n'est disponible"""
        # Bouger légèrement vers le centre
        screen_center = self.screen_width / 2
        player_center = self.player.x + self.player.width / 2
        
        if player_center < screen_center:
            self.small_move_right()
        else:
            self.small_move_left()
    
    def emergency_evasion(self):
        """Mouvement d'urgence quand tout semble perdu"""
        # Mouvement rapide et aléatoire
        if random.choice([True, False]):
            self.move_left()
        else:
            self.move_right()
    
    # Méthodes de mouvement de base
    def move_left(self):
        if self.player.x > self.player.speed:
            self.player.x -= self.player.speed
            self.last_direction = 'left'
    
    def move_right(self):
        if self.player.x < self.screen_width - self.player.width - self.player.speed:
            self.player.x += self.player.speed
            self.last_direction = 'right'
    
    def small_move_left(self):
        if self.player.x > 2:
            self.player.x -= 2
    
    def small_move_right(self):
        if self.player.x < self.screen_width - self.player.width - 2:
            self.player.x += 2

    # Méthodes utilitaires pour la compatibilité
    def find_most_dangerous_obstacle(self):
        dangers = self.find_immediate_dangers()
        if dangers:
            return dangers[0]['obstacle']
        return None
    
    def find_best_power_up(self):
        return self.find_good_power_up()
    
    def avoid_obstacle(self, obstacle):
        self.handle_immediate_danger([{'obstacle': obstacle, 'time': 0.5, 'danger_level': 5}])