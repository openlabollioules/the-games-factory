import pygame
import random
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
COLORS = [RED, GREEN, BLUE, YELLOW]

# Créer la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Casse Briques")

# Charger les images
background_image = pygame.image.load("background.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
player_image = pygame.image.load("player.png")

# Charger la musique
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)  # Jouer en boucle

# Variables du joueur
player_width = 100
player_height = 20
player_image = pygame.transform.scale(player_image, (player_width, player_height))
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 30
player_speed = 8
lives = 3

# Variables de la balle
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 4 * random.choice((1, -1))
ball_speed_y = -4

# Variables des blocs
block_width = 60
block_height = 20
blocks = []
bonuses = []

# Variables de tir
shots = []
shot_speed = -5
can_shoot = False

# Fonction pour créer les niveaux
def create_level(level):
    blocks.clear()
    if level == 1:
        rows, cols = 5, WIDTH // (block_width + 10)
        for row in range(rows):
            for col in range(cols):
                block_x = col * (block_width + 10) + 35
                block_y = row * (block_height + 10) + 50
                color = random.choice(COLORS)
                blocks.append((pygame.Rect(block_x, block_y, block_width, block_height), color))
    elif level == 2:
        for row in range(5):
            for col in range(row, WIDTH // (block_width + 10) - row):
                block_x = col * (block_width + 10) + 35
                block_y = row * (block_height + 10) + 50
                color = random.choice(COLORS)
                blocks.append((pygame.Rect(block_x, block_y, block_width, block_height), color))

# Fonction principale du jeu
def main_menu():
    menu_font = pygame.font.Font(None, 50)
    menu_text = menu_font.render("Appuyez sur ENTREE pour jouer", True, WHITE)
    quit_text = menu_font.render("Appuyez sur ESCAPE pour quitter", True, WHITE)
    while True:
        screen.fill(BLACK)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# Fonction du jeu
def game_loop():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, player_x, can_shoot, lives
    clock = pygame.time.Clock()
    running = True
    level = 1
    create_level(level)

    while running:
        screen.blit(background_image, (0, 0))

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and can_shoot:
                    shots.append(pygame.Rect(player_x + player_width // 2 - 2, player_y, 4, 10))
                elif event.key == pygame.K_ESCAPE:
                    main_menu()
                    shots.append(pygame.Rect(player_x + player_width // 2 - 2, player_y, 4, 10))

        # Mouvements du joueur
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x - player_speed > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x + player_speed < WIDTH - player_width:
            player_x += player_speed

        # Mise à jour de la balle
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Collision avec les murs
        if ball_x <= 0 or ball_x >= WIDTH - ball_radius * 2:
            ball_speed_x *= -1
        if ball_y <= 0:
            ball_speed_y *= -1
        if ball_y >= HEIGHT:
            lives -= 1
            if lives > 0:
                ball_x = WIDTH // 2
                ball_y = player_y - ball_radius * 2
                ball_speed_x = 4 * random.choice((1, -1))
                ball_speed_y = -4
            else:
                running = False  # Game over

        # Collision avec le joueur
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        ball_rect = pygame.Rect(ball_x, ball_y, ball_radius * 2, ball_radius * 2)
        if ball_rect.colliderect(player_rect):
            if ball_speed_y > 0:
                ball_speed_y *= -1
                ball_y = player_y - ball_radius * 2

        # Collision avec les blocs
        for block, color in blocks[:]:
            if ball_rect.colliderect(block):
                ball_speed_y *= -1
                blocks.remove((block, color))
                if random.random() < 0.2:  # 20% de chance de bonus de tir
                    bonuses.append((pygame.Rect(block.x + block_width // 2 - 10, block.y, 20, 20), "shot"))
                elif random.random() < 0.1:  # 10% de chance de bonus de vie
                    bonuses.append((pygame.Rect(block.x + block_width // 2 - 10, block.y, 20, 20), "life"))

        # Mise à jour des tirs
        for shot in shots[:]:
            shot.y += shot_speed
            if shot.y < 0:
                shots.remove(shot)
            for block, color in blocks[:]:
                if shot.colliderect(block):
                    blocks.remove((block, color))
                    shots.remove(shot)
                    break

        # Mise à jour des bonus
        for bonus, bonus_type in bonuses[:]:
            bonus.y += 3
            if bonus.colliderect(player_rect):
                if bonus_type == "shot":
                    can_shoot = True
                elif bonus_type == "life":
                    lives += 1
                bonuses.remove((bonus, bonus_type))
            elif bonus.y > HEIGHT:
                bonuses.remove((bonus, bonus_type))

        # Dessiner les blocs
        for block, color in blocks:
            pygame.draw.rect(screen, color, block)

        # Dessiner les bonus
        for bonus, bonus_type in bonuses:
            if bonus_type == "shot":
                pygame.draw.rect(screen, YELLOW, bonus)
            elif bonus_type == "life":
                pygame.draw.rect(screen, GREEN, bonus)

        # Dessiner le joueur
        screen.blit(player_image, (player_x, player_y))

        # Dessiner la balle
        pygame.draw.ellipse(screen, WHITE, ball_rect)

        # Dessiner les tirs
        for shot in shots:
            pygame.draw.rect(screen, WHITE, shot)

        # Afficher le nombre de vies
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Vies: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))

        # Vérifier si tous les blocs sont détruits
        if not blocks:
            level += 1
            create_level(level)
            ball_x = WIDTH // 2
            ball_y = player_y - ball_radius * 2
            ball_speed_x = 4 * random.choice((1, -1))
            ball_speed_y = -4
            can_shoot = False

        # Rafraîchir l'écran
        pygame.display.flip()
        clock.tick(60)

    main_menu()

# Lancer le menu principal
main_menu()
