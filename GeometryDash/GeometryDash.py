import pygame
import random
import sys

# Initialisation de pygame
pygame.init()

# Paramètres de l'écran
WIDTH, HEIGHT = 800, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Paramètres du joueur
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_X = 100
PLAYER_Y = HEIGHT - PLAYER_HEIGHT - 10
PLAYER_COLOR = BLUE

# Paramètres des obstacles
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
OBSTACLE_COLOR = RED

# Vitesse du jeu
PLAYER_VELOCITY = 8
GRAVITY = 1
JUMP_VELOCITY = -15
OBSTACLE_SPEED = 10

# Horloge
clock = pygame.time.Clock()
FPS = 60

# Police de score
font = pygame.font.Font(None, 36)


def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    SCREEN.blit(label, (x, y))


def main():
    # Position et vitesse du joueur
    player_y = PLAYER_Y
    player_velocity_y = 0

    # Obstacles
    obstacles = []
    obstacle_timer = 0

    # Score
    score = 0

    # Démarrage du jeu
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_SPACE and player_y >= PLAYER_Y:
                    player_velocity_y = JUMP_VELOCITY

        if not game_over:
            # Gravitation
            player_velocity_y += GRAVITY
            player_y += player_velocity_y
            if player_y > PLAYER_Y:  # Empêche de tomber sous le sol
                player_y = PLAYER_Y

            # Génération des obstacles
            obstacle_timer += 1
            if obstacle_timer > 60:  # Toutes les 60 frames
                obstacles.append(pygame.Rect(WIDTH, HEIGHT - OBSTACLE_HEIGHT - 10, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
                obstacle_timer = 0

            # Déplacement des obstacles
            for obstacle in obstacles:
                obstacle.x -= OBSTACLE_SPEED
            obstacles = [obs for obs in obstacles if obs.x + OBSTACLE_WIDTH > 0]

            # Collision
            player_rect = pygame.Rect(PLAYER_X, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            for obstacle in obstacles:
                if player_rect.colliderect(obstacle):
                    game_over = True

            # Score
            score += 1

        # Dessin des éléments
        SCREEN.fill(WHITE)
        pygame.draw.rect(SCREEN, PLAYER_COLOR, (PLAYER_X, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        for obstacle in obstacles:
            pygame.draw.rect(SCREEN, OBSTACLE_COLOR, obstacle)

        # Affichage du score
        draw_text(f"Score: {score}", 10, 10)

        if game_over:
            draw_text("Game Over! Press R to Restart", WIDTH // 2 - 150, HEIGHT // 2, RED)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()  # Redémarrage du jeu

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
@