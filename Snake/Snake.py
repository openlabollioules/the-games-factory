import pygame
import random
import sys
import os

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre de jeu
WIDTH, HEIGHT = 800, 600

# Couleurs
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Charger l'image de fond
background_img = pygame.image.load(os.path.join('assets', 'background.jpg'))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Charger les images des blocs
gem_img = pygame.image.load(os.path.join('assets', 'gem.jpg'))
gem_img = pygame.transform.scale(gem_img, (20, 20))
coin_img = pygame.image.load(os.path.join('assets', 'coin.png'))
coin_img = pygame.transform.scale(coin_img, (20, 20))

# Charger la musique de fond
pygame.mixer.music.load(os.path.join('assets', 'background.mp3'))
pygame.mixer.music.play(-1)  # Jouer la musique en boucle

# Vitesse et dimensions du serpent
SNAKE_SIZE = 20
snake_speed = 15

# Police de score
font = pygame.font.SysFont("comicsansms", 35)

def message(msg, color, position):
    mesg = font.render(msg, True, color)
    screen.blit(mesg, position)

def game_loop():
    # Position initiale du serpent
    x, y = WIDTH // 2, HEIGHT // 2
    x_change, y_change = 0, 0
    snake_body = []
    length_of_snake = 1

    # Score
    score = 0

    # Position initiale des pierres précieuses et des pièces d'or
    gem_x, gem_y = random.randint(0, (WIDTH // SNAKE_SIZE) - 1) * SNAKE_SIZE, random.randint(0, (HEIGHT // SNAKE_SIZE) - 1) * SNAKE_SIZE
    coin_x, coin_y = random.randint(0, (WIDTH // SNAKE_SIZE) - 1) * SNAKE_SIZE, random.randint(0, (HEIGHT // SNAKE_SIZE) - 1) * SNAKE_SIZE

    # Boucle principale du jeu
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -SNAKE_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = SNAKE_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -SNAKE_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = SNAKE_SIZE
                    x_change = 0

        # Mise à jour de la position du serpent
        x += x_change
        y += y_change

        # Vérification des collisions avec les bords de l'écran
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            running = False

        # Mise à jour du corps du serpent
        snake_head = [x, y]
        snake_body.append(snake_head)
        if len(snake_body) > length_of_snake:
            del snake_body[0]

        # Vérification des collisions avec soi-même
        for block in snake_body[:-1]:
            if block == snake_head:
                running = False

        # Dessiner l'arrière-plan
        screen.blit(background_img, (0, 0))

        # Dessiner les pierres précieuses et les pièces d'or
        screen.blit(gem_img, (gem_x, gem_y))
        screen.blit(coin_img, (coin_x, coin_y))

        # Dessiner le serpent
        for segment in snake_body:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE])

        # Gestion des collisions avec les pierres précieuses et les pièces d'or
        if x == gem_x and y == gem_y:
            length_of_snake += 1
            score += 10
            gem_x, gem_y = random.randint(0, (WIDTH // SNAKE_SIZE) - 1) * SNAKE_SIZE, random.randint(0, (HEIGHT // SNAKE_SIZE) - 1) * SNAKE_SIZE
        elif x == coin_x and y == coin_y:
            length_of_snake += 1
            score += 5
            coin_x, coin_y = random.randint(0, (WIDTH // SNAKE_SIZE) - 1) * SNAKE_SIZE, random.randint(0, (HEIGHT // SNAKE_SIZE) - 1) * SNAKE_SIZE

        # Afficher le score
        message(f"Score: {score}", WHITE, [10, 10])

        # Rafraîchir l'écran
        pygame.display.update()

        # Contrôle de la vitesse du serpent
        clock.tick(snake_speed)

    # Fin du jeu
    pygame.quit()
    sys.exit()

def main_menu():
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        message("Press SPACE to Play", WHITE, [WIDTH // 3, HEIGHT // 3])
        message("Press Q to Quit", WHITE, [WIDTH // 3, HEIGHT // 2])
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_loop()
                elif event.key == pygame.K_q:
                    menu_running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
