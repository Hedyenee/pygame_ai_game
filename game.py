import json
import os
import random
import time
import pygame
from player import Player
from obstacle import Obstacle
from ai import SimpleAI
from powerup import PowerUp
from projectile import Projectile


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Jeu Multi IA - Score: 0")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.players = self._create_players()
        self.obstacles = []
        self.power_ups = []
        self.projectiles = []
        self.ai_controllers = self._create_ai_controllers()

        self.obstacle_timer = 0
        self.game_over = False
        self.level = 1
        self.start_time = time.time()
        self.power_up_timer = 0
        self.ai_thinking = {player.name: False for player in self.players}
        self.global_best = 0
        self.high_score = self.load_high_score()
        self.paused = False
        self.in_menu = True
        self.slow_timer = 0.0
        self.muted = False
        self.music_volume = 0.4
        self.fx_volume = 0.7
        self.sounds = self._load_sounds()
        self.music_loaded = self._load_music()
        if self.music_loaded:
            pygame.mixer.music.play(-1)
        self.flash_timer = 0.0
        self.particles = []
        self.in_options = False
        self.pending_remap = None  # (player_index, control_name)
        self.ai_all_default = False
        self.active_players = 2
        self.menu_button_rects = {}
        self.menu_pressed = None

    def _create_players(self):
        return [
            Player(
                325,
                500,
                name="Joueur 1",
                color=(0, 128, 255),
                controls={
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN,
                    "shoot": pygame.K_RCTRL,
                },
                screen_size=(self.screen_width, self.screen_height),
            ),
            Player(
                425,
                500,
                name="Joueur 2",
                color=(255, 165, 0),
                controls={
                    "left": pygame.K_q,
                    "right": pygame.K_d,
                    "up": pygame.K_z,
                    "down": pygame.K_s,
                    "shoot": pygame.K_e,
                },
                screen_size=(self.screen_width, self.screen_height),
            ),
        ]

    def _create_ai_controllers(self):
        return {
            player: SimpleAI(
                player, self.obstacles, self.power_ups, self.screen_width, self.screen_height
            )
            for player in self.players
        }

    def _find_asset(self, base_name, exts):
        sfx_dir = os.path.join("assets", "sfx")
        for ext in exts:
            path = os.path.join(sfx_dir, f"{base_name}{ext}")
            if os.path.exists(path):
                return path
        return None

    def _load_sound(self, base_name, volume=0.6):
        path = self._find_asset(base_name, [".wav", ".ogg", ".mp3"])
        if not path:
            return None
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound
        except Exception:
            return None

    def _load_sounds(self):
        return {
            "hit": self._load_sound("hit", self.fx_volume),
            "powerup": self._load_sound("powerup", self.fx_volume),
            "zap": self._load_sound("zap", self.fx_volume),
            "ai_grace": self._load_sound("ai_grace", self.fx_volume),
            "click": self._load_sound("click", self.fx_volume),
        }

    def _load_music(self):
        path = self._find_asset("music", [".ogg", ".mp3", ".wav"])
        if not path:
            return False
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            return True
        except Exception:
            return False

    def play_sound(self, name):
        snd = self.sounds.get(name)
        if snd and not self.muted:
            snd.play()

    def spawn_particles(self, x, y, color=(255, 255, 255), amount=12):
        for _ in range(amount):
            self.particles.append(
                {
                    "x": x + random.randint(-5, 5),
                    "y": y + random.randint(-5, 5),
                    "vx": random.uniform(-2, 2),
                    "vy": random.uniform(-2, 2),
                    "life": random.randint(20, 35),
                    "color": color,
                    "size": random.randint(2, 4),
                }
            )

    def set_fx_volume(self, value):
        self.fx_volume = max(0.0, min(1.0, value))
        for snd in self.sounds.values():
            if snd:
                snd.set_volume(self.fx_volume if not self.muted else 0)

    def set_music_volume(self, value):
        self.music_volume = max(0.0, min(1.0, value))
        try:
            if not self.muted:
                pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass

    def load_high_score(self):
        path = "highscore.json"
        if not os.path.exists(path):
            return 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
        except Exception:
            return 0

    def save_high_score(self):
        path = "highscore.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.in_options:
                        self.in_options = False
                        self.pending_remap = None
                        return True
                    return False
                if self.in_options:
                    self.handle_options_input(event)
                elif self.in_menu and event.key == pygame.K_o:
                    self.in_options = True
                elif self.in_menu and event.key == pygame.K_1:
                    self.active_players = 1
                elif self.in_menu and event.key == pygame.K_2:
                    self.active_players = 2
                elif self.in_menu and event.key == pygame.K_a:
                    self.ai_all_default = not self.ai_all_default
                elif self.in_menu and event.key == pygame.K_m:
                    self.toggle_mute()
                elif self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game(start_immediately=True)
                elif not self.in_menu and not self.game_over:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_1:
                        self.players[0].toggle_ai()
                    elif event.key == pygame.K_2:
                        self.players[1].toggle_ai()
                    elif event.key in (pygame.K_TAB, pygame.K_t):
                        for player in self.players:
                            player.toggle_ai()
                    elif event.key == pygame.K_m:
                        self.toggle_mute()
                    elif not self.paused:
                        for player in self.players:
                            if not player.alive or player.ai_enabled:
                                continue
                            shoot_key = player.controls.get("shoot")
                            if shoot_key and event.key == shoot_key:
                                proj = player.shoot()
                                if proj:
                                    self.projectiles.append(proj)
                                    self.play_sound("zap")
            if event.type == pygame.MOUSEBUTTONDOWN and self.in_menu:
                self.menu_pressed = self.get_menu_key_at_pos(event.pos)
                if self.menu_pressed:
                    self.play_sound("click")
                    self.handle_menu_click(self.menu_pressed)
            if event.type == pygame.MOUSEBUTTONUP and self.in_menu:
                self.menu_pressed = None
        return True

    def handle_options_input(self, event):
        # Pendant le remap, le prochain keydown assigne directement
        if self.pending_remap and event.key not in (pygame.K_ESCAPE, pygame.K_o):
            player_idx, control_name = self.pending_remap
            if 0 <= player_idx < len(self.players):
                self.players[player_idx].controls[control_name] = event.key
            self.pending_remap = None
            return

        if event.key == pygame.K_o:
            self.in_options = False
            return

        if event.key == pygame.K_LEFT:
            self.set_music_volume(self.music_volume - 0.05)
        elif event.key == pygame.K_RIGHT:
            self.set_music_volume(self.music_volume + 0.05)
        elif event.key == pygame.K_UP:
            self.set_fx_volume(self.fx_volume + 0.05)
        elif event.key == pygame.K_DOWN:
            self.set_fx_volume(self.fx_volume - 0.05)
        elif event.key == pygame.K_a:
            self.ai_all_default = not self.ai_all_default
        elif event.key == pygame.K_m:
            self.toggle_mute()
        elif event.key == pygame.K_1:
            self.pending_remap = (0, "left")
        elif event.key == pygame.K_2:
            self.pending_remap = (0, "right")
        elif event.key == pygame.K_3:
            self.pending_remap = (0, "up")
        elif event.key == pygame.K_4:
            self.pending_remap = (0, "down")
        elif event.key == pygame.K_5:
            self.pending_remap = (0, "shoot")
        elif event.key == pygame.K_6:
            self.pending_remap = (1, "left")
        elif event.key == pygame.K_7:
            self.pending_remap = (1, "right")
        elif event.key == pygame.K_8:
            self.pending_remap = (1, "up")
        elif event.key == pygame.K_9:
            self.pending_remap = (1, "down")
        elif event.key == pygame.K_0:
            self.pending_remap = (1, "shoot")

    def get_menu_key_at_pos(self, pos):
        for key, rect in self.menu_button_rects.items():
            if rect.collidepoint(pos):
                return key
        return None

    def handle_menu_click(self, key):
        if key == "solo":
            self.active_players = 1
        elif key == "duo":
            self.active_players = 2
        elif key == "ia":
            self.ai_all_default = not self.ai_all_default
        elif key == "music":
            self.toggle_mute()
        elif key == "start":
            self.start_game()


    def start_game(self):
        self.in_menu = False
        self.reset_game(start_immediately=True)

    def reset_game(self, start_immediately=False):
        for player in self.players:
            player.reset()
        self.obstacles = []
        self.power_ups = []
        self.projectiles = []
        self.ai_controllers = self._create_ai_controllers()
        self.obstacle_timer = 0
        self.game_over = False
        self.level = 1
        self.start_time = time.time()
        self.power_up_timer = 0
        self.ai_thinking = {player.name: False for player in self.players}
        self.paused = False
        self.slow_timer = 0.0
        self.flash_timer = 0.0
        if start_immediately:
            self.in_menu = False
        pygame.display.set_caption("Jeu Multi IA - Score: 0")
        if self.music_loaded and not self.muted:
            pygame.mixer.music.play(-1)

        if self.ai_all_default:
            for player in self.players:
                player.ai_enabled = True
                player.ai_extra_hits = 1
        if self.active_players == 1:
            # désactiver le joueur 2
            self.players[1].alive = False
            self.players[1].ai_enabled = False

    def zap_closest_obstacle(self):
        if not self.obstacles:
            return
        target = max(self.obstacles, key=lambda o: o.y)
        self.obstacles.remove(target)
        self.play_sound("zap")

    def update(self):
        if self.in_menu or self.paused or self.game_over or self.in_options:
            return

        keys = pygame.key.get_pressed()

        for player in self.players:
            self.ai_thinking[player.name] = False

        for player in self.players:
            player.update_power_ups()

        current_time = time.time() - self.start_time
        self.level = max(1, int(current_time // 30) + 1)
        # changer forme des joueurs après niveau 2
        if self.level >= 2:
            for p in self.players:
                p.shape = "circle"

        for player in self.players:
            if not player.alive:
                continue
            if player.ai_enabled:
                self.ai_thinking[player.name] = True
                self.ai_controllers[player].make_decision()
            else:
                player.move(keys)

        self.obstacle_timer += 1
        spawn_rate = max(15, 60 - self.level * 6)
        if self.obstacle_timer >= spawn_rate:
            new_obstacle = Obstacle()
            new_obstacle.speed += min(8, self.level // 2)
            self.obstacles.append(new_obstacle)
            self.obstacle_timer = 0

        self.power_up_timer += 1
        if self.power_up_timer >= 250 and random.random() < 0.4:
            self.power_ups.append(PowerUp())
            self.power_up_timer = 0

        speed_scale = 0.55 if self.slow_timer > 0 else 1.0
        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - 1 / 60)

        obstacles_to_remove = []
        for obstacle in self.obstacles:
            if obstacle.update(speed_scale):
                obstacles_to_remove.append(obstacle)
                for player in self.players:
                    if player.alive:
                        player.score += 1

        particles_to_remove = []
        for p in self.particles:
            p["x"] += p.get("vx", 0)
            p["y"] += p.get("vy", 0)
            p["life"] -= 1
            if p["life"] <= 0:
                particles_to_remove.append(p)
        for p in particles_to_remove:
            if p in self.particles:
                self.particles.remove(p)

        projectiles_to_remove = []
        destroyed_by_projectile = []
        for projectile in self.projectiles:
            if projectile.update():
                projectiles_to_remove.append(projectile)
                continue
            for obstacle in self.obstacles:
                if projectile.get_rect().colliderect(obstacle.get_rect()):
                    destroyed_by_projectile.append(obstacle)
                    projectiles_to_remove.append(projectile)
                    if projectile.owner and projectile.owner.alive:
                        projectile.owner.score += 1
                    self.play_sound("zap")
                    break

        for projectile in set(projectiles_to_remove):
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)

        for power_up in self.power_ups[:]:
            if power_up.update():
                self.power_ups.remove(power_up)
                continue

            for player in self.players:
                if player.alive and player.get_rect().colliderect(power_up.get_rect()):
                    power_up.apply_effect(player, self)
                    self.play_sound("powerup")
                    self.spawn_particles(power_up.x, power_up.y, color=(150, 255, 200))
                    self.power_ups.remove(power_up)
                    break

        collided_obstacles = []
        for obstacle in self.obstacles:
            for player in self.players:
                if player.alive and player.get_rect().colliderect(obstacle.get_rect()):
                    collided_obstacles.append(obstacle)
                    if player.shield_time > 0:
                        self.flash_timer = 0.25
                    elif player.ai_enabled and player.ai_extra_hits > 0:
                        player.ai_extra_hits -= 1
                        self.flash_timer = 0.25
                        self.play_sound("ai_grace")
                    else:
                        player.eliminate()
                        self.flash_timer = 0.25
                    self.play_sound("hit")

        # Remove any obstacles that were hit by players
        for obstacle in set(obstacles_to_remove + collided_obstacles + destroyed_by_projectile):
            if obstacle in self.obstacles:
                self.obstacles.remove(obstacle)

        if not any(player.alive for player in self.players):
            self.game_over = True

        best_score = max(player.score for player in self.players)
        self.global_best = max(self.global_best, best_score)
        if self.global_best > self.high_score:
            self.high_score = self.global_best
            self.save_high_score()
        pygame.display.set_caption(
            f"Jeu Multi IA - Meilleur: {self.global_best} - Niveau: {self.level} - High score: {self.high_score}"
        )

    def draw(self):
        palette = [
            (30, 30, 60),
            (20, 80, 120),
            (80, 40, 120),
            (100, 100, 40),
            (60, 20, 20),
        ]
        bg = palette[(self.level - 1) % len(palette)]
        self.screen.fill(bg)

        if self.flash_timer > 0:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(int(180 * min(1.0, self.flash_timer * 2)))
            overlay.fill((255, 80, 80))
            self.screen.blit(overlay, (0, 0))
            self.flash_timer = max(0.0, self.flash_timer - 1 / 60)

        for idx, player in enumerate(self.players):
            if self.active_players == 1 and idx > 0:
                continue
            player.draw(self.screen)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        for power_up in self.power_ups:
            power_up.draw(self.screen)

        for p in self.particles:
            pygame.draw.circle(self.screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        for idx, player in enumerate(self.players):
            if self.active_players == 1 and idx > 0:
                continue
            if player.ai_enabled:
                ai = self.ai_controllers.get(player)
                if ai and ai.debug_line:
                    start = ai.debug_line["start"]
                    end = ai.debug_line["end"]
                    color = ai.debug_line.get("color", (255, 255, 255))
                    pygame.draw.line(
                        self.screen,
                        color,
                        (int(start[0]), int(start[1])),
                        (int(end[0]), int(end[1])),
                        3,
                    )
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (int(end[0]), int(end[1])),
                        6,
                        1,
                    )

        level_text = self.font.render(f"Niveau: {self.level}", True, (255, 255, 0))
        self.screen.blit(level_text, (10, 10))

        hs_text = self.small_font.render(f"High score: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(hs_text, (10, 40))

        y_offset = 70
        for idx, player in enumerate(self.players):
            if self.active_players == 1 and idx > 0:
                continue
            color = (0, 255, 0) if player.alive else (150, 150, 150)
            status = "IA" if player.ai_enabled else "Humain"
            text = self.small_font.render(
                f"{player.name} ({status}) - Score: {player.score}", True, color
            )
            self.screen.blit(text, (10, y_offset))
            if player.speed_boost_time > 0:
                boost_text = self.small_font.render(
                    f"Vitesse x2: {player.speed_boost_time:.1f}s", True, (200, 255, 200)
                )
                self.screen.blit(boost_text, (30, y_offset + 20))
            if player.shield_time > 0:
                shield_text = self.small_font.render(
                    f"Bouclier: {player.shield_time:.1f}s", True, (200, 255, 255)
                )
                self.screen.blit(shield_text, (30, y_offset + 40))
            if player.ai_enabled and self.ai_thinking.get(player.name, False):
                thinking_text = self.small_font.render(
                    "IA en reflexion...", True, (255, 255, 0)
                )
                self.screen.blit(thinking_text, (30, y_offset + 60))
            ammo_text = self.small_font.render(
                f"Munitions: {player.ammo} | Hits IA: {player.ai_extra_hits}", True, (255, 230, 180)
            )
            self.screen.blit(ammo_text, (30, y_offset + 80))
            y_offset += 110

        slow_text = ""
        if self.slow_timer > 0:
            slow_text = f"Ralenti: {self.slow_timer:.1f}s"
        stats_text = self.small_font.render(
            f"Obstacles: {len(self.obstacles)} | Power-ups: {len(self.power_ups)} {slow_text} | Son: {'Off' if self.muted else 'On'}",
            True,
            (200, 200, 255),
        )
        self.screen.blit(stats_text, (400, 10))

        instructions = self.small_font.render(
            "ENTREE jouer | 1=Solo 2=Deux joueurs | A: IA auto | M: Son On/Off | O Options | Fleches+Ctrl dr: J1 tir | ZQSD+E: J2 tir | TAB/T IA tous | P Pause | ESPACE Restart",
            True,
            (240, 240, 240),
        )
        self.screen.blit(instructions, (20, 570))

        if self.in_options:
            self.draw_options()
        elif self.in_menu:
            self.draw_menu()
        elif self.paused:
            self.draw_overlay("PAUSE", "Appuie sur P pour reprendre")
        elif self.game_over:
            best_player = max(self.players, key=lambda p: p.score)
            self.draw_overlay(
                "GAME OVER",
                f"Meilleur: {best_player.name} ({best_player.score} pts) | ESPACE pour recommencer",
            )

        pygame.display.flip()

    def draw_overlay(self, title, subtitle):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(190)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font.render(title, True, (255, 255, 255))
        sub_text = self.small_font.render(subtitle, True, (220, 220, 0))
        self.screen.blit(
            title_text,
            (self.screen_width // 2 - title_text.get_width() // 2, 220),
        )
        self.screen.blit(
            sub_text,
            (self.screen_width // 2 - sub_text.get_width() // 2, 280),
        )
    
    def draw_menu(self):
        # fond semi-transparent avec dégradé simple
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((12, 18, 40))
        self.screen.blit(overlay, (0, 0))

        # bandeau supérieur
        header = pygame.Surface((self.screen_width, 120))
        header.fill((30, 60, 120))
        self.screen.blit(header, (0, 0))

        title_text = self.font.render("MENU PRINCIPAL", True, (255, 255, 255))
        subtitle = self.small_font.render("Choisis joueurs, IA, son avant de lancer", True, (220, 230, 255))
        self.screen.blit(
            title_text,
            (self.screen_width // 2 - title_text.get_width() // 2, 28),
        )
        self.screen.blit(
            subtitle,
            (self.screen_width // 2 - subtitle.get_width() // 2, 70),
        )

        self.menu_button_rects = {}

        mouse_pos = pygame.mouse.get_pos()

        def draw_button(rect, title, value, hint, key):
            shadow = rect.move(4, 6)
            pygame.draw.rect(self.screen, (10, 10, 20), shadow, border_radius=14)
            hovered = rect.collidepoint(mouse_pos)
            base_color = (28, 40, 80)
            if self.menu_pressed == key:
                base_color = (18, 90, 150)
            elif hovered:
                base_color = (38, 60, 110)
            pygame.draw.rect(self.screen, base_color, rect, border_radius=14)
            border_col = (90, 150, 240) if hovered else (70, 120, 200)
            pygame.draw.rect(self.screen, border_col, rect, width=2, border_radius=14)
            t = self.small_font.render(title, True, (210, 225, 255))
            v = self.font.render(value, True, (255, 255, 255))
            h = self.small_font.render(hint, True, (180, 195, 215))
            self.screen.blit(t, (rect.x + 16, rect.y + 12))
            self.screen.blit(v, (rect.x + 16, rect.y + 46))
            self.screen.blit(h, (rect.x + 16, rect.y + 86))
            self.menu_button_rects[key] = rect

        btn_w = 340
        btn_h = 120
        gap_x = 30
        gap_y = 24
        start_x = (self.screen_width - (btn_w * 2 + gap_x)) // 2
        start_y = 180
        buttons = [
            ("1 Joueur", "Solo", "Clique pour solo", "solo"),
            ("2 Joueurs", "Duo", "Clique pour duo", "duo"),
            ("IA auto", "On" if self.ai_all_default else "Off", "Clique pour toggle", "ia"),
            ("Musique", "Off" if self.muted else "On", "Clique pour mute", "music"),
        ]

        for idx, (title, value, hint, key) in enumerate(buttons):
            col = idx % 2
            row = idx // 2
            x = start_x + col * (btn_w + gap_x)
            y = start_y + row * (btn_h + gap_y)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            draw_button(rect, title, value, hint, key)

        # bouton start plein centre
        start_rect = pygame.Rect(self.screen_width // 2 - 160, start_y + btn_h * 2 + 40, 320, 70)
        hovered_start = start_rect.collidepoint(mouse_pos)
        start_col = (18, 120, 80)
        if self.menu_pressed == "start":
            start_col = (12, 90, 60)
        elif hovered_start:
            start_col = (22, 150, 100)
        pygame.draw.rect(self.screen, (10, 25, 20), start_rect.move(3, 5), border_radius=16)
        pygame.draw.rect(self.screen, start_col, start_rect, border_radius=16)
        pygame.draw.rect(self.screen, (80, 200, 140), start_rect, width=3, border_radius=16)
        start_txt = self.font.render("START", True, (255, 255, 255))
        self.screen.blit(
            start_txt,
            (start_rect.x + start_rect.width // 2 - start_txt.get_width() // 2,
             start_rect.y + start_rect.height // 2 - start_txt.get_height() // 2),
        )
        self.menu_button_rects["start"] = start_rect

        hint = self.small_font.render("Clique sur START après tes choix", True, (230, 230, 230))
        self.screen.blit(hint, (self.screen_width // 2 - hint.get_width() // 2, start_rect.y + 80))

    def draw_options(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(210)
        overlay.fill((10, 10, 30))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("OPTIONS", True, (255, 255, 255))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 40))

        opts = [
            f"Volume Musique: {int(self.music_volume*100)}% (← / →)",
            f"Volume FX: {int(self.fx_volume*100)}% (↑ / ↓)",
            f"Mute: {'On' if self.muted else 'Off'} (M)",
            f"IA auto pour tous: {'On' if self.ai_all_default else 'Off'} (A)",
            "Remap touches (appuie sur la touche listée puis sur la nouvelle touche):",
            " J1: 1=Gauche 2=Droite 3=Haut 4=Bas 5=Tir",
            " J2: 6=Gauche 7=Droite 8=Haut 9=Bas 0=Tir",
            "Retour: O ou ESC",
        ]
        y = 120
        for line in opts:
            txt = self.small_font.render(line, True, (220, 220, 240))
            self.screen.blit(txt, (60, y))
            y += 28

        p1 = self.players[0].controls
        p2 = self.players[1].controls
        controls_lines = [
            f"J1 map: G:{pygame.key.name(p1['left'])} D:{pygame.key.name(p1['right'])} H:{pygame.key.name(p1['up'])} B:{pygame.key.name(p1['down'])} Tir:{pygame.key.name(p1['shoot'])}",
            f"J2 map: G:{pygame.key.name(p2['left'])} D:{pygame.key.name(p2['right'])} H:{pygame.key.name(p2['up'])} B:{pygame.key.name(p2['down'])} Tir:{pygame.key.name(p2['shoot'])}",
        ]
        y += 10
        for line in controls_lines:
            txt = self.small_font.render(line, True, (180, 220, 255))
            self.screen.blit(txt, (60, y))
            y += 24

        if self.pending_remap:
            idx, ctrl = self.pending_remap
            prompt = self.small_font.render(
                f"Appuie sur la nouvelle touche pour J{idx+1} {ctrl}", True, (255, 220, 120)
            )
            self.screen.blit(prompt, (60, y + 20))

    def toggle_mute(self):
        self.muted = not self.muted
        volume = 0 if self.muted else self.music_volume
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception:
            pass
        for snd in self.sounds.values():
            if snd:
                snd.set_volume(0 if self.muted else self.fx_volume)

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
