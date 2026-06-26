import sys
from pathlib import Path

import pygame


# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GAME_TITLE = "Jeu de plateformes"

BASE_DIRECTORY = Path(__file__).resolve().parent
ASSETS_DIRECTORY = BASE_DIRECTORY / "assets"

ASSET_FILES = {
    "background": "background.png",
    "player_idle": "player_idle.png",
    "player_run_1": "player_run_1.png",
    "player_run_2": "player_run_2.png",
    "player_jump": "player_jump.png",
    "platform": "platform.png",
    "coin": "coin.png",
    "enemy": "enemy.png",
    "goal": "goal.png",
    "music": "music.mp3",
}


# ============================================================
# OUTILS
# ============================================================

def load_image(
    filename,
    size,
    fallback_color=(255, 0, 255),
    use_alpha=True,
):
    """
    Charge une image depuis le dossier assets.

    Si le fichier n'existe pas, une image temporaire colorée
    est créée afin que le jeu reste exécutable.
    """

    image_path = ASSETS_DIRECTORY / filename

    if image_path.exists():
        image = pygame.image.load(image_path)

        if use_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

        return pygame.transform.smoothscale(image, size)

    flags = pygame.SRCALPHA if use_alpha else 0

    image = pygame.Surface(size, flags)
    image.fill(fallback_color)

    pygame.draw.line(
        image,
        (0, 0, 0),
        (0, 0),
        (size[0], size[1]),
        3,
    )

    pygame.draw.line(
        image,
        (0, 0, 0),
        (size[0], 0),
        (0, size[1]),
        3,
    )

    return image


def remove_white_background(image, threshold=238):
    """
    Rend transparents les pixels blancs ou presque blancs.

    Cette fonction sert notamment à enlever le contour blanc
    autour de l'image de la pièce.
    """

    image = image.convert_alpha()
    result = image.copy()

    width, height = result.get_size()

    for x in range(width):
        for y in range(height):
            red, green, blue, alpha = result.get_at((x, y))

            if (
                red >= threshold
                and green >= threshold
                and blue >= threshold
            ):
                result.set_at((x, y), (red, green, blue, 0))

    return result


def create_ground_surface(width, height):
    """
    Crée un sol avec une couche d'herbe et de la terre.
    """

    surface = pygame.Surface(
        (width, height),
        pygame.SRCALPHA,
    )

    grass_light = (93, 207, 70)
    grass_middle = (50, 168, 48)
    grass_dark = (31, 120, 38)

    dirt_light = (173, 105, 53)
    dirt_middle = (137, 78, 39)
    dirt_dark = (91, 49, 26)

    # Terre principale.
    pygame.draw.rect(
        surface,
        dirt_light,
        (0, 10, width, height - 10),
    )

    # Couches d'herbe.
    pygame.draw.rect(
        surface,
        grass_dark,
        (0, 0, width, 16),
    )

    pygame.draw.rect(
        surface,
        grass_middle,
        (0, 0, width, 12),
    )

    pygame.draw.rect(
        surface,
        grass_light,
        (0, 0, width, 7),
    )

    # Pointes d'herbe.
    for x in range(0, width, 10):
        pygame.draw.polygon(
            surface,
            grass_middle,
            [
                (x, 12),
                (x + 3, 5),
                (x + 6, 12),
            ],
        )

        pygame.draw.polygon(
            surface,
            grass_dark,
            [
                (x + 5, 15),
                (x + 8, 8),
                (x + 11, 15),
            ],
        )

    # Ombre sous l'herbe.
    pygame.draw.line(
        surface,
        dirt_dark,
        (0, 16),
        (width, 16),
        3,
    )

    # Petites pierres dans la terre.
    for x in range(10, width, 28):
        for y in range(27, height, 22):
            pygame.draw.circle(
                surface,
                dirt_middle,
                (x, y),
                3,
            )

            pygame.draw.circle(
                surface,
                (204, 142, 80),
                (x + 9, y + 6),
                2,
            )

    # Petits traits décoratifs.
    for x in range(18, width, 42):
        pygame.draw.line(
            surface,
            dirt_dark,
            (x, 35),
            (x + 8, 39),
            2,
        )

    pygame.draw.rect(
        surface,
        dirt_dark,
        (0, 0, width, height),
        2,
    )

    return surface


def draw_centered_text(
    surface,
    text,
    font,
    color,
    center_position,
):
    rendered_text = font.render(
        text,
        True,
        color,
    )

    text_rectangle = rendered_text.get_rect(
        center=center_position
    )

    surface.blit(
        rendered_text,
        text_rectangle,
    )


# ============================================================
# CAMÉRA
# ============================================================

class Camera:
    def __init__(self, world_width):
        self.x = 0
        self.world_width = world_width

    def update(self, target):
        desired_x = target.rect.centerx - SCREEN_WIDTH // 2

        maximum_x = max(
            0,
            self.world_width - SCREEN_WIDTH,
        )

        self.x = max(
            0,
            min(desired_x, maximum_x),
        )

    def apply(self, rectangle):
        return rectangle.move(-self.x, 0)


# ============================================================
# PLATEFORME
# ============================================================

class Platform(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        image,
    ):
        super().__init__()

        self.image = pygame.transform.scale(
            image,
            (width, height),
        )

        self.rect = self.image.get_rect(
            topleft=(x, y)
        )


# ============================================================
# PIÈCE
# ============================================================

class Coin(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        image,
    ):
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect(
            center=(x, y)
        )


# ============================================================
# OBJECTIF
# ============================================================

class Goal(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        image,
    ):
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect(
            bottomleft=(x, y)
        )


# ============================================================
# ENNEMI
# ============================================================

class Enemy(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        image,
        left_limit,
        right_limit,
    ):
        super().__init__()

        self.original_image = image
        self.image = image

        self.rect = self.image.get_rect(
            bottomleft=(x, y)
        )

        self.left_limit = left_limit
        self.right_limit = right_limit

        self.speed = 2
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction

        if self.rect.left <= self.left_limit:
            self.rect.left = self.left_limit
            self.direction = 1

        elif self.rect.right >= self.right_limit:
            self.rect.right = self.right_limit
            self.direction = -1

        self.image = pygame.transform.flip(
            self.original_image,
            self.direction < 0,
            False,
        )


# ============================================================
# JOUEUR
# ============================================================

class Player(pygame.sprite.Sprite):
    MOVE_SPEED = 5
    JUMP_SPEED = -13
    STOMP_BOUNCE_SPEED = -9
    GRAVITY = 0.65
    MAXIMUM_FALL_SPEED = 15

    def __init__(
        self,
        x,
        y,
        images,
    ):
        super().__init__()

        self.images = images

        self.image = self.images["idle"]

        self.rect = self.image.get_rect(
            topleft=(x, y)
        )

        self.velocity = pygame.Vector2(0, 0)

        self.on_ground = False
        self.facing_left = False

        self.animation_timer = 0
        self.animation_index = 0

        self.spawn_position = pygame.Vector2(
            x,
            y,
        )

        # Position du joueur avant le déplacement.
        # Elle permet de savoir s'il était au-dessus d'un ennemi.
        self.previous_rect = self.rect.copy()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        self.velocity.x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.velocity.x = -self.MOVE_SPEED
            self.facing_left = True

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = self.MOVE_SPEED
            self.facing_left = False

    def jump(self):
        if self.on_ground:
            self.velocity.y = self.JUMP_SPEED
            self.on_ground = False

    def bounce_after_stomp(self):
        """
        Fait rebondir le joueur après avoir écrasé un ennemi.
        """

        self.velocity.y = self.STOMP_BOUNCE_SPEED
        self.on_ground = False

    def apply_gravity(self):
        self.velocity.y += self.GRAVITY

        if self.velocity.y > self.MAXIMUM_FALL_SPEED:
            self.velocity.y = self.MAXIMUM_FALL_SPEED

    def move_horizontally(self, platforms):
        self.rect.x += round(self.velocity.x)

        collided_platforms = pygame.sprite.spritecollide(
            self,
            platforms,
            False,
        )

        for platform in collided_platforms:
            if self.velocity.x > 0:
                self.rect.right = platform.rect.left

            elif self.velocity.x < 0:
                self.rect.left = platform.rect.right

    def move_vertically(self, platforms):
        self.rect.y += round(self.velocity.y)

        self.on_ground = False

        collided_platforms = pygame.sprite.spritecollide(
            self,
            platforms,
            False,
        )

        for platform in collided_platforms:
            if self.velocity.y > 0:
                self.rect.bottom = platform.rect.top
                self.velocity.y = 0
                self.on_ground = True

            elif self.velocity.y < 0:
                self.rect.top = platform.rect.bottom
                self.velocity.y = 0

    def update_animation(self):
        if not self.on_ground:
            selected_image = self.images["jump"]

        elif self.velocity.x != 0:
            self.animation_timer += 1

            if self.animation_timer >= 10:
                self.animation_timer = 0
                self.animation_index += 1

                if self.animation_index >= len(
                    self.images["run"]
                ):
                    self.animation_index = 0

            selected_image = self.images["run"][
                self.animation_index
            ]

        else:
            selected_image = self.images["idle"]

        previous_bottom = self.rect.bottom
        previous_center_x = self.rect.centerx

        self.image = pygame.transform.flip(
            selected_image,
            self.facing_left,
            False,
        )

        self.rect = self.image.get_rect()

        self.rect.bottom = previous_bottom
        self.rect.centerx = previous_center_x

    def update(self, platforms):
        # Sauvegarde de la position avant le mouvement.
        self.previous_rect = self.rect.copy()

        self.handle_input()
        self.apply_gravity()

        self.move_horizontally(platforms)
        self.move_vertically(platforms)

        self.update_animation()


# ============================================================
# JEU PRINCIPAL
# ============================================================

class Game:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    VICTORY = "victory"

    def __init__(self):
        pygame.init()

        try:
            pygame.mixer.init()
            self.audio_available = True

        except pygame.error:
            self.audio_available = False

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        pygame.display.set_caption(GAME_TITLE)

        self.clock = pygame.time.Clock()

        self.large_font = pygame.font.Font(
            None,
            72,
        )

        self.medium_font = pygame.font.Font(
            None,
            42,
        )

        self.small_font = pygame.font.Font(
            None,
            28,
        )

        self.running = True
        self.state = self.MENU

        self.score = 0
        self.lives = 3

        self.invincibility_timer = 0

        self.load_assets()
        self.create_level()
        self.start_music()

    # --------------------------------------------------------
    # CHARGEMENT DES RESSOURCES
    # --------------------------------------------------------

    def load_assets(self):
        self.background_image = load_image(
            ASSET_FILES["background"],
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            fallback_color=(90, 170, 255),
            use_alpha=False,
        )

        self.player_images = {
            "idle": load_image(
                ASSET_FILES["player_idle"],
                (42, 58),
                fallback_color=(30, 100, 255),
            ),

            "run": [
                load_image(
                    ASSET_FILES["player_run_1"],
                    (42, 58),
                    fallback_color=(30, 160, 255),
                ),

                load_image(
                    ASSET_FILES["player_run_2"],
                    (42, 58),
                    fallback_color=(30, 210, 255),
                ),
            ],

            "jump": load_image(
                ASSET_FILES["player_jump"],
                (42, 58),
                fallback_color=(255, 180, 20),
            ),
        }

        self.platform_image = load_image(
            ASSET_FILES["platform"],
            (120, 32),
            fallback_color=(135, 85, 42),
        )

        self.ground_image = create_ground_surface(
            128,
            64,
        )

        self.coin_image = load_image(
            ASSET_FILES["coin"],
            (28, 28),
            fallback_color=(255, 215, 0),
        )

        self.coin_image = remove_white_background(
            self.coin_image,
            threshold=238,
        )

        self.enemy_image = load_image(
            ASSET_FILES["enemy"],
            (46, 42),
            fallback_color=(210, 50, 50),
        )

        self.goal_image = load_image(
            ASSET_FILES["goal"],
            (64, 100),
            fallback_color=(245, 245, 245),
        )

    def start_music(self):
        if not self.audio_available:
            return

        music_path = (
            ASSETS_DIRECTORY
            / ASSET_FILES["music"]
        )

        if not music_path.exists():
            return

        try:
            pygame.mixer.music.load(
                music_path
            )

            pygame.mixer.music.set_volume(
                0.45
            )

            pygame.mixer.music.play(-1)

        except pygame.error as error:
            print(
                "Impossible de lire la musique :",
                error,
            )

    # --------------------------------------------------------
    # CRÉATION DU NIVEAU
    # --------------------------------------------------------

    def create_level(self):
        self.world_width = 3000

        self.camera = Camera(
            self.world_width
        )

        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.goals = pygame.sprite.Group()

        ground_segments = [
            (0, 540, 700, 60),
            (780, 540, 500, 60),
            (1380, 540, 620, 60),
            (2080, 540, 920, 60),
        ]

        for x, y, width, height in ground_segments:
            ground = Platform(
                x,
                y,
                width,
                height,
                self.ground_image,
            )

            self.platforms.add(ground)

        platform_positions = [
            (260, 455, 150, 28),
            (500, 385, 150, 28),
            (720, 315, 130, 28),
            (930, 430, 160, 28),
            (1180, 350, 130, 28),
            (1420, 455, 150, 28),
            (1660, 380, 160, 28),
            (1880, 300, 130, 28),
            (2160, 440, 160, 28),
            (2410, 360, 150, 28),
            (2640, 280, 150, 28),
        ]

        for x, y, width, height in platform_positions:
            platform = Platform(
                x,
                y,
                width,
                height,
                self.platform_image,
            )

            self.platforms.add(platform)

        coin_positions = [
            (335, 415),
            (575, 345),
            (785, 275),
            (1010, 390),
            (1245, 310),
            (1495, 415),
            (1740, 340),
            (1945, 260),
            (2240, 400),
            (2485, 320),
            (2715, 240),
        ]

        for x, y in coin_positions:
            coin = Coin(
                x,
                y,
                self.coin_image,
            )

            self.coins.add(coin)

        enemy_data = [
            (880, 540, 800, 1200),
            (1500, 540, 1390, 1950),
            (2250, 540, 2100, 2580),
        ]

        for (
            x,
            y,
            left_limit,
            right_limit,
        ) in enemy_data:

            enemy = Enemy(
                x,
                y,
                self.enemy_image,
                left_limit,
                right_limit,
            )

            self.enemies.add(enemy)

        self.goal = Goal(
            2880,
            540,
            self.goal_image,
        )

        self.goals.add(self.goal)

        self.player = Player(
            80,
            450,
            self.player_images,
        )

    # --------------------------------------------------------
    # RÉINITIALISATION
    # --------------------------------------------------------

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.invincibility_timer = 0

        self.create_level()

        self.state = self.PLAYING

    def lose_life(self):
        if self.invincibility_timer > 0:
            return

        self.lives -= 1

        if self.lives <= 0:
            self.state = self.GAME_OVER
            return

        self.player.rect.topleft = (
            round(self.player.spawn_position.x),
            round(self.player.spawn_position.y),
        )

        self.player.previous_rect = self.player.rect.copy()
        self.player.velocity.update(0, 0)

        self.camera.x = 0

        # Environ 1,5 seconde d'invincibilité.
        self.invincibility_timer = 90

    # --------------------------------------------------------
    # COLLISION AVEC LES ENNEMIS
    # --------------------------------------------------------

    def handle_enemy_collisions(self):
        """
        Détermine si le joueur écrase un ennemi ou s'il est touché.

        Un ennemi est écrasé lorsque :
        - le joueur descend ;
        - le joueur était au-dessus de l'ennemi avant le mouvement ;
        - le joueur entre maintenant en collision avec l'ennemi.
        """

        collided_enemies = pygame.sprite.spritecollide(
            self.player,
            self.enemies,
            False,
        )

        if not collided_enemies:
            return False

        for enemy in collided_enemies:
            player_was_above = (
                self.player.previous_rect.bottom
                <= enemy.rect.top + 10
            )

            player_is_falling = (
                self.player.velocity.y > 0
            )

            player_hits_enemy_top = (
                self.player.rect.bottom
                >= enemy.rect.top
            )

            if (
                player_was_above
                and player_is_falling
                and player_hits_enemy_top
            ):
                # Replace le joueur juste au-dessus de l'ennemi.
                self.player.rect.bottom = enemy.rect.top

                # Supprime l'ennemi.
                enemy.kill()

                # Fait rebondir le joueur.
                self.player.bounce_after_stomp()

                # Ajoute des points.
                self.score += 200

                return True

        # La collision ne vient pas du dessus :
        # le joueur perd une vie.
        self.lose_life()

        return True

    # --------------------------------------------------------
    # ÉVÉNEMENTS
    # --------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:

                if self.state == self.PLAYING:
                    self.state = self.MENU

                else:
                    self.running = False

            if self.state == self.MENU:

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ):
                    self.reset_game()

            elif self.state == self.PLAYING:

                if event.key in (
                    pygame.K_SPACE,
                    pygame.K_UP,
                    pygame.K_z,
                ):
                    self.player.jump()

            elif self.state in (
                self.GAME_OVER,
                self.VICTORY,
            ):

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ):
                    self.reset_game()

    # --------------------------------------------------------
    # MISE À JOUR DU JEU
    # --------------------------------------------------------

    def update(self):
        if self.state != self.PLAYING:
            return

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        self.player.update(
            self.platforms
        )

        self.enemies.update()

        # Collision avec les ennemis.
        enemy_collision = self.handle_enemy_collisions()

        if enemy_collision and self.state != self.PLAYING:
            return

        self.camera.update(
            self.player
        )

        # Ramassage des pièces.
        collected_coins = pygame.sprite.spritecollide(
            self.player,
            self.coins,
            True,
        )

        self.score += (
            len(collected_coins) * 100
        )

        # Fin du niveau.
        touched_goal = pygame.sprite.spritecollideany(
            self.player,
            self.goals,
        )

        if touched_goal:
            self.state = self.VICTORY
            return

        # Chute dans un trou.
        if self.player.rect.top > SCREEN_HEIGHT + 200:
            self.lose_life()

    # --------------------------------------------------------
    # AFFICHAGE DU NIVEAU
    # --------------------------------------------------------

    def draw_background(self):
        self.screen.blit(
            self.background_image,
            (0, 0),
        )

    def draw_world(self):
        self.draw_background()

        for platform in self.platforms:
            screen_rectangle = self.camera.apply(
                platform.rect
            )

            self.screen.blit(
                platform.image,
                screen_rectangle,
            )

        for coin in self.coins:
            screen_rectangle = self.camera.apply(
                coin.rect
            )

            self.screen.blit(
                coin.image,
                screen_rectangle,
            )

        for enemy in self.enemies:
            screen_rectangle = self.camera.apply(
                enemy.rect
            )

            self.screen.blit(
                enemy.image,
                screen_rectangle,
            )

        for goal in self.goals:
            screen_rectangle = self.camera.apply(
                goal.rect
            )

            self.screen.blit(
                goal.image,
                screen_rectangle,
            )

        player_screen_rectangle = self.camera.apply(
            self.player.rect
        )

        player_visible = (
            self.invincibility_timer == 0
            or self.invincibility_timer % 10 < 5
        )

        if player_visible:
            self.screen.blit(
                self.player.image,
                player_screen_rectangle,
            )

        self.draw_hud()

    def draw_hud(self):
        hud_surface = pygame.Surface(
            (270, 55),
            pygame.SRCALPHA,
        )

        hud_surface.fill(
            (0, 0, 0, 145)
        )

        self.screen.blit(
            hud_surface,
            (12, 12),
        )

        score_text = self.small_font.render(
            f"Score : {self.score}",
            True,
            (255, 255, 255),
        )

        lives_text = self.small_font.render(
            f"Vies : {self.lives}",
            True,
            (255, 255, 255),
        )

        self.screen.blit(
            score_text,
            (25, 28),
        )

        self.screen.blit(
            lives_text,
            (175, 28),
        )

    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    def draw_menu(self):
        self.draw_background()

        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (0, 0, 0, 145)
        )

        self.screen.blit(
            overlay,
            (0, 0),
        )

        draw_centered_text(
            self.screen,
            GAME_TITLE,
            self.large_font,
            (255, 255, 255),
            (SCREEN_WIDTH // 2, 150),
        )

        draw_centered_text(
            self.screen,
            "Entrée ou Espace : jouer",
            self.medium_font,
            (255, 230, 80),
            (SCREEN_WIDTH // 2, 260),
        )

        draw_centered_text(
            self.screen,
            "Flèche gauche / Q : aller à gauche",
            self.small_font,
            (255, 255, 255),
            (SCREEN_WIDTH // 2, 325),
        )

        draw_centered_text(
            self.screen,
            "Flèche droite / D : aller à droite",
            self.small_font,
            (255, 255, 255),
            (SCREEN_WIDTH // 2, 360),
        )

        draw_centered_text(
            self.screen,
            "Espace, Z ou flèche du haut : sauter",
            self.small_font,
            (255, 255, 255),
            (SCREEN_WIDTH // 2, 395),
        )

        draw_centered_text(
            self.screen,
            "Saute sur les ennemis pour les éliminer",
            self.small_font,
            (255, 230, 80),
            (SCREEN_WIDTH // 2, 440),
        )

        draw_centered_text(
            self.screen,
            "Échap : quitter",
            self.small_font,
            (210, 210, 210),
            (SCREEN_WIDTH // 2, 485),
        )

    # --------------------------------------------------------
    # ÉCRANS DE FIN
    # --------------------------------------------------------

    def draw_end_screen(self, victory):
        self.draw_world()

        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        self.screen.blit(
            overlay,
            (0, 0),
        )

        if victory:
            title = "NIVEAU TERMINÉ !"
            title_color = (255, 230, 70)

        else:
            title = "GAME OVER"
            title_color = (255, 80, 80)

        draw_centered_text(
            self.screen,
            title,
            self.large_font,
            title_color,
            (SCREEN_WIDTH // 2, 210),
        )

        draw_centered_text(
            self.screen,
            f"Score : {self.score}",
            self.medium_font,
            (255, 255, 255),
            (SCREEN_WIDTH // 2, 305),
        )

        draw_centered_text(
            self.screen,
            "Entrée ou Espace : recommencer",
            self.small_font,
            (255, 255, 255),
            (SCREEN_WIDTH // 2, 375),
        )

        draw_centered_text(
            self.screen,
            "Échap : quitter",
            self.small_font,
            (210, 210, 210),
            (SCREEN_WIDTH // 2, 420),
        )

    def draw(self):
        if self.state == self.MENU:
            self.draw_menu()

        elif self.state == self.PLAYING:
            self.draw_world()

        elif self.state == self.GAME_OVER:
            self.draw_end_screen(
                victory=False
            )

        elif self.state == self.VICTORY:
            self.draw_end_screen(
                victory=True
            )

        pygame.display.flip()

    # --------------------------------------------------------
    # BOUCLE PRINCIPALE
    # --------------------------------------------------------

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ============================================================
# LANCEMENT DU JEU
# ============================================================

if __name__ == "__main__":
    game = Game()
    game.run()