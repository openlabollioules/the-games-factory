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
GRAY = (200, 200, 200)

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

pokemon_image = pygame.image.load("pokemon.png")  # Charger l'image du Pokémon
pokemon_size = (100, 100)
pokemon_image = pygame.transform.scale(pokemon_image, pokemon_size)  # Redimensionner l'image du Pokémon

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
pokemon_active = False
pokemon_x, pokemon_y = None, None
pokemon_speed = 5
paused = False


# Fonction pour dessiner le joueur
def draw_player(x, y):
    screen.blit(player_image, (x, y))  # Afficher l'image à la position du joueur


# Fonction pour créer un train sur un seul rail à la fois
def create_obstacle():
    if not obstacles or all(obs[1] > train_size[1] * 2 for obs in obstacles):
        column = random.choice(columns)  # Choisir une colonne valide
        y = -train_size[1]
        return [column - train_size[0] // 2, y]
    return None


# Fonction pour dessiner les trains
def draw_obstacles(obstacles):
    for obs in obstacles:
        screen.blit(train_image, (obs[0], obs[1]))


# Fonction pour dessiner les rails
def draw_tracks():
    track_width = 10
    for column in columns:
        pygame.draw.rect(screen, GRAY, (column - track_width // 2, 0, track_width, SCREEN_HEIGHT))


# Vérifier les collisions
def check_collision(player_x, player_y, obstacles):
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for obs in obstacles:
        obs_rect = pygame.Rect(obs[0], obs[1], train_size[0], train_size[1])
        if player_rect.colliderect(obs_rect):
            return True
    return False


# Vérifier les collisions avec le Pokémon
def check_pokemon_collision(player_x, player_y, pokemon_x, pokemon_y):
    if not pokemon_active:
        return False
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pokemon_rect = pygame.Rect(pokemon_x, pokemon_y, pokemon_size[0], pokemon_size[1])
    return player_rect.colliderect(pokemon_rect)


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


# Fonction pour le menu pause
def show_pause_menu():
    while paused:
        screen.fill(WHITE)
        # Afficher le menu pause
        pause_font = pygame.font.Font(None, 72)
        pause_surface = pause_font.render("Pause", True, BLACK)
        pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(pause_surface, pause_rect)

        instructions_font = pygame.font.Font(None, 36)
        instructions_surface = instructions_font.render("Appuyez sur P pour reprendre ou Échap pour quitter", True,
                                                        BLACK)
        instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(instructions_surface, instructions_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Reprendre le jeu
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
    if paused:
        show_pause_menu()
        paused = False

    screen.fill(WHITE)
    draw_tracks()  # Dessiner les rails

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Activer le menu pause
                paused = True

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
    new_obstacle = create_obstacle()
    if new_obstacle:
        obstacles.append(new_obstacle)

    for obs in obstacles:
        obs[1] += obstacle_speed

    # Enlever les obstacles hors écran
    obstacles = [obs for obs in obstacles if obs[1] < SCREEN_HEIGHT]

    # Activer le Pokémon après 3000 points
    if score > 3000 and not pokemon_active:
        pokemon_active = True
        pokemon_x = random.choice(columns) - pokemon_size[0] // 2
        pokemon_y = -pokemon_size[1]

    # Déplacer le Pokémon s'il est actif
    if pokemon_active:
        pokemon_y += pokemon_speed
        screen.blit(pokemon_image, (pokemon_x, pokemon_y))

        # Vérifier les collisions avec le Pokémon
        if check_pokemon_collision(player_x, player_y, pokemon_x, pokemon_y):
            text = font.render("Game Over!", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            running = False

        # Désactiver le Pokémon s'il sort de l'écran
        if pokemon_y > SCREEN_HEIGHT:
            pokemon_active = False

    # Augmenter la vitesse après 1500 points
    if score > 1500:
        obstacle_speed = 10

    # Dessiner les éléments
    draw_player(player_x, player_y)  # Afficher l'image du joueur
    draw_obstacles(obstacles)  # Afficher les trains

    # Vérifier les collisions
    if check_collision(player_x, player_y, obstacles):
        text = font.render("Game Over!", True, BLACK)
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

àà