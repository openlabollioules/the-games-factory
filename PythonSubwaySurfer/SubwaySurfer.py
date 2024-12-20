import pygame
import random

# Initialiser Pygame
pygame.init()

# Paramètres du jeu
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Créer l'écran du jeu
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Subway Surfers Simplifié")

# Charger les images
player_image = pygame.image.load("player.png")  # Charger l'image du joueur
player_size = 50
player_image = pygame.transform.scale(player_image, (player_size, player_size))  # Redimensionner l'image

train_image = pygame.image.load("train.png")  # Charger l'image du train
train_size = (70, 100)
train_image = pygame.transform.scale(train_image, train_size)  # Redimensionner l'image du train

# Charger la musique de fond
pygame.mixer.music.load("background_music.mp3")  # Charger le fichier audio
pygame.mixer.music.play(-1)  # Jouer la musique en boucle (-1 pour répétition infinie)

# Police
font = pygame.font.Font(None, 36)

# Position du joueur
columns = [SCREEN_WIDTH // 6, SCREEN_WIDTH // 2, 5 * SCREEN_WIDTH // 6]  # Positions des 3 colonnes
player_x = columns[1] - player_size // 2  # Le joueur commence dans la colonne du milieu
player_y = SCREEN_HEIGHT - player_size - 10
current_column = 1  # Index de la colonne actuelle

# Obstacles (trains)
obstacle_speed = 7
obstacles = []


# Fonction pour dessiner le joueur
def draw_player(x, y):
    screen.blit(player_image, (x, y))  # Afficher l'image à la position du joueur


# Fonction pour créer un train
def create_obstacle():
    column = random.choice(columns)  # Choisir une colonne aléatoire
    y = -train_size[1]
    return [column - train_size[0] // 2, y]


# Fonction pour dessiner les trains
def draw_obstacles(obstacles):
    for obs in obstacles:
        screen.blit(train_image, (obs[0], obs[1]))


# Vérifier les collisions
def check_collision(player_x, player_y, obstacles):
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for obs in obstacles:
        obs_rect = pygame.Rect(obs[0], obs[1], train_size[0], train_size[1])
        if player_rect.colliderect(obs_rect):
            return True
    return False


# Fonction pour l'écran d'accueil
def show_start_screen():
    while True:
        screen.fill(WHITE)
        # Afficher le titre du jeu
        title_font = pygame.font.Font(None, 72)
        title_surface = title_font.render("Subway Surfers Simplifié", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_surface, title_rect)

        # Instructions
        instructions_font = pygame.font.Font(None, 36)
        instructions_surface = instructions_font.render("Appuyez sur Entrée pour jouer ou Échap pour quitter", True,
                                                        BLACK)
        instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(instructions_surface, instructions_rect)

        pygame.display.flip()

        # Gérer les événements de l'écran d'accueil
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Commencer le jeu
                    return
                elif event.key == pygame.K_ESCAPE:  # Quitter le jeu
                    pygame.quit()
                    exit()


# Boucle principale
clock = pygame.time.Clock()
running = True
score = 0

# Afficher l'écran d'accueil avant de commencer
show_start_screen()

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Déplacer le joueur entre les colonnes
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and current_column > 0:
        current_column -= 1
        player_x = columns[current_column] - player_size // 2
        pygame.time.delay(200)  # Éviter les mouvements trop rapides
    if keys[pygame.K_RIGHT] and current_column < len(columns) - 1:
        current_column += 1
        player_x = columns[current_column] - player_size // 2
        pygame.time.delay(200)  # Éviter les mouvements trop rapides

    # Créer et déplacer les obstacles
    if random.randint(1, 20) == 1:
        obstacles.append(create_obstacle())

    for obs in obstacles:
        obs[1] += obstacle_speed

    # Enlever les obstacles hors écran
    obstacles = [obs for obs in obstacles if obs[1] < SCREEN_HEIGHT]

    # Dessiner les éléments
    draw_player(player_x, player_y)  # Afficher l'image du joueur
    draw_obstacles(obstacles)  # Afficher les trains

    # Vérifier les collisions
    if check_collision(player_x, player_y, obstacles):
        text = font.render("Game Over!", True, RED)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        running = False

    # Afficher le score
    score += 1
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
