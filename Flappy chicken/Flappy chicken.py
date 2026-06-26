import os
import random
import sys

import pygame


# ============================================================
# Configuration générale
# ============================================================

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

GROUND_Y = 500

ASSETS_FOLDER = "assets"

BACKGROUND_PATH = os.path.join(ASSETS_FOLDER, "background.png")
CHICKEN_PATH = os.path.join(ASSETS_FOLDER, "chicken.png")
CAR_PATH = os.path.join(ASSETS_FOLDER, "car.png")
GAME_OVER_PATH = os.path.join(ASSETS_FOLDER, "kfc.png")
MUSIC_PATH = os.path.join(ASSETS_FOLDER, "background_music.mp3")

# Distance minimale et maximale entre deux voitures, en pixels.
MIN_CAR_GAP = 320
MAX_CAR_GAP = 650


# ============================================================
# Initialisation de Pygame
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
except pygame.error as error:
    print(f"Attention : impossible d'initialiser le son : {error}")

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chicken Run - GO TO KFC")

clock = pygame.time.Clock()

title_font = pygame.font.Font(None, 80)
menu_font = pygame.font.Font(None, 48)
score_font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 30)


# ============================================================
# Fonctions utilitaires
# ============================================================

def load_image(path, size, fallback_color=(255, 0, 255)):
    """
    Charge une image et la redimensionne avec pygame.transform.scale().

    Si l'image n'existe pas, une surface colorée est créée afin que
    le jeu puisse quand même démarrer.
    """
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)

    except (pygame.error, FileNotFoundError) as error:
        print(f"Impossible de charger l'image '{path}' : {error}")

        fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
        fallback_surface.fill(fallback_color)

        pygame.draw.rect(
            fallback_surface,
            (30, 30, 30),
            fallback_surface.get_rect(),
            3
        )

        return fallback_surface


def draw_centered_text(text, font, color, center_x, center_y):
    """Affiche un texte centré à la position indiquée."""
    text_surface = font.render(text, True, color)
    text_rectangle = text_surface.get_rect(
        center=(center_x, center_y)
    )
    screen.blit(text_surface, text_rectangle)


def quit_game():
    """Ferme correctement le jeu."""
    pygame.quit()
    sys.exit()


# ============================================================
# Chargement des images
# ============================================================

background_image = load_image(
    BACKGROUND_PATH,
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    fallback_color=(135, 206, 235)
)

chicken_image = load_image(
    CHICKEN_PATH,
    (85, 85),
    fallback_color=(255, 220, 0)
)

car_image = load_image(
    CAR_PATH,
    (140, 75),
    fallback_color=(220, 30, 30)
)

game_over_image = load_image(
    GAME_OVER_PATH,
    (430, 170),
    fallback_color=(240, 240, 240)
)


# ============================================================
# Musique
# ============================================================

def start_music():
    """Démarre la musique de fond en boucle."""
    if not pygame.mixer.get_init():
        return

    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    except (pygame.error, FileNotFoundError) as error:
        print(f"Impossible de jouer la musique : {error}")


start_music()


# ============================================================
# Classe du poulet
# ============================================================

class Chicken:
    def __init__(self):
        self.image = chicken_image
        self.rect = self.image.get_rect()

        self.rect.x = 120
        self.rect.bottom = GROUND_Y

        self.position_y = float(self.rect.y)

        self.vertical_speed = 0
        self.gravity = 0.9
        self.jump_strength = -18

        self.on_ground = True

    def jump(self):
        """Fait sauter le poulet s'il se trouve au sol."""
        if self.on_ground:
            self.vertical_speed = self.jump_strength
            self.on_ground = False

    def update(self):
        """Applique la gravité et met à jour la position du poulet."""
        self.vertical_speed += self.gravity
        self.position_y += self.vertical_speed

        self.rect.y = round(self.position_y)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.position_y = float(self.rect.y)

            self.vertical_speed = 0
            self.on_ground = True

    def draw(self):
        """Affiche le poulet."""
        screen.blit(self.image, self.rect)

    def get_collision_rect(self):
        """
        Retourne une zone de collision légèrement réduite.

        Cela évite les collisions provoquées par les parties
        transparentes de l'image.
        """
        return self.rect.inflate(-24, -18)


# ============================================================
# Classe des voitures
# ============================================================

class Car:
    def __init__(self, x_position, speed):
        self.image = car_image
        self.rect = self.image.get_rect()

        self.rect.x = x_position
        self.rect.bottom = GROUND_Y

        self.position_x = float(self.rect.x)
        self.speed = speed

        # Empêche de compter plusieurs fois la même voiture.
        self.counted = False

    def update(self):
        """Déplace la voiture vers la gauche."""
        self.position_x -= self.speed
        self.rect.x = round(self.position_x)

    def draw(self):
        """Affiche la voiture."""
        screen.blit(self.image, self.rect)

    def is_off_screen(self):
        """Indique si la voiture est complètement sortie de l'écran."""
        return self.rect.right < 0

    def get_collision_rect(self):
        """Retourne une zone de collision réduite."""
        return self.rect.inflate(-20, -12)


# ============================================================
# Décor
# ============================================================

def draw_scrolling_background(background_x):
    """
    Affiche deux exemplaires de l'arrière-plan côte à côte.

    Cela permet de créer un défilement continu.
    """
    screen.blit(background_image, (background_x, 0))
    screen.blit(
        background_image,
        (background_x + WINDOW_WIDTH, 0)
    )


def draw_ground():
    """Dessine une ligne correspondant au sol."""
    pygame.draw.line(
        screen,
        (70, 70, 70),
        (0, GROUND_Y),
        (WINDOW_WIDTH, GROUND_Y),
        4
    )


# ============================================================
# Menu principal
# ============================================================

def main_menu():
    selected_option = 0
    options = ["Démarrer", "Quitter"]

    background_x = 0
    menu_background_speed = 1

    while True:
        clock.tick(FPS)

        background_x -= menu_background_speed

        if background_x <= -WINDOW_WIDTH:
            background_x = 0

        start_rectangle = pygame.Rect(
            WINDOW_WIDTH // 2 - 140,
            310,
            280,
            60
        )

        quit_rectangle = pygame.Rect(
            WINDOW_WIDTH // 2 - 140,
            390,
            280,
            60
        )

        # ----------------------------------------------------
        # Événements
        # ----------------------------------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_option = (
                        selected_option - 1
                    ) % len(options)

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_option = (
                        selected_option + 1
                    ) % len(options)

                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return "play"

                    quit_game()

                elif event.key == pygame.K_ESCAPE:
                    quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()

                if start_rectangle.collidepoint(mouse_position):
                    return "play"

                if quit_rectangle.collidepoint(mouse_position):
                    quit_game()

        # ----------------------------------------------------
        # Sélection avec la souris
        # ----------------------------------------------------

        mouse_position = pygame.mouse.get_pos()

        if start_rectangle.collidepoint(mouse_position):
            selected_option = 0

        elif quit_rectangle.collidepoint(mouse_position):
            selected_option = 1

        # ----------------------------------------------------
        # Affichage du menu
        # ----------------------------------------------------

        draw_scrolling_background(background_x)

        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))

        draw_centered_text(
            "CHICKEN RUN",
            title_font,
            (255, 235, 50),
            WINDOW_WIDTH // 2,
            150
        )

        draw_centered_text(
            "Saute au-dessus des voitures !",
            small_font,
            (255, 255, 255),
            WINDOW_WIDTH // 2,
            220
        )

        for index, option in enumerate(options):
            option_rectangle = pygame.Rect(
                WINDOW_WIDTH // 2 - 140,
                310 + index * 80,
                280,
                60
            )

            if index == selected_option:
                button_color = (255, 210, 40)
                text_color = (20, 20, 20)
            else:
                button_color = (240, 240, 240)
                text_color = (50, 50, 50)

            pygame.draw.rect(
                screen,
                button_color,
                option_rectangle,
                border_radius=14
            )

            pygame.draw.rect(
                screen,
                (30, 30, 30),
                option_rectangle,
                3,
                border_radius=14
            )

            option_surface = menu_font.render(
                option,
                True,
                text_color
            )

            option_text_rectangle = option_surface.get_rect(
                center=option_rectangle.center
            )

            screen.blit(
                option_surface,
                option_text_rectangle
            )

        draw_centered_text(
            "Flèches : sélectionner | Entrée : valider",
            small_font,
            (255, 255, 255),
            WINDOW_WIDTH // 2,
            520
        )

        pygame.display.flip()


# ============================================================
# Écran GO TO KFC
# ============================================================

def show_game_over(score):
    """
    Affiche l'image GO TO KFC au centre de la fenêtre.

    Après 2,5 secondes, le jeu retourne automatiquement au menu.
    """
    start_time = pygame.time.get_ticks()
    display_duration = 2500

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                    pygame.K_ESCAPE
                ):
                    return

        screen.blit(background_image, (0, 0))

        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        game_over_rectangle = game_over_image.get_rect(
            center=(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 - 40
            )
        )

        screen.blit(
            game_over_image,
            game_over_rectangle
        )

        draw_centered_text(
            f"Score : {score}",
            score_font,
            (255, 255, 255),
            WINDOW_WIDTH // 2,
            410
        )

        draw_centered_text(
            "Retour au menu...",
            small_font,
            (255, 255, 255),
            WINDOW_WIDTH // 2,
            460
        )

        pygame.display.flip()

        elapsed_time = pygame.time.get_ticks() - start_time

        if elapsed_time >= display_duration:
            return


# ============================================================
# Création des voitures
# ============================================================

def create_first_car(car_speed):
    """Crée la première voiture de la partie."""
    first_position = WINDOW_WIDTH + random.randint(150, 350)

    return Car(
        x_position=first_position,
        speed=car_speed
    )


def create_next_car(previous_car, car_speed):
    """
    Crée une voiture à une distance aléatoire de la précédente.

    La distance choisie varie entre MIN_CAR_GAP et MAX_CAR_GAP.
    """
    random_gap = random.randint(
        MIN_CAR_GAP,
        MAX_CAR_GAP
    )

    new_x_position = previous_car.rect.right + random_gap

    return Car(
        x_position=new_x_position,
        speed=car_speed
    )


# ============================================================
# Partie principale
# ============================================================

def play_game():
    chicken = Chicken()

    score = 0

    background_x = 0
    background_speed = 4

    base_car_speed = 8
    car_speed = base_car_speed

    # Création de la première voiture.
    cars = [create_first_car(car_speed)]

    # Une nouvelle distance aléatoire sera choisie après
    # chaque apparition de voiture.
    next_car_gap = random.randint(
        MIN_CAR_GAP,
        MAX_CAR_GAP
    )

    while True:
        clock.tick(FPS)

        # ----------------------------------------------------
        # Événements
        # ----------------------------------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    chicken.jump()

                elif event.key == pygame.K_ESCAPE:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                chicken.jump()

        # ----------------------------------------------------
        # Défilement du fond
        # ----------------------------------------------------

        background_x -= background_speed

        if background_x <= -WINDOW_WIDTH:
            background_x = 0

        # ----------------------------------------------------
        # Mise à jour du poulet
        # ----------------------------------------------------

        chicken.update()

        # ----------------------------------------------------
        # Mise à jour des voitures
        # ----------------------------------------------------

        for car in cars:
            car.speed = car_speed
            car.update()

            # Le score augmente lorsque le poulet a complètement
            # dépassé une voiture.
            if not car.counted and car.rect.right < chicken.rect.left:
                car.counted = True
                score += 1

                # Augmentation progressive de la difficulté.
                car_speed = min(
                    base_car_speed + score * 0.25,
                    15
                )

                background_speed = min(
                    4 + score * 0.08,
                    8
                )

        # Suppression des voitures sorties de l'écran.
        cars = [
            car for car in cars
            if not car.is_off_screen()
        ]

        # ----------------------------------------------------
        # Apparition d'une nouvelle voiture
        # ----------------------------------------------------

        if len(cars) == 0:
            # Cas exceptionnel : toutes les voitures ont quitté
            # l'écran avant la création de la suivante.
            cars.append(create_first_car(car_speed))

            next_car_gap = random.randint(
                MIN_CAR_GAP,
                MAX_CAR_GAP
            )

        else:
            last_car = cars[-1]

            distance_from_right_edge = (
                last_car.rect.left - WINDOW_WIDTH
            )

            # La voiture suivante est créée lorsque la voiture
            # précédente s'est suffisamment avancée.
            if distance_from_right_edge <= -next_car_gap:
                new_car_x = WINDOW_WIDTH + random.randint(20, 100)

                cars.append(
                    Car(
                        x_position=new_car_x,
                        speed=car_speed
                    )
                )

                # Choix d'une nouvelle distance pour la voiture
                # qui apparaîtra ensuite.
                next_car_gap = random.randint(
                    MIN_CAR_GAP,
                    MAX_CAR_GAP
                )

        # ----------------------------------------------------
        # Collisions
        # ----------------------------------------------------

        chicken_collision_rectangle = (
            chicken.get_collision_rect()
        )

        for car in cars:
            car_collision_rectangle = (
                car.get_collision_rect()
            )

            if chicken_collision_rectangle.colliderect(
                car_collision_rectangle
            ):
                show_game_over(score)
                return

        # ----------------------------------------------------
        # Affichage
        # ----------------------------------------------------

        draw_scrolling_background(background_x)
        draw_ground()

        for car in cars:
            car.draw()

        chicken.draw()

        # ----------------------------------------------------
        # Affichage du score
        # ----------------------------------------------------

        score_background = pygame.Surface(
            (200, 58),
            pygame.SRCALPHA
        )
        score_background.fill((0, 0, 0, 120))

        screen.blit(score_background, (20, 20))

        score_surface = score_font.render(
            f"Score : {score}",
            True,
            (255, 255, 255)
        )

        screen.blit(score_surface, (35, 31))

        # ----------------------------------------------------
        # Affichage des commandes
        # ----------------------------------------------------

        instruction_surface = small_font.render(
            "ESPACE : sauter    ÉCHAP : menu",
            True,
            (255, 255, 255)
        )

        instruction_rectangle = instruction_surface.get_rect(
            topright=(WINDOW_WIDTH - 20, 30)
        )

        instruction_background = pygame.Surface(
            (
                instruction_rectangle.width + 24,
                instruction_rectangle.height + 16
            ),
            pygame.SRCALPHA
        )

        instruction_background.fill((0, 0, 0, 120))

        screen.blit(
            instruction_background,
            (
                instruction_rectangle.x - 12,
                instruction_rectangle.y - 8
            )
        )

        screen.blit(
            instruction_surface,
            instruction_rectangle
        )

        pygame.display.flip()


# ============================================================
# Fonction principale
# ============================================================

def main():
    while True:
        action = main_menu()

        if action == "play":
            play_game()


if __name__ == "__main__":
    main()