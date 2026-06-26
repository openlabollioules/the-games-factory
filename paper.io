import json
import os
import random
import sys
from collections import deque

import pygame


# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

CELL_SIZE = 20

WORLD_COLS = SCREEN_WIDTH // CELL_SIZE
WORLD_ROWS = SCREEN_HEIGHT // CELL_SIZE

PLAYER_MOVE_DELAY = 75
ENEMY_MOVE_DELAY = 105

ASSETS_FOLDER = "assets"
BACKGROUND_PATH = os.path.join(ASSETS_FOLDER, "background.png")
HIGHSCORE_PATH = "highscore.json"

# États possibles d'une case
EMPTY = 0
PLAYER_TERRITORY = 1
ENEMY_TERRITORY = 2

# Couleurs
WHITE = (245, 245, 245)
BLACK = (15, 15, 20)
DARK_BLUE = (20, 30, 55)
LIGHT_BLUE = (60, 170, 255)
PLAYER_COLOR = (40, 150, 255)
PLAYER_TRAIL_COLOR = (120, 215, 255)
PLAYER_TERRITORY_COLOR = (35, 105, 190)

ENEMY_COLOR = (255, 75, 90)
ENEMY_TRAIL_COLOR = (255, 145, 155)
ENEMY_TERRITORY_COLOR = (175, 45, 60)

BUTTON_COLOR = (35, 55, 95)
BUTTON_HOVER_COLOR = (55, 105, 175)
BUTTON_SELECTED_COLOR = (45, 130, 215)

GRID_COLOR = (255, 255, 255, 20)
OVERLAY_COLOR = (10, 15, 30, 175)


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def clamp(value, minimum, maximum):
    """Limite une valeur entre un minimum et un maximum."""
    return max(minimum, min(value, maximum))


def load_highscore():
    """Charge le meilleur score depuis un fichier JSON."""
    try:
        with open(HIGHSCORE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return int(data.get("highscore", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        return 0


def save_highscore(score):
    """Sauvegarde le meilleur score."""
    try:
        with open(HIGHSCORE_PATH, "w", encoding="utf-8") as file:
            json.dump({"highscore": score}, file, indent=4)
    except OSError as error:
        print("Impossible de sauvegarder le meilleur score :", error)


def create_fallback_background(size):
    """
    Crée un arrière-plan de remplacement si l'image personnalisée
    est absente ou impossible à charger.
    """
    width, height = size
    surface = pygame.Surface(size)

    for y in range(height):
        ratio = y / max(1, height - 1)

        red = int(15 + 20 * ratio)
        green = int(25 + 35 * ratio)
        blue = int(55 + 65 * ratio)

        pygame.draw.line(
            surface,
            (red, green, blue),
            (0, y),
            (width, y)
        )

    # Ajout de formes décoratives
    random_generator = random.Random(42)

    for _ in range(50):
        x = random_generator.randint(0, width)
        y = random_generator.randint(0, height)
        radius = random_generator.randint(10, 70)

        decoration = pygame.Surface(
            (radius * 2, radius * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            decoration,
            (
                random_generator.randint(70, 130),
                random_generator.randint(100, 180),
                random_generator.randint(180, 255),
                random_generator.randint(15, 45),
            ),
            (radius, radius),
            radius
        )

        surface.blit(decoration, (x - radius, y - radius))

    return surface


def load_background(size):
    """Charge et redimensionne l'image d'arrière-plan."""
    try:
        image = pygame.image.load(BACKGROUND_PATH).convert()
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError, OSError) as error:
        print(
            f"Impossible de charger '{BACKGROUND_PATH}'. "
            f"Utilisation du fond de remplacement."
        )
        print("Détail :", error)

        return create_fallback_background(size)


# ============================================================
# ARRIÈRE-PLAN ANIMÉ
# ============================================================

class AnimatedBackground:
    def __init__(self, size):
        self.width, self.height = size
        self.image = load_background(size)

        self.offset_x = 0.0
        self.offset_y = 0.0

        self.speed_x = 18
        self.speed_y = 9

    def update(self, delta_time):
        """Déplace progressivement l'arrière-plan."""
        self.offset_x += self.speed_x * delta_time
        self.offset_y += self.speed_y * delta_time

        self.offset_x %= self.width
        self.offset_y %= self.height

    def draw(self, screen):
        """
        Dessine plusieurs copies de l'image pour produire
        un déplacement continu sans zone vide.
        """
        x = int(self.offset_x)
        y = int(self.offset_y)

        positions = [
            (-x, -y),
            (self.width - x, -y),
            (-x, self.height - y),
            (self.width - x, self.height - y),
        ]

        for position in positions:
            screen.blit(self.image, position)


# ============================================================
# BOUTONS
# ============================================================

class Button:
    def __init__(self, text, center, size, font):
        self.text = text
        self.font = font

        width, height = size

        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = center

        self.hovered = False
        self.selected = False

    def update(self, mouse_position):
        self.hovered = self.rect.collidepoint(mouse_position)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, screen):
        if self.selected:
            color = BUTTON_SELECTED_COLOR
        elif self.hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        shadow_rect = self.rect.move(0, 6)

        pygame.draw.rect(
            screen,
            (8, 12, 25),
            shadow_rect,
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            WHITE,
            self.rect,
            width=2,
            border_radius=15
        )

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)

        screen.blit(text_surface, text_rect)


# ============================================================
# JOUEUR
# ============================================================

class Player:
    def __init__(self):
        self.col = WORLD_COLS // 4
        self.row = WORLD_ROWS // 2

        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.trail = []
        self.trail_set = set()

        self.last_move = 0

    @property
    def position(self):
        return self.col, self.row

    def reset(self):
        self.col = WORLD_COLS // 4
        self.row = WORLD_ROWS // 2

        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.trail.clear()
        self.trail_set.clear()

        self.last_move = pygame.time.get_ticks()

    def request_direction(self, direction):
        """
        Change la direction demandée.

        Le joueur ne peut pas effectuer immédiatement un demi-tour.
        """
        opposite = (-self.direction[0], -self.direction[1])

        if direction != opposite:
            self.next_direction = direction

    def move(self, current_time):
        """
        Déplace le joueur sur la grille.

        Retourne True si un déplacement a été effectué.
        """
        if current_time - self.last_move < PLAYER_MOVE_DELAY:
            return False

        self.last_move = current_time
        self.direction = self.next_direction

        self.col += self.direction[0]
        self.row += self.direction[1]

        return True

    def add_trail_position(self, position):
        if position not in self.trail_set:
            self.trail.append(position)
            self.trail_set.add(position)

    def clear_trail(self):
        self.trail.clear()
        self.trail_set.clear()

    def draw(self, screen):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE

        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        inner_rect = rect.inflate(-5, -5)

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
            border_radius=5
        )

        pygame.draw.rect(
            screen,
            PLAYER_COLOR,
            inner_rect,
            border_radius=4
        )


# ============================================================
# ENNEMI
# ============================================================

class Enemy:
    def __init__(self):
        self.col = WORLD_COLS * 3 // 4
        self.row = WORLD_ROWS // 2

        self.direction = (-1, 0)

        self.trail = []
        self.trail_set = set()

        self.last_move = 0
        self.steps_before_turn = random.randint(4, 10)

    @property
    def position(self):
        return self.col, self.row

    def reset(self):
        self.col = WORLD_COLS * 3 // 4
        self.row = WORLD_ROWS // 2

        self.direction = random.choice(
            [(-1, 0), (0, -1), (0, 1)]
        )

        self.trail.clear()
        self.trail_set.clear()

        self.steps_before_turn = random.randint(4, 10)
        self.last_move = pygame.time.get_ticks()

    def choose_direction(self):
        """Choisit une nouvelle direction sans demi-tour direct."""
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]

        opposite = (-self.direction[0], -self.direction[1])

        possible_directions = [
            direction
            for direction in directions
            if direction != opposite
        ]

        # Évite les bords lorsque cela est possible.
        safe_directions = []

        for direction in possible_directions:
            next_col = self.col + direction[0]
            next_row = self.row + direction[1]

            if (
                1 <= next_col < WORLD_COLS - 1
                and 1 <= next_row < WORLD_ROWS - 1
            ):
                safe_directions.append(direction)

        if safe_directions:
            self.direction = random.choice(safe_directions)
        else:
            self.direction = random.choice(possible_directions)

        self.steps_before_turn = random.randint(4, 12)

    def move(self, current_time):
        if current_time - self.last_move < ENEMY_MOVE_DELAY:
            return False

        self.last_move = current_time

        if self.steps_before_turn <= 0 or random.random() < 0.08:
            self.choose_direction()

        next_col = self.col + self.direction[0]
        next_row = self.row + self.direction[1]

        if not (
            0 <= next_col < WORLD_COLS
            and 0 <= next_row < WORLD_ROWS
        ):
            self.choose_direction()

            next_col = self.col + self.direction[0]
            next_row = self.row + self.direction[1]

        self.col = clamp(next_col, 0, WORLD_COLS - 1)
        self.row = clamp(next_row, 0, WORLD_ROWS - 1)

        self.steps_before_turn -= 1

        return True

    def add_trail_position(self, position):
        if position not in self.trail_set:
            self.trail.append(position)
            self.trail_set.add(position)

    def clear_trail(self):
        self.trail.clear()
        self.trail_set.clear()

    def draw(self, screen):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE

        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        inner_rect = rect.inflate(-5, -5)

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
            border_radius=5
        )

        pygame.draw.rect(
            screen,
            ENEMY_COLOR,
            inner_rect,
            border_radius=4
        )


# ============================================================
# PARTIE
# ============================================================

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Paper Zone")

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font(None, 92)
        self.large_font = pygame.font.Font(None, 68)
        self.button_font = pygame.font.Font(None, 42)
        self.medium_font = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 25)

        self.background = AnimatedBackground(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        self.player = Player()
        self.enemy = Enemy()

        self.grid = []

        self.score = 0
        self.highscore = load_highscore()

        self.running = True
        self.state = "menu"

        self.menu_selection = 0
        self.game_over_selection = 0

        self.create_buttons()
        self.reset_game()

    def create_buttons(self):
        center_x = SCREEN_WIDTH // 2

        self.play_button = Button(
            "JOUER",
            (center_x, 390),
            (300, 70),
            self.button_font
        )

        self.quit_button = Button(
            "QUITTER",
            (center_x, 490),
            (300, 70),
            self.button_font
        )

        self.restart_button = Button(
            "RECOMMENCER",
            (center_x, 385),
            (340, 62),
            self.button_font
        )

        self.menu_button = Button(
            "MENU PRINCIPAL",
            (center_x, 465),
            (340, 62),
            self.button_font
        )

        self.game_over_quit_button = Button(
            "QUITTER",
            (center_x, 545),
            (340, 62),
            self.button_font
        )

    # --------------------------------------------------------
    # INITIALISATION DE LA PARTIE
    # --------------------------------------------------------

    def reset_game(self):
        self.grid = [
            [EMPTY for _ in range(WORLD_COLS)]
            for _ in range(WORLD_ROWS)
        ]

        self.player.reset()
        self.enemy.reset()

        self.create_initial_territory(
            self.player.col,
            self.player.row,
            PLAYER_TERRITORY
        )

        self.create_initial_territory(
            self.enemy.col,
            self.enemy.row,
            ENEMY_TERRITORY
        )

        self.update_score()

    def create_initial_territory(self, center_col, center_row, owner):
        """Crée un territoire carré de 7 cases sur 7."""
        radius = 3

        for row in range(center_row - radius, center_row + radius + 1):
            for col in range(center_col - radius, center_col + radius + 1):
                if (
                    0 <= col < WORLD_COLS
                    and 0 <= row < WORLD_ROWS
                ):
                    self.grid[row][col] = owner

    # --------------------------------------------------------
    # GESTION DU SCORE
    # --------------------------------------------------------

    def update_score(self):
        territory_cells = 0

        for row in self.grid:
            territory_cells += row.count(PLAYER_TERRITORY)

        self.score = territory_cells

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    # --------------------------------------------------------
    # CAPTURE DU TERRITOIRE
    # --------------------------------------------------------

    def capture_player_area(self):
        """
        Transforme la traînée du joueur en territoire, puis capture
        toutes les cases qui ne sont plus reliées au bord de la carte.
        """
        if not self.player.trail:
            return

        for col, row in self.player.trail:
            if 0 <= col < WORLD_COLS and 0 <= row < WORLD_ROWS:
                self.grid[row][col] = PLAYER_TERRITORY

        outside = self.find_outside_cells(PLAYER_TERRITORY)

        for row in range(WORLD_ROWS):
            for col in range(WORLD_COLS):
                if (
                    self.grid[row][col] != PLAYER_TERRITORY
                    and (col, row) not in outside
                ):
                    self.grid[row][col] = PLAYER_TERRITORY

        self.player.clear_trail()
        self.update_score()

    def capture_enemy_area(self):
        """
        Capture simplifiée pour l'ennemi.

        Sa traînée devient son territoire lorsqu'il rejoint une case
        qu'il possédait déjà.
        """
        for col, row in self.enemy.trail:
            if 0 <= col < WORLD_COLS and 0 <= row < WORLD_ROWS:
                self.grid[row][col] = ENEMY_TERRITORY

        self.enemy.clear_trail()
        self.update_score()

    def find_outside_cells(self, blocked_owner):
        """
        Recherche les cases encore accessibles depuis les bords.

        Les cases appartenant au joueur servent de mur. Les cases non
        accessibles depuis l'extérieur sont considérées comme entourées.
        """
        visited = set()
        queue = deque()

        def add_cell(col, row):
            if (
                0 <= col < WORLD_COLS
                and 0 <= row < WORLD_ROWS
                and (col, row) not in visited
                and self.grid[row][col] != blocked_owner
            ):
                visited.add((col, row))
                queue.append((col, row))

        for col in range(WORLD_COLS):
            add_cell(col, 0)
            add_cell(col, WORLD_ROWS - 1)

        for row in range(WORLD_ROWS):
            add_cell(0, row)
            add_cell(WORLD_COLS - 1, row)

        while queue:
            col, row = queue.popleft()

            add_cell(col + 1, row)
            add_cell(col - 1, row)
            add_cell(col, row + 1)
            add_cell(col, row - 1)

        return visited

    # --------------------------------------------------------
    # LOGIQUE DU JOUEUR
    # --------------------------------------------------------

    def update_player(self):
        current_time = pygame.time.get_ticks()

        if not self.player.move(current_time):
            return

        col, row = self.player.position

        # Sortie des limites
        if not (
            0 <= col < WORLD_COLS
            and 0 <= row < WORLD_ROWS
        ):
            self.end_game()
            return

        current_cell = self.grid[row][col]

        # Collision avec l'ennemi
        if self.player.position == self.enemy.position:
            self.end_game()
            return

        # Collision avec la traînée ennemie
        if self.player.position in self.enemy.trail_set:
            self.end_game()
            return

        if current_cell == PLAYER_TERRITORY:
            # Retour sur son territoire : capture.
            if self.player.trail:
                self.capture_player_area()
        else:
            # Collision avec sa propre traînée.
            if self.player.position in self.player.trail_set:
                self.end_game()
                return

            self.player.add_trail_position(self.player.position)

    # --------------------------------------------------------
    # LOGIQUE DE L'ENNEMI
    # --------------------------------------------------------

    def update_enemy(self):
        current_time = pygame.time.get_ticks()

        if not self.enemy.move(current_time):
            return

        col, row = self.enemy.position

        if not (
            0 <= col < WORLD_COLS
            and 0 <= row < WORLD_ROWS
        ):
            self.enemy.reset()
            return

        current_cell = self.grid[row][col]

        # L'ennemi touche le joueur.
        if self.enemy.position == self.player.position:
            self.end_game()
            return

        # L'ennemi coupe la traînée du joueur.
        if self.enemy.position in self.player.trail_set:
            self.end_game()
            return

        # L'ennemi touche sa propre traînée.
        if self.enemy.position in self.enemy.trail_set:
            self.reset_enemy_after_collision()
            return

        if current_cell == ENEMY_TERRITORY:
            if self.enemy.trail:
                self.capture_enemy_area()
        else:
            self.enemy.add_trail_position(self.enemy.position)

    def reset_enemy_after_collision(self):
        """
        Réinitialise l'ennemi après une collision avec sa propre traînée.
        """
        for col, row in self.enemy.trail:
            if (
                0 <= col < WORLD_COLS
                and 0 <= row < WORLD_ROWS
                and self.grid[row][col] == EMPTY
            ):
                self.grid[row][col] = EMPTY

        self.enemy.reset()

    # --------------------------------------------------------
    # FIN DE PARTIE
    # --------------------------------------------------------

    def end_game(self):
        self.update_score()

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

        self.game_over_selection = 0
        self.state = "game_over"

    # --------------------------------------------------------
    # ÉVÉNEMENTS DU MENU
    # --------------------------------------------------------

    def handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_w,
                pygame.K_s,
                pygame.K_z,
            ):
                self.menu_selection = 1 - self.menu_selection

            elif event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE,
            ):
                if self.menu_selection == 0:
                    self.reset_game()
                    self.state = "playing"
                else:
                    self.running = False

            elif event.key == pygame.K_ESCAPE:
                self.running = False

        if self.play_button.is_clicked(event):
            self.reset_game()
            self.state = "playing"

        if self.quit_button.is_clicked(event):
            self.running = False

    # --------------------------------------------------------
    # ÉVÉNEMENTS EN JEU
    # --------------------------------------------------------

    def handle_playing_events(self, event):
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

        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"
            self.menu_selection = 0

    # --------------------------------------------------------
    # ÉVÉNEMENTS DE L'ÉCRAN GAME OVER
    # --------------------------------------------------------

    def handle_game_over_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_UP,
                pygame.K_w,
                pygame.K_z,
            ):
                self.game_over_selection -= 1
                self.game_over_selection %= 3

            elif event.key in (
                pygame.K_DOWN,
                pygame.K_s,
            ):
                self.game_over_selection += 1
                self.game_over_selection %= 3

            elif event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE,
            ):
                if self.game_over_selection == 0:
                    self.reset_game()
                    self.state = "playing"

                elif self.game_over_selection == 1:
                    self.state = "menu"
                    self.menu_selection = 0

                else:
                    self.running = False

            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"

        if self.restart_button.is_clicked(event):
            self.reset_game()
            self.state = "playing"

        if self.menu_button.is_clicked(event):
            self.state = "menu"
            self.menu_selection = 0

        if self.game_over_quit_button.is_clicked(event):
            self.running = False

    # --------------------------------------------------------
    # GESTION GLOBALE DES ÉVÉNEMENTS
    # --------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.state == "menu":
                self.handle_menu_events(event)

            elif self.state == "playing":
                self.handle_playing_events(event)

            elif self.state == "game_over":
                self.handle_game_over_events(event)

    # --------------------------------------------------------
    # MISE À JOUR
    # --------------------------------------------------------

    def update(self, delta_time):
        self.background.update(delta_time)

        mouse_position = pygame.mouse.get_pos()

        if self.state == "menu":
            self.play_button.update(mouse_position)
            self.quit_button.update(mouse_position)

            self.play_button.selected = self.menu_selection == 0
            self.quit_button.selected = self.menu_selection == 1

        elif self.state == "playing":
            self.update_player()

            if self.state == "playing":
                self.update_enemy()

        elif self.state == "game_over":
            self.restart_button.update(mouse_position)
            self.menu_button.update(mouse_position)
            self.game_over_quit_button.update(mouse_position)

            self.restart_button.selected = (
                self.game_over_selection == 0
            )

            self.menu_button.selected = (
                self.game_over_selection == 1
            )

            self.game_over_quit_button.selected = (
                self.game_over_selection == 2
            )

    # --------------------------------------------------------
    # AFFICHAGE DU TERRITOIRE
    # --------------------------------------------------------

    def draw_world(self):
        board_overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        board_overlay.fill((5, 10, 20, 105))
        self.screen.blit(board_overlay, (0, 0))

        for row in range(WORLD_ROWS):
            for col in range(WORLD_COLS):
                value = self.grid[row][col]

                if value == EMPTY:
                    continue

                rect = pygame.Rect(
                    col * CELL_SIZE,
                    row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                if value == PLAYER_TERRITORY:
                    color = PLAYER_TERRITORY_COLOR
                else:
                    color = ENEMY_TERRITORY_COLOR

                pygame.draw.rect(self.screen, color, rect)

        # Traînée du joueur
        for col, row in self.player.trail:
            rect = pygame.Rect(
                col * CELL_SIZE + 3,
                row * CELL_SIZE + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )

            pygame.draw.rect(
                self.screen,
                PLAYER_TRAIL_COLOR,
                rect,
                border_radius=3
            )

        # Traînée ennemie
        for col, row in self.enemy.trail:
            rect = pygame.Rect(
                col * CELL_SIZE + 3,
                row * CELL_SIZE + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )

            pygame.draw.rect(
                self.screen,
                ENEMY_TRAIL_COLOR,
                rect,
                border_radius=3
            )

        self.draw_grid()
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

    def draw_grid(self):
        grid_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(
                grid_surface,
                GRID_COLOR,
                (x, 0),
                (x, SCREEN_HEIGHT)
            )

        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(
                grid_surface,
                GRID_COLOR,
                (0, y),
                (SCREEN_WIDTH, y)
            )

        self.screen.blit(grid_surface, (0, 0))

    # --------------------------------------------------------
    # INTERFACE EN JEU
    # --------------------------------------------------------

    def draw_hud(self):
        hud_surface = pygame.Surface(
            (SCREEN_WIDTH, 55),
            pygame.SRCALPHA
        )

        hud_surface.fill((5, 10, 25, 190))
        self.screen.blit(hud_surface, (0, 0))

        score_text = self.medium_font.render(
            f"Score : {self.score}",
            True,
            WHITE
        )

        highscore_text = self.medium_font.render(
            f"Meilleur : {self.highscore}",
            True,
            WHITE
        )

        controls_text = self.small_font.render(
            "Flèches / ZQSD / WASD — Échap : menu",
            True,
            (210, 220, 235)
        )

        self.screen.blit(score_text, (20, 13))

        highscore_rect = highscore_text.get_rect(
            midtop=(SCREEN_WIDTH // 2, 13)
        )
        self.screen.blit(highscore_text, highscore_rect)

        controls_rect = controls_text.get_rect(
            topright=(SCREEN_WIDTH - 20, 17)
        )
        self.screen.blit(controls_text, controls_rect)

    # --------------------------------------------------------
    # AFFICHAGE DU MENU
    # --------------------------------------------------------

    def draw_menu(self):
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill(OVERLAY_COLOR)

        self.screen.blit(overlay, (0, 0))

        title_shadow = self.title_font.render(
            "PAPER ZONE",
            True,
            BLACK
        )

        title = self.title_font.render(
            "PAPER ZONE",
            True,
            WHITE
        )

        title_rect = title.get_rect(
            center=(SCREEN_WIDTH // 2, 155)
        )

        self.screen.blit(
            title_shadow,
            title_rect.move(5, 6)
        )

        self.screen.blit(title, title_rect)

        subtitle = self.medium_font.render(
            "Capture le plus grand territoire possible",
            True,
            (200, 220, 255)
        )

        subtitle_rect = subtitle.get_rect(
            center=(SCREEN_WIDTH // 2, 235)
        )

        self.screen.blit(subtitle, subtitle_rect)

        highscore_surface = self.medium_font.render(
            f"Meilleur score : {self.highscore}",
            True,
            (255, 225, 120)
        )

        highscore_rect = highscore_surface.get_rect(
            center=(SCREEN_WIDTH // 2, 290)
        )

        self.screen.blit(highscore_surface, highscore_rect)

        self.play_button.draw(self.screen)
        self.quit_button.draw(self.screen)

        help_text = self.small_font.render(
            "Souris ou flèches — Entrée pour sélectionner",
            True,
            (190, 200, 220)
        )

        help_rect = help_text.get_rect(
            center=(SCREEN_WIDTH // 2, 610)
        )

        self.screen.blit(help_text, help_rect)

    # --------------------------------------------------------
    # AFFICHAGE DE L'ÉCRAN GAME OVER
    # --------------------------------------------------------

    def draw_game_over(self):
        # Le terrain reste visible derrière l'écran de fin.
        self.draw_world()
        self.draw_hud()

        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((10, 10, 20, 205))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render(
            "GAME OVER",
            True,
            (255, 90, 100)
        )

        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, 125)
        )

        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.medium_font.render(
            f"Score final : {self.score}",
            True,
            WHITE
        )

        score_rect = score_text.get_rect(
            center=(SCREEN_WIDTH // 2, 205)
        )

        self.screen.blit(score_text, score_rect)

        highscore_text = self.medium_font.render(
            f"Meilleur score : {self.highscore}",
            True,
            (255, 225, 120)
        )

        highscore_rect = highscore_text.get_rect(
            center=(SCREEN_WIDTH // 2, 250)
        )

        self.screen.blit(highscore_text, highscore_rect)

        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        self.game_over_quit_button.draw(self.screen)

    # --------------------------------------------------------
    # AFFICHAGE GÉNÉRAL
    # --------------------------------------------------------

    def draw(self):
        self.background.draw(self.screen)

        if self.state == "menu":
            self.draw_menu()

        elif self.state == "playing":
            self.draw_world()
            self.draw_hud()

        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    # --------------------------------------------------------
    # BOUCLE PRINCIPALE
    # --------------------------------------------------------

    def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    game = Game()
    game.run()