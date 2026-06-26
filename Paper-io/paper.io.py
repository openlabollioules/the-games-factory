import json
import os
import random
import sys
from collections import deque

import pygame


# ============================================================
# CONFIGURATION
# ============================================================

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

CELL_SIZE = 20
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

PLAYER_DELAY = 80
ENEMY_DELAY = 115

ASSETS = "assets"
SOUNDS = os.path.join(ASSETS, "sounds")

MENU_BACKGROUND = os.path.join(ASSETS, "menu_background.png")
GAME_BACKGROUND = os.path.join(ASSETS, "game_background.png")
PLAYER_IMAGE = os.path.join(ASSETS, "player.png")

MENU_MUSIC = os.path.join(SOUNDS, "menu_music.mp3")
GAME_MUSIC = os.path.join(SOUNDS, "game_music.mp3")
CAPTURE_SOUND = os.path.join(SOUNDS, "capture.wav")
GAME_OVER_SOUND = os.path.join(SOUNDS, "game_over.wav")

HIGHSCORE_FILE = "highscore.json"

EMPTY = 0
PLAYER_ZONE = 1
ENEMY_ZONE = 2

WHITE = (245, 245, 245)
BLACK = (15, 18, 25)
PLAYER_COLOR = (50, 165, 255)
PLAYER_ZONE_COLOR = (30, 105, 195)
PLAYER_TRAIL_COLOR = (130, 220, 255)
ENEMY_COLOR = (255, 70, 90)
ENEMY_ZONE_COLOR = (175, 40, 60)
ENEMY_TRAIL_COLOR = (255, 145, 155)
BUTTON_COLOR = (35, 60, 105)
BUTTON_HOVER = (55, 110, 180)
BUTTON_SELECTED = (40, 145, 225)


# ============================================================
# OUTILS
# ============================================================

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as file:
            return int(json.load(file).get("highscore", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as file:
            json.dump({"highscore": score}, file, indent=4)
    except OSError as error:
        print("Erreur de sauvegarde :", error)


def create_fallback_background(size, seed):
    width, height = size
    surface = pygame.Surface(size)
    rng = random.Random(seed)

    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(15 + 20 * ratio),
            int(25 + 35 * ratio),
            int(60 + 70 * ratio),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))

    decoration = pygame.Surface(size, pygame.SRCALPHA)

    for _ in range(45):
        radius = rng.randint(15, 80)
        x = rng.randint(-radius, width + radius)
        y = rng.randint(-radius, height + radius)
        color = (
            rng.randint(50, 150),
            rng.randint(80, 190),
            rng.randint(150, 255),
            rng.randint(15, 45),
        )
        pygame.draw.circle(decoration, color, (x, y), radius)

    surface.blit(decoration, (0, 0))
    return surface


def load_scaled_image(path, size, alpha=False, fallback_seed=1):
    try:
        image = pygame.image.load(path)
        image = image.convert_alpha() if alpha else image.convert()
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError, OSError) as error:
        print(f"Impossible de charger {path} :", error)
        return create_fallback_background(size, fallback_seed)


def load_player_image():
    size = (CELL_SIZE - 2, CELL_SIZE - 2)

    try:
        image = pygame.image.load(PLAYER_IMAGE).convert_alpha()
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError, OSError) as error:
        print("Image du joueur introuvable :", error)

        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, PLAYER_COLOR, surface.get_rect(), border_radius=5)
        pygame.draw.circle(surface, WHITE, (size[0] // 2 + 4, 6), 3)
        return surface


def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError, OSError) as error:
        print(f"Son introuvable {path} :", error)
        return None


# ============================================================
# AUDIO
# ============================================================

class AudioManager:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.capture_sound = load_sound(CAPTURE_SOUND) if self.enabled else None
        self.game_over_sound = load_sound(GAME_OVER_SOUND) if self.enabled else None
        self.current_music = None

    def toggle(self):
        self.enabled = not self.enabled

        if not self.enabled:
            pygame.mixer.music.stop()
        elif self.current_music:
            self.play_music(self.current_music, force=True)

    def play_music(self, path, force=False):
        if not self.enabled:
            self.current_music = path
            return

        if path == self.current_music and not force:
            return

        self.current_music = path

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError, OSError) as error:
            print(f"Musique introuvable {path} :", error)

    def play_sound(self, sound):
        if self.enabled and sound:
            sound.play()


# ============================================================
# ARRIÈRE-PLAN ANIMÉ
# ============================================================

class AnimatedBackground:
    def __init__(self, path, size, seed):
        self.width, self.height = size
        self.image = load_scaled_image(path, size, fallback_seed=seed)
        self.offset_x = 0.0
        self.offset_y = 0.0

    def update(self, dt):
        self.offset_x = (self.offset_x + 14 * dt) % self.width
        self.offset_y = (self.offset_y + 7 * dt) % self.height

    def draw(self, screen):
        x = int(self.offset_x)
        y = int(self.offset_y)

        for px, py in (
            (-x, -y),
            (self.width - x, -y),
            (-x, self.height - y),
            (self.width - x, self.height - y),
        ):
            screen.blit(self.image, (px, py))


# ============================================================
# BOUTON
# ============================================================

class Button:
    def __init__(self, text, center, size, font):
        self.text = text
        self.font = font
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.hovered = False
        self.selected = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, screen):
        color = (
            BUTTON_SELECTED
            if self.selected
            else BUTTON_HOVER
            if self.hovered
            else BUTTON_COLOR
        )

        pygame.draw.rect(screen, BLACK, self.rect.move(0, 6), border_radius=14)
        pygame.draw.rect(screen, color, self.rect, border_radius=14)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=14)

        text = self.font.render(self.text, True, WHITE)
        screen.blit(text, text.get_rect(center=self.rect.center))


# ============================================================
# JOUEUR
# ============================================================

class Player:
    def __init__(self):
        self.base_image = load_player_image()
        self.reset()

    def reset(self):
        self.col = COLS // 4
        self.row = ROWS // 2
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.trail = []
        self.trail_set = set()
        self.last_move = pygame.time.get_ticks()

    @property
    def position(self):
        return self.col, self.row

    def request_direction(self, direction):
        opposite = (-self.direction[0], -self.direction[1])

        if direction != opposite:
            self.next_direction = direction

    def move(self, now):
        if now - self.last_move < PLAYER_DELAY:
            return False

        self.last_move = now
        self.direction = self.next_direction
        self.col += self.direction[0]
        self.row += self.direction[1]
        return True

    def add_trail(self):
        if self.position not in self.trail_set:
            self.trail.append(self.position)
            self.trail_set.add(self.position)

    def clear_trail(self):
        self.trail.clear()
        self.trail_set.clear()

    def draw(self, screen):
        angles = {
            (1, 0): 0,
            (0, -1): 90,
            (-1, 0): 180,
            (0, 1): 270,
        }

        image = pygame.transform.rotate(
            self.base_image,
            angles.get(self.direction, 0)
        )

        rect = image.get_rect(
            center=(
                self.col * CELL_SIZE + CELL_SIZE // 2,
                self.row * CELL_SIZE + CELL_SIZE // 2,
            )
        )
        screen.blit(image, rect)


# ============================================================
# ENNEMI
# ============================================================

class Enemy:
    def __init__(self):
        self.reset()

    def reset(self):
        self.col = COLS * 3 // 4
        self.row = ROWS // 2
        self.direction = (-1, 0)
        self.trail = []
        self.trail_set = set()
        self.steps = random.randint(5, 12)
        self.last_move = pygame.time.get_ticks()

    @property
    def position(self):
        return self.col, self.row

    def choose_direction(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        opposite = (-self.direction[0], -self.direction[1])

        valid = []

        for direction in directions:
            if direction == opposite:
                continue

            col = self.col + direction[0]
            row = self.row + direction[1]

            if 1 <= col < COLS - 1 and 1 <= row < ROWS - 1:
                valid.append(direction)

        if valid:
            self.direction = random.choice(valid)

        self.steps = random.randint(5, 12)

    def move(self, now):
        if now - self.last_move < ENEMY_DELAY:
            return False

        self.last_move = now

        if self.steps <= 0 or random.random() < 0.06:
            self.choose_direction()

        next_col = self.col + self.direction[0]
        next_row = self.row + self.direction[1]

        if not (0 <= next_col < COLS and 0 <= next_row < ROWS):
            self.choose_direction()
            next_col = self.col + self.direction[0]
            next_row = self.row + self.direction[1]

        self.col = max(0, min(COLS - 1, next_col))
        self.row = max(0, min(ROWS - 1, next_row))
        self.steps -= 1
        return True

    def add_trail(self):
        if self.position not in self.trail_set:
            self.trail.append(self.position)
            self.trail_set.add(self.position)

    def clear_trail(self):
        self.trail.clear()
        self.trail_set.clear()

    def draw(self, screen):
        rect = pygame.Rect(
            self.col * CELL_SIZE + 2,
            self.row * CELL_SIZE + 2,
            CELL_SIZE - 4,
            CELL_SIZE - 4,
        )
        pygame.draw.rect(screen, ENEMY_COLOR, rect, border_radius=5)
        pygame.draw.circle(screen, WHITE, (rect.centerx + 4, rect.top + 5), 2)


# ============================================================
# JEU
# ============================================================

class Game:
    def __init__(self):
        pygame.init()

        try:
            pygame.mixer.init()
        except pygame.error as error:
            print("Audio désactivé :", error)

        pygame.display.set_caption("Paper Zone")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font(None, 90)
        self.large_font = pygame.font.Font(None, 68)
        self.button_font = pygame.font.Font(None, 40)
        self.medium_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 23)

        self.menu_background = load_scaled_image(
            MENU_BACKGROUND,
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            fallback_seed=11,
        )

        self.game_background = AnimatedBackground(
            GAME_BACKGROUND,
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            seed=22,
        )

        self.audio = AudioManager()
        self.player = Player()
        self.enemy = Enemy()

        self.highscore = load_highscore()
        self.score = 0
        self.state = "menu"
        self.running = True

        self.menu_selection = 0
        self.game_over_selection = 0

        self.play_button = Button(
            "JOUER", (SCREEN_WIDTH // 2, 390), (310, 70), self.button_font
        )
        self.quit_button = Button(
            "QUITTER", (SCREEN_WIDTH // 2, 480), (310, 70), self.button_font
        )

        self.restart_button = Button(
            "RECOMMENCER", (SCREEN_WIDTH // 2, 370), (350, 62), self.button_font
        )
        self.back_menu_button = Button(
            "MENU PRINCIPAL", (SCREEN_WIDTH // 2, 450), (350, 62), self.button_font
        )
        self.end_quit_button = Button(
            "QUITTER", (SCREEN_WIDTH // 2, 530), (350, 62), self.button_font
        )

        self.reset_game()
        self.audio.play_music(MENU_MUSIC)

    def reset_game(self):
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

        self.player.reset()
        self.enemy.reset()

        self.create_initial_zone(
            self.player.col, self.player.row, PLAYER_ZONE
        )
        self.create_initial_zone(
            self.enemy.col, self.enemy.row, ENEMY_ZONE
        )

        self.update_score()

    def create_initial_zone(self, center_col, center_row, owner):
        for row in range(center_row - 3, center_row + 4):
            for col in range(center_col - 3, center_col + 4):
                if 0 <= col < COLS and 0 <= row < ROWS:
                    self.grid[row][col] = owner

    def update_score(self):
        self.score = sum(row.count(PLAYER_ZONE) for row in self.grid)

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def find_outside_cells(self):
        visited = set()
        queue = deque()

        def add(col, row):
            if (
                0 <= col < COLS
                and 0 <= row < ROWS
                and (col, row) not in visited
                and self.grid[row][col] != PLAYER_ZONE
            ):
                visited.add((col, row))
                queue.append((col, row))

        for col in range(COLS):
            add(col, 0)
            add(col, ROWS - 1)

        for row in range(ROWS):
            add(0, row)
            add(COLS - 1, row)

        while queue:
            col, row = queue.popleft()
            add(col + 1, row)
            add(col - 1, row)
            add(col, row + 1)
            add(col, row - 1)

        return visited

    def capture_player_area(self):
        for col, row in self.player.trail:
            self.grid[row][col] = PLAYER_ZONE

        outside = self.find_outside_cells()

        for row in range(ROWS):
            for col in range(COLS):
                if (
                    self.grid[row][col] != PLAYER_ZONE
                    and (col, row) not in outside
                ):
                    self.grid[row][col] = PLAYER_ZONE

        self.player.clear_trail()
        self.update_score()
        self.audio.play_sound(self.audio.capture_sound)

    def capture_enemy_area(self):
        for col, row in self.enemy.trail:
            if 0 <= col < COLS and 0 <= row < ROWS:
                self.grid[row][col] = ENEMY_ZONE

        self.enemy.clear_trail()
        self.update_score()

    def update_player(self):
        if not self.player.move(pygame.time.get_ticks()):
            return

        col, row = self.player.position

        if not (0 <= col < COLS and 0 <= row < ROWS):
            self.end_game()
            return

        if self.player.position == self.enemy.position:
            self.end_game()
            return

        if self.player.position in self.enemy.trail_set:
            self.enemy.reset()
            return

        if self.grid[row][col] == PLAYER_ZONE:
            if self.player.trail:
                self.capture_player_area()
        else:
            if self.player.position in self.player.trail_set:
                self.end_game()
                return

            self.player.add_trail()

    def update_enemy(self):
        if not self.enemy.move(pygame.time.get_ticks()):
            return

        col, row = self.enemy.position

        if self.enemy.position == self.player.position:
            self.end_game()
            return

        if self.enemy.position in self.player.trail_set:
            self.end_game()
            return

        if self.enemy.position in self.enemy.trail_set:
            self.enemy.clear_trail()
            self.enemy.reset()
            return

        if self.grid[row][col] == ENEMY_ZONE:
            if self.enemy.trail:
                self.capture_enemy_area()
        else:
            self.enemy.add_trail()

    def end_game(self):
        self.update_score()
        self.state = "game_over"
        self.game_over_selection = 0
        pygame.mixer.music.stop()
        self.audio.play_sound(self.audio.game_over_sound)

    def start_game(self):
        self.reset_game()
        self.state = "playing"
        self.audio.play_music(GAME_MUSIC, force=True)

    def return_to_menu(self):
        self.state = "menu"
        self.menu_selection = 0
        self.audio.play_music(MENU_MUSIC, force=True)

    def handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_z, pygame.K_s):
                self.menu_selection = 1 - self.menu_selection
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.menu_selection == 0:
                    self.start_game()
                else:
                    self.running = False
            elif event.key == pygame.K_m:
                self.audio.toggle()
            elif event.key == pygame.K_ESCAPE:
                self.running = False

        if self.play_button.clicked(event):
            self.start_game()
        elif self.quit_button.clicked(event):
            self.running = False

    def handle_playing_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_z, pygame.K_w):
            self.player.request_direction((0, -1))
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.player.request_direction((0, 1))
        elif event.key in (pygame.K_LEFT, pygame.K_q, pygame.K_a):
            self.player.request_direction((-1, 0))
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player.request_direction((1, 0))
        elif event.key == pygame.K_m:
            self.audio.toggle()
        elif event.key == pygame.K_ESCAPE:
            self.return_to_menu()

    def handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_z, pygame.K_w):
                self.game_over_selection = (self.game_over_selection - 1) % 3
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.game_over_selection = (self.game_over_selection + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.game_over_selection == 0:
                    self.start_game()
                elif self.game_over_selection == 1:
                    self.return_to_menu()
                else:
                    self.running = False
            elif event.key == pygame.K_m:
                self.audio.toggle()
            elif event.key == pygame.K_ESCAPE:
                self.return_to_menu()

        if self.restart_button.clicked(event):
            self.start_game()
        elif self.back_menu_button.clicked(event):
            self.return_to_menu()
        elif self.end_quit_button.clicked(event):
            self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == "menu":
                self.handle_menu_event(event)
            elif self.state == "playing":
                self.handle_playing_event(event)
            elif self.state == "game_over":
                self.handle_game_over_event(event)

    def update(self, dt):
        mouse = pygame.mouse.get_pos()

        if self.state == "menu":
            self.play_button.update(mouse)
            self.quit_button.update(mouse)
            self.play_button.selected = self.menu_selection == 0
            self.quit_button.selected = self.menu_selection == 1

        elif self.state == "playing":
            self.game_background.update(dt)
            self.update_player()

            if self.state == "playing":
                self.update_enemy()

        elif self.state == "game_over":
            self.restart_button.update(mouse)
            self.back_menu_button.update(mouse)
            self.end_quit_button.update(mouse)

            self.restart_button.selected = self.game_over_selection == 0
            self.back_menu_button.selected = self.game_over_selection == 1
            self.end_quit_button.selected = self.game_over_selection == 2

    def draw_menu(self):
        self.screen.blit(self.menu_background, (0, 0))

        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((5, 10, 25, 145))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAPER ZONE", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 145))
        self.screen.blit(title, title_rect)

        subtitle = self.medium_font.render(
            "Capture le plus grand territoire !", True, WHITE
        )
        self.screen.blit(
            subtitle,
            subtitle.get_rect(center=(SCREEN_WIDTH // 2, 230)),
        )

        best = self.medium_font.render(
            f"Meilleur score : {self.highscore}", True, (255, 225, 120)
        )
        self.screen.blit(
            best,
            best.get_rect(center=(SCREEN_WIDTH // 2, 285)),
        )

        self.play_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        sound_state = "activé" if self.audio.enabled else "désactivé"
        help_text = self.small_font.render(
            f"Souris ou clavier — M : son {sound_state}",
            True,
            WHITE,
        )
        self.screen.blit(
            help_text,
            help_text.get_rect(center=(SCREEN_WIDTH // 2, 610)),
        )

    def draw_world(self):
        self.game_background.draw(self.screen)

        shade = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        shade.fill((5, 10, 20, 115))
        self.screen.blit(shade, (0, 0))

        for row in range(ROWS):
            for col in range(COLS):
                value = self.grid[row][col]

                if value == EMPTY:
                    continue

                color = (
                    PLAYER_ZONE_COLOR
                    if value == PLAYER_ZONE
                    else ENEMY_ZONE_COLOR
                )

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        col * CELL_SIZE,
                        row * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    ),
                )

        for col, row in self.player.trail:
            pygame.draw.rect(
                self.screen,
                PLAYER_TRAIL_COLOR,
                (
                    col * CELL_SIZE + 3,
                    row * CELL_SIZE + 3,
                    CELL_SIZE - 6,
                    CELL_SIZE - 6,
                ),
                border_radius=3,
            )

        for col, row in self.enemy.trail:
            pygame.draw.rect(
                self.screen,
                ENEMY_TRAIL_COLOR,
                (
                    col * CELL_SIZE + 3,
                    row * CELL_SIZE + 3,
                    CELL_SIZE - 6,
                    CELL_SIZE - 6,
                ),
                border_radius=3,
            )

        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

    def draw_hud(self):
        bar = pygame.Surface((SCREEN_WIDTH, 52), pygame.SRCALPHA)
        bar.fill((5, 10, 25, 205))
        self.screen.blit(bar, (0, 0))

        score = self.medium_font.render(
            f"Score : {self.score}", True, WHITE
        )
        best = self.medium_font.render(
            f"Meilleur : {self.highscore}", True, WHITE
        )
        sound = self.small_font.render(
            "M : son | Échap : menu", True, WHITE
        )

        self.screen.blit(score, (18, 12))
        self.screen.blit(
            best,
            best.get_rect(midtop=(SCREEN_WIDTH // 2, 12)),
        )
        self.screen.blit(
            sound,
            sound.get_rect(topright=(SCREEN_WIDTH - 18, 16)),
        )

    def draw_game_over(self):
        self.draw_world()
        self.draw_hud()

        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((5, 5, 15, 215))
        self.screen.blit(overlay, (0, 0))

        title = self.large_font.render(
            "GAME OVER", True, (255, 90, 105)
        )
        score = self.medium_font.render(
            f"Score final : {self.score}", True, WHITE
        )
        best = self.medium_font.render(
            f"Meilleur score : {self.highscore}",
            True,
            (255, 225, 120),
        )

        self.screen.blit(
            title,
            title.get_rect(center=(SCREEN_WIDTH // 2, 120)),
        )
        self.screen.blit(
            score,
            score.get_rect(center=(SCREEN_WIDTH // 2, 205)),
        )
        self.screen.blit(
            best,
            best.get_rect(center=(SCREEN_WIDTH // 2, 245)),
        )

        self.restart_button.draw(self.screen)
        self.back_menu_button.draw(self.screen)
        self.end_quit_button.draw(self.screen)

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_world()
            self.draw_hud()
        else:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
