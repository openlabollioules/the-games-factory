import pygame
import time
import math
import random
import json
import socket
import threading

# Définition des constantes
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TEAM_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Rouge, Vert, Bleu, Jaune

# Classe Wall
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width=40, height=40):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))  # Gris initialement
        self.rect = self.image.get_rect(topleft=(x, y))
        self.current_team_color = None

    def change_color(self, team_color):
        self.current_team_color = team_color
        self.image.fill(team_color)

# Classe Player
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, team_color):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(team_color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.team_color = team_color
        self.last_shot_time = 0
        self.shot_delay = 500
        self.base_position = (x, y)
        self.immobilized = False
        self.immobilized_until = 0

    def handle_movement(self):
        if not self.immobilized:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.rect.y += self.speed
            self.rect.clamp_ip(WINDOW.get_rect())

    def handle_shooting(self, paint_projectiles_group):
        if not self.immobilized:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_shot_time > self.shot_delay:
                    self.last_shot_time = current_time
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    direction = math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx)
                    projectile = PaintProjectile(self.rect.centerx, self.rect.centery, direction, self.team_color)
                    paint_projectiles_group.add(projectile)

    def immobilize(self):
        self.rect.topleft = self.base_position
        self.immobilized = True
        self.immobilized_until = pygame.time.get_ticks() + 3000

    def update(self, paint_projectiles_group):
        if self.immobilized and pygame.time.get_ticks() > self.immobilized_until:
            self.immobilized = False
        self.handle_movement()
        self.handle_shooting(paint_projectiles_group)

# Classe PaintProjectile
class PaintProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.direction = direction
        self.color = color

    def update(self):
        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or
                self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()
            return
        wall_hit = pygame.sprite.spritecollideany(self, game_manager.walls_group)
        if wall_hit:
            wall_hit.change_color(self.color)
            self.kill()
            return
        player_hit = pygame.sprite.spritecollideany(self, game_manager.players_group)
        if player_hit and player_hit.team_color != self.color:
            if not player_hit.immobilized:
                player_hit.immobilize()
                self.kill()
                return
        elif player_hit and player_hit.immobilized:
            self.kill()
            return

# Classe LevelLoader
class LevelLoader:
    def __init__(self, json_file):
        self.json_file = json_file
        self.walls_group = pygame.sprite.Group()
        self.bases = []

    def load_level(self):
        with open(self.json_file, 'r') as file:
            level_data = json.load(file)
        for wall_data in level_data.get("walls", []):
            x = wall_data.get("x", 0)
            y = wall_data.get("y", 0)
            width = wall_data.get("width", 40)
            height = wall_data.get("height", 40)
            wall = Wall(x, y, width, height)
            self.walls_group.add(wall)
        for base_data in level_data.get("bases", []):
            base_position = (base_data.get("x", 0), base_data.get("y", 0))
            team_color = tuple(base_data.get("team_color", [255, 255, 255]))
            self.bases.append({"position": base_position, "team_color": team_color})

    def get_walls_group(self):
        return self.walls_group

    def get_bases(self):
        return self.bases

# Classe GameManager
class GameManager:
    def __init__(self):
        self.players_group = pygame.sprite.Group()
        self.walls_group = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group()
        self.scores = {color: 0 for color in TEAM_COLORS}
        self.start_time = time.time()
        self.game_duration = 120
        self.window_width = WINDOW_WIDTH

        level_loader = LevelLoader("level_data.json")
        level_loader.load_level()
        self.walls_group = level_loader.get_walls_group()
        self.bases = level_loader.get_bases()
        self.assign_teams()

    def assign_teams(self):
        for i in range(4):
            for j in range(4):
                base = self.bases[i]
                player = Player(base['position'][0] + j * 40, base['position'][1], base['team_color'])
                self.players_group.add(player)

    def calculate_scores(self):
        self.scores = {color: 0 for color in TEAM_COLORS}
        for wall in self.walls_group:
            if wall.current_team_color:
                self.scores[wall.current_team_color] += 1

    def check_game_over(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.game_duration:
            return True
        return False

    def get_winning_team(self):
        return max(self.scores, key=self.scores.get)

    def update(self):
        self.players_group.update(self.projectiles_group)
        self.projectiles_group.update()
        self.calculate_scores()

    def draw(self, window):
        self.walls_group.draw(window)
        self.players_group.draw(window)
        self.projectiles_group.draw(window)

# Classe UIManager
class UIManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font = pygame.font.Font(None, 36)
        self.notification_font = pygame.font.Font(None, 48)
        self.notifications = []
        self.notification_timer = 0

    def draw_timer(self, window):
        elapsed_time = time.time() - self.game_manager.start_time
        time_left = max(0, int(self.game_manager.game_duration - elapsed_time))
        timer_text = self.font.render(f"Temps restant: {time_left}s", True, (0, 0, 0))
        window.blit(timer_text, (10, 10))

    def draw_scores(self, window):
        y_offset = 50
        for idx, (color, score) in enumerate(self.game_manager.scores.items()):
            score_text = self.font.render(f"Score équipe {idx + 1}: {score}", True, color)
            window.blit(score_text, (10, y_offset))
            y_offset += 30

    def draw_notifications(self, window):
        if self.notifications and time.time() < self.notification_timer:
            for i, notification in enumerate(self.notifications):
                notification_text = self.notification_font.render(notification, True, (255, 0, 0))
                window.blit(notification_text, (self.game_manager.window_width // 2 - notification_text.get_width() // 2, 200 + (i * 50)))
        else:
            self.notifications = []

    def add_notification(self, text, duration=3):
        self.notifications.append(text)
        self.notification_timer = time.time() + duration

    def update(self, window):
        self.draw_timer(window)
        self.draw_scores(window)
        self.draw_notifications(window)

# Code principal du jeu
if __name__ == "__main__":
    pygame.init()
    WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Jeu de peinture - Multijoueur")

    game_manager = GameManager()
    ui_manager = UIManager(game_manager)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_manager.update()

        WINDOW.fill((255, 255, 255))  # Fond blanc
        game_manager.draw(WINDOW)
        ui_manager.update(WINDOW)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
