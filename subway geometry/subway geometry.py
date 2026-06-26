import os
import random
import sys

import pygame


# ============================================================
# INITIALISATION
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
except pygame.error as error:
    print(f"Impossible d'initialiser le système audio : {error}")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Subway")

clock = pygame.time.Clock()


# ============================================================
# CHEMINS DES RESSOURCES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def asset_path(filename):
    """
    Retourne le chemin d'un fichier placé directement
    dans le dossier assets.
    """
    return os.path.join(ASSETS_DIR, filename)


# ============================================================
# COULEURS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (50, 130, 220)
DARK_BLUE = (30, 85, 160)
RED = (220, 55, 55)
DARK_RED = (160, 35, 35)
GREEN = (45, 180, 90)
YELLOW = (245, 200, 40)
SKY_BLUE = (100, 180, 230)


# ============================================================
# PARAMÈTRES DU JEU
# ============================================================

GROUND_Y = 500

# Vitesse initiale et augmentation progressive.
INITIAL_GAME_SPEED = 7.0
MAX_GAME_SPEED = 18.0
SPEED_INCREASE_PER_OBSTACLE = 0.35

GRAVITY = 0.9
JUMP_FORCE = -17

MIN_OBSTACLE_DELAY = 1000
MAX_OBSTACLE_DELAY = 1800

MIN_COIN_DELAY = 700
MAX_COIN_DELAY = 1400

OBSTACLE_SCORE_VALUE = 10
COIN_VALUE = 5

PLAYER_NORMAL_SIZE = (75, 100)
PLAYER_DUCK_SIZE = (100, 55)

HURDLE_SIZE = (75, 85)
BIRD_SIZE = (90, 60)
COIN_SIZE = (40, 40)

GAME_OVER_SIZE = (430, 170)


# ============================================================
# CHARGEMENT DES RESSOURCES
# ============================================================

def load_image(filename, size, fallback_color):
    """
    Charge et redimensionne une image située dans assets.

    Une surface colorée est créée si l'image est absente.
    """
    path = asset_path(filename)

    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)

    except (pygame.error, FileNotFoundError) as error:
        print(f"Impossible de charger : {path}")
        print(f"Détail : {error}")

        fallback = pygame.Surface(size, pygame.SRCALPHA)
        fallback.fill(fallback_color)

        pygame.draw.rect(
            fallback,
            BLACK,
            fallback.get_rect(),
            width=3,
            border_radius=8
        )

        return fallback


def load_music(filename):
    """
    Charge la musique depuis assets.
    La musique sera lancée au début d'une partie.
    """
    if not pygame.mixer.get_init():
        return False

    path = asset_path(filename)

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.4)
        return True

    except (pygame.error, FileNotFoundError) as error:
        print(f"Impossible de charger la musique : {path}")
        print(f"Détail : {error}")
        return False


# Arrière-plan réservé au menu.
menu_background_image = load_image(
    "menu_background.png",
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    DARK_BLUE
)

# Arrière-plan réservé à la partie.
game_background_image = load_image(
    "game_background.png",
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    SKY_BLUE
)

player_normal_image = load_image(
    "player.png",
    PLAYER_NORMAL_SIZE,
    BLUE
)

player_duck_image = load_image(
    "player_duck.png",
    PLAYER_DUCK_SIZE,
    DARK_BLUE
)

hurdle_image = load_image(
    "hurdle.png",
    HURDLE_SIZE,
    GREEN
)

bird_image = load_image(
    "bird.png",
    BIRD_SIZE,
    RED
)

coin_image = load_image(
    "coin.png",
    COIN_SIZE,
    YELLOW
)

game_over_image = load_image(
    "game_over.png",
    GAME_OVER_SIZE,
    DARK_RED
)

music_loaded = load_music("music.mp3")


# ============================================================
# POLICES
# ============================================================

font_title = pygame.font.Font(None, 80)
font_button = pygame.font.Font(None, 44)
font_score = pygame.font.Font(None, 38)
font_small = pygame.font.Font(None, 27)


# ============================================================
# MUSIQUE
# ============================================================

def start_music():
    """Lance la musique en boucle pendant la partie."""
    if music_loaded and pygame.mixer.get_init():
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)


def stop_music():
    """Arrête la musique lors du retour au menu."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


# ============================================================
# BOUTON
# ============================================================

class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        normal_color,
        hover_color
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.normal_color = normal_color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_position = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_position)

        color = self.hover_color if hovered else self.normal_color

        pygame.draw.rect(
            surface,
            color,
            self.rect,
            border_radius=15
        )

        pygame.draw.rect(
            surface,
            WHITE,
            self.rect,
            width=3,
            border_radius=15
        )

        text_surface = font_button.render(
            self.text,
            True,
            WHITE
        )

        text_rect = text_surface.get_rect(
            center=self.rect.center
        )

        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ============================================================
# PERSONNAGE
# ============================================================

class Player:
    def __init__(self):
        self.normal_image = player_normal_image
        self.duck_image = player_duck_image

        self.image = self.normal_image

        self.rect = self.image.get_rect()
        self.rect.left = 110
        self.rect.bottom = GROUND_Y

        self.velocity_y = 0

        self.is_jumping = False
        self.is_ducking = False

    def jump(self):
        """Fait sauter le personnage s'il est au sol."""
        if not self.is_jumping:
            self.stop_ducking()

            self.velocity_y = JUMP_FORCE
            self.is_jumping = True

    def duck(self):
        """Accroupit le personnage s'il est au sol."""
        if self.is_jumping or self.is_ducking:
            return

        old_left = self.rect.left
        old_bottom = self.rect.bottom

        self.image = self.duck_image
        self.rect = self.image.get_rect()

        self.rect.left = old_left
        self.rect.bottom = old_bottom

        self.is_ducking = True

    def stop_ducking(self):
        """Remet le personnage debout."""
        if not self.is_ducking:
            return

        old_left = self.rect.left
        old_bottom = self.rect.bottom

        self.image = self.normal_image
        self.rect = self.image.get_rect()

        self.rect.left = old_left
        self.rect.bottom = old_bottom

        self.is_ducking = False

    def update(self, keys):
        wants_to_duck = (
            keys[pygame.K_DOWN]
            or keys[pygame.K_s]
        )

        if wants_to_duck and not self.is_jumping:
            self.duck()
        else:
            self.stop_ducking()

        # Gravité.
        self.velocity_y += GRAVITY
        self.rect.y += round(self.velocity_y)

        # Collision avec le sol.
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.is_jumping = False

    def get_collision_rect(self):
        """
        Retourne une boîte de collision légèrement réduite.
        """
        collision_rect = self.rect.copy()

        collision_rect.inflate_ip(
            -int(self.rect.width * 0.25),
            -int(self.rect.height * 0.15)
        )

        return collision_rect

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ============================================================
# OBSTACLES
# ============================================================

class Obstacle:
    def __init__(self, obstacle_type):
        self.obstacle_type = obstacle_type
        self.has_been_passed = False

        if obstacle_type == "hurdle":
            self.image = hurdle_image
            self.rect = self.image.get_rect()

            self.rect.left = SCREEN_WIDTH + 30
            self.rect.bottom = GROUND_Y

        else:
            self.image = bird_image
            self.rect = self.image.get_rect()

            self.rect.left = SCREEN_WIDTH + 30

            # L'oiseau est suffisamment bas pour toucher
            # le personnage debout, mais pas le personnage accroupi.
            self.rect.bottom = GROUND_Y - 55

    def update(self, speed):
        self.rect.x -= round(speed)

    def is_outside_screen(self):
        return self.rect.right < 0

    def get_collision_rect(self):
        collision_rect = self.rect.copy()

        collision_rect.inflate_ip(
            -int(self.rect.width * 0.20),
            -int(self.rect.height * 0.20)
        )

        return collision_rect

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ============================================================
# PIÈCES
# ============================================================

class Coin:
    def __init__(self, x, y):
        self.image = coin_image
        self.rect = self.image.get_rect()

        self.rect.centerx = x
        self.rect.centery = y

        self.collected = False

    def update(self, speed):
        self.rect.x -= round(speed)

    def is_outside_screen(self):
        return self.rect.right < 0

    def get_collision_rect(self):
        collision_rect = self.rect.copy()
        collision_rect.inflate_ip(-8, -8)
        return collision_rect

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ============================================================
# ARRIÈRE-PLAN DÉFILANT
# ============================================================

class ScrollingBackground:
    def __init__(self, image):
        self.image = image
        self.x1 = 0
        self.x2 = SCREEN_WIDTH

    def reset(self):
        self.x1 = 0
        self.x2 = SCREEN_WIDTH

    def update(self, speed):
        """
        Le fond accélère en même temps que le jeu.

        Sa vitesse est légèrement inférieure à celle des
        obstacles afin de créer un effet de profondeur.
        """
        background_speed = max(2, speed * 0.55)

        self.x1 -= background_speed
        self.x2 -= background_speed

        if self.x1 <= -SCREEN_WIDTH:
            self.x1 = self.x2 + SCREEN_WIDTH

        if self.x2 <= -SCREEN_WIDTH:
            self.x2 = self.x1 + SCREEN_WIDTH

    def draw(self, surface):
        surface.blit(self.image, (round(self.x1), 0))
        surface.blit(self.image, (round(self.x2), 0))


# ============================================================
# OBJETS DU JEU
# ============================================================

game_background = ScrollingBackground(game_background_image)

player = Player()
obstacles = []
coins = []

start_button = Button(
    SCREEN_WIDTH // 2 - 130,
    290,
    260,
    70,
    "JOUER",
    BLUE,
    DARK_BLUE
)

quit_button = Button(
    SCREEN_WIDTH // 2 - 130,
    390,
    260,
    70,
    "QUITTER",
    RED,
    DARK_RED
)


# ============================================================
# ÉTATS DU JEU
# ============================================================

MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU

score = 0
obstacles_passed = 0
game_speed = INITIAL_GAME_SPEED

next_obstacle_time = 0
next_coin_time = 0
game_over_start_time = 0


# ============================================================
# RÉINITIALISATION
# ============================================================

def reset_game():
    """Réinitialise complètement une nouvelle partie."""
    global player
    global obstacles
    global coins
    global score
    global obstacles_passed
    global game_speed
    global next_obstacle_time
    global next_coin_time

    player = Player()

    obstacles = []
    coins = []

    score = 0
    obstacles_passed = 0
    game_speed = INITIAL_GAME_SPEED

    game_background.reset()

    current_time = pygame.time.get_ticks()

    next_obstacle_time = current_time + 1300
    next_coin_time = current_time + 700

    start_music()


# ============================================================
# CRÉATION DES OBSTACLES
# ============================================================

def create_random_obstacle():
    """
    Crée une haie ou un oiseau.

    Les haies doivent être franchies en sautant.
    Les oiseaux doivent être franchis en se baissant.
    """
    obstacle_type = random.choice(["hurdle", "bird"])
    return Obstacle(obstacle_type)


# ============================================================
# CRÉATION DES PIÈCES
# ============================================================

def create_coin_group():
    """
    Crée une ligne de plusieurs pièces.

    Les pièces peuvent être placées au sol ou en hauteur.
    Les pièces en hauteur encouragent le joueur à sauter.
    """
    group = []

    coin_count = random.randint(3, 6)
    start_x = SCREEN_WIDTH + 50
    spacing = 55

    pattern = random.choice([
        "ground",
        "high",
        "arc"
    ])

    for index in range(coin_count):
        x = start_x + index * spacing

        if pattern == "ground":
            y = GROUND_Y - 45

        elif pattern == "high":
            y = GROUND_Y - 145

        else:
            # Forme simple d'arc.
            middle = (coin_count - 1) / 2
            distance_from_middle = abs(index - middle)

            y = int(
                GROUND_Y
                - 145
                + distance_from_middle * 28
            )

        group.append(Coin(x, y))

    return group


# ============================================================
# DIFFICULTÉ PROGRESSIVE
# ============================================================

def increase_game_speed():
    """
    Augmente la vitesse après chaque obstacle dépassé.
    """
    global game_speed

    game_speed = min(
        game_speed + SPEED_INCREASE_PER_OBSTACLE,
        MAX_GAME_SPEED
    )


# ============================================================
# AFFICHAGE DU SCORE
# ============================================================

def draw_score():
    score_text = f"Score : {score}"
    speed_text = f"Vitesse : {game_speed:.1f}"
    obstacle_text = f"Obstacles : {obstacles_passed}"

    score_shadow = font_score.render(
        score_text,
        True,
        BLACK
    )

    score_surface = font_score.render(
        score_text,
        True,
        WHITE
    )

    speed_shadow = font_small.render(
        speed_text,
        True,
        BLACK
    )

    speed_surface = font_small.render(
        speed_text,
        True,
        WHITE
    )

    obstacle_shadow = font_small.render(
        obstacle_text,
        True,
        BLACK
    )

    obstacle_surface = font_small.render(
        obstacle_text,
        True,
        WHITE
    )

    screen.blit(score_shadow, (23, 23))
    screen.blit(score_surface, (20, 20))

    screen.blit(speed_shadow, (23, 65))
    screen.blit(speed_surface, (20, 62))

    screen.blit(obstacle_shadow, (23, 92))
    screen.blit(obstacle_surface, (20, 89))


def draw_ground():
    pygame.draw.line(
        screen,
        WHITE,
        (0, GROUND_Y),
        (SCREEN_WIDTH, GROUND_Y),
        width=4
    )


# ============================================================
# MENU PRINCIPAL
# ============================================================

def draw_menu():
    """
    Affiche l'arrière-plan propre au menu principal.
    """
    screen.blit(menu_background_image, (0, 0))

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    title_shadow = font_title.render(
        "GEOMETRY SUBWAY",
        True,
        BLACK
    )

    title_surface = font_title.render(
        "GEOMETRY SUBWAY",
        True,
        WHITE
    )

    title_rect = title_surface.get_rect(
        center=(SCREEN_WIDTH // 2, 155)
    )

    shadow_rect = title_shadow.get_rect(
        center=(SCREEN_WIDTH // 2 + 4, 159)
    )

    screen.blit(title_shadow, shadow_rect)
    screen.blit(title_surface, title_rect)

    start_button.draw(screen)
    quit_button.draw(screen)

    controls_surface = font_small.render(
        "Espace / Haut : sauter    Bas / S : se baisser",
        True,
        WHITE
    )

    controls_rect = controls_surface.get_rect(
        center=(SCREEN_WIDTH // 2, 520)
    )

    screen.blit(controls_surface, controls_rect)

    score_info_surface = font_small.render(
        "Obstacle : +10 points    Pièce : +5 points",
        True,
        YELLOW
    )

    score_info_rect = score_info_surface.get_rect(
        center=(SCREEN_WIDTH // 2, 555)
    )

    screen.blit(score_info_surface, score_info_rect)


# ============================================================
# AFFICHAGE DE LA PARTIE
# ============================================================

def draw_game():
    game_background.draw(screen)
    draw_ground()

    for coin in coins:
        coin.draw(screen)

    for obstacle in obstacles:
        obstacle.draw(screen)

    player.draw(screen)
    draw_score()


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 155))
    screen.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 250,
        SCREEN_HEIGHT // 2 - 155,
        500,
        310
    )

    pygame.draw.rect(
        screen,
        BLACK,
        panel_rect,
        border_radius=20
    )

    pygame.draw.rect(
        screen,
        WHITE,
        panel_rect,
        width=3,
        border_radius=20
    )

    game_over_rect = game_over_image.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 45
        )
    )

    screen.blit(game_over_image, game_over_rect)

    final_score_surface = font_score.render(
        f"Score final : {score}",
        True,
        WHITE
    )

    final_score_rect = final_score_surface.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80
        )
    )

    screen.blit(final_score_surface, final_score_rect)

    obstacle_surface = font_small.render(
        f"Obstacles franchis : {obstacles_passed}",
        True,
        YELLOW
    )

    obstacle_rect = obstacle_surface.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 120
        )
    )

    screen.blit(obstacle_surface, obstacle_rect)


# ============================================================
# MISE À JOUR DU JEU
# ============================================================

def update_game():
    global score
    global obstacles_passed
    global game_state
    global game_over_start_time
    global next_obstacle_time
    global next_coin_time

    keys = pygame.key.get_pressed()

    player.update(keys)
    game_background.update(game_speed)

    current_time = pygame.time.get_ticks()

    # --------------------------------------------------------
    # CRÉATION DES OBSTACLES
    # --------------------------------------------------------

    if current_time >= next_obstacle_time:
        obstacles.append(create_random_obstacle())

        # Le délai diminue progressivement lorsque le jeu accélère.
        speed_difference = game_speed - INITIAL_GAME_SPEED
        delay_reduction = int(speed_difference * 35)

        minimum_delay = max(
            700,
            MIN_OBSTACLE_DELAY - delay_reduction
        )

        maximum_delay = max(
            1100,
            MAX_OBSTACLE_DELAY - delay_reduction
        )

        next_obstacle_time = (
            current_time
            + random.randint(minimum_delay, maximum_delay)
        )

    # --------------------------------------------------------
    # CRÉATION DES PIÈCES
    # --------------------------------------------------------

    if current_time >= next_coin_time:
        coins.extend(create_coin_group())

        next_coin_time = (
            current_time
            + random.randint(
                MIN_COIN_DELAY,
                MAX_COIN_DELAY
            )
        )

    player_collision_rect = player.get_collision_rect()

    # --------------------------------------------------------
    # MISE À JOUR DES OBSTACLES
    # --------------------------------------------------------

    for obstacle in obstacles[:]:
        obstacle.update(game_speed)

        # L'obstacle est considéré comme franchi lorsque sa partie
        # droite est passée derrière le personnage.
        if (
            not obstacle.has_been_passed
            and obstacle.rect.right < player.rect.left
        ):
            obstacle.has_been_passed = True

            obstacles_passed += 1
            score += OBSTACLE_SCORE_VALUE

            increase_game_speed()

        # Collision avec une haie ou un oiseau.
        if player_collision_rect.colliderect(
            obstacle.get_collision_rect()
        ):
            game_state = GAME_OVER
            game_over_start_time = current_time
            stop_music()
            return

        if obstacle.is_outside_screen():
            obstacles.remove(obstacle)

    # --------------------------------------------------------
    # MISE À JOUR DES PIÈCES
    # --------------------------------------------------------

    for coin in coins[:]:
        coin.update(game_speed)

        if player_collision_rect.colliderect(
            coin.get_collision_rect()
        ):
            score += COIN_VALUE
            coin.collected = True
            coins.remove(coin)
            continue

        if coin.is_outside_screen():
            coins.remove(coin)


# ============================================================
# RETOUR AU MENU
# ============================================================

def return_to_menu():
    global game_state

    stop_music()
    game_state = MENU


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

running = True

while running:
    clock.tick(FPS)

    # --------------------------------------------------------
    # ÉVÉNEMENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ----------------------------------------------------
        # MENU PRINCIPAL
        # ----------------------------------------------------

        if game_state == MENU:

            if start_button.is_clicked(event):
                reset_game()
                game_state = PLAYING

            elif quit_button.is_clicked(event):
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                ):
                    reset_game()
                    game_state = PLAYING

                elif event.key == pygame.K_ESCAPE:
                    running = False

        # ----------------------------------------------------
        # PARTIE EN COURS
        # ----------------------------------------------------

        elif game_state == PLAYING:

            if event.type == pygame.KEYDOWN:

                if event.key in (
                    pygame.K_SPACE,
                    pygame.K_UP,
                    pygame.K_z
                ):
                    player.jump()

                elif event.key == pygame.K_ESCAPE:
                    return_to_menu()

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        elif game_state == GAME_OVER:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return_to_menu()

                elif (
                    event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE
                    )
                    and pygame.time.get_ticks()
                    - game_over_start_time > 500
                ):
                    return_to_menu()

    # --------------------------------------------------------
    # MISE À JOUR ET AFFICHAGE
    # --------------------------------------------------------

    if game_state == MENU:
        draw_menu()

    elif game_state == PLAYING:
        update_game()

        # update_game peut déclencher immédiatement GAME_OVER.
        if game_state == PLAYING:
            draw_game()
        else:
            draw_game()
            draw_game_over()

    elif game_state == GAME_OVER:
        draw_game()
        draw_game_over()

        # Retour automatique au menu après deux secondes.
        if (
            pygame.time.get_ticks()
            - game_over_start_time
            >= 2000
        ):
            return_to_menu()

    pygame.display.flip()


# ============================================================
# FERMETURE
# ============================================================

stop_music()
pygame.quit()
sys.exit()