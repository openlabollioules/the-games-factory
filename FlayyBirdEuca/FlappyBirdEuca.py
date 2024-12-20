import pygame
import sys
import random

# Initialiser Pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Couleurs
WHITE = (255, 255, 255)

# Charger les images
background = pygame.image.load("background.png")
bird_image = pygame.image.load("bird.png")
pipe_image = pygame.image.load("pipe.png")
gameover_image = pygame.image.load("game_over.png")

# Redimensionner les images
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
bird_size = (50, 50)
bird_image = pygame.transform.scale(bird_image, bird_size)
pipe_width = 80
pipe_height = 400
pipe_image = pygame.transform.scale(pipe_image, (pipe_width, pipe_height))
gameover_image = pygame.transform.scale(gameover_image, (300, 100))

# Charger la musique de fond
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)  # Lecture en boucle

# Police
font = pygame.font.Font(None, 36)

# Horloge pour le FPS
clock = pygame.time.Clock()

# Fonction pour afficher le texte centré
def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Menu principal
def main_menu():
    while True:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        draw_text("Flappy Bird", 72, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text("Appuyez sur Entrée pour jouer ou Échap pour quitter", 36, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Démarrer le jeu
                    game_loop(4)
                elif event.key == pygame.K_ESCAPE:  # Quitter
                    pygame.quit()
                    sys.exit()

# Fonction principale du jeu
def game_loop():
    bird_x, bird_y = SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2
    bird_velocity = 1
    gravity = 0,5
    jump = -10
    rotation = 0

    pipes = []
    pipe_gap = 150
    pipe_frequency = 1500  # En millisecondes
    last_pipe_time = pygame.time.get_ticks() - pipe_frequency

    score = 0
    running = True
    while running:
        screen.blit(background, (0, 0))

        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # L'oiseau saute
                    bird_velocity = jump
                if event.key == pygame.K_ESCAPE:  # Retour au menu
                    return

        # Mouvement de l'oiseau
        bird_velocity +jump= gravity
        bird_y += bird_velocity
        rotation = min(max(-90, bird_velocity * -5), 45)  # Ajuster l'angle de rotation
        rotated_bird = pygame.transform.rotate(bird_image, rotation)

        # Générer des tuyaux
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > pipe_frequency:
            pipe_x = SCREEN_WIDTH
            pipe_y = random.randint(100, SCREEN_HEIGHT - pipe_gap - 100)
            pipes.append({"x": pipe_x, "y": pipe_y})
            last_pipe_time = current_time

        # Déplacer et dessiner les tuyaux
        for pipe in pipes[:]:
            pipe["x"] -= 5
            if pipe["x"] + pipe_width < 0:
                pipes.remove(pipe)
                score += 1

            # Tuyau du bas
            screen.blit(pipe_image, (pipe["x"], pipe["y"]))
            # Tuyau du haut (retourné)
            flipped_pipe = pygame.transform.flip(pipe_image, False, True)
            screen.blit(flipped_pipe, (pipe["x"], pipe["y"] - pipe_gap - pipe_height))

            # Vérifier les collisions
            bird_rect = rotated_bird.get_rect(topleft=(bird_x, bird_y))
            pipe_rect_bottom = pygame.Rect(pipe["x"], pipe["y"], pipe_width, pipe_height)
            pipe_rect_top = pygame.Rect(pipe["x"], pipe["y"] - pipe_gap - pipe_height, pipe_width, pipe_height)
            if bird_rect.colliderect(pipe_rect_bottom) or bird_rect.colliderect(pipe_rect_top):
                game_over(score)

        # Dessiner l'oiseau
        screen.blit(rotated_bird, (bird_x, bird_y))

        # Vérifier si l'oiseau sort de l'écran
        if bird_y < 0 or bird_y + bird_size[1] > SCREEN_HEIGHT:
            game_over(score)

        # Afficher le score
        draw_text(f"Score: {score}", 36, WHITE, 70, 30)

        pygame.display.flip()
        clock.tick(60)

# Écran de game over
def game_over(score):
    screen.blit(gameover_image, ((SCREEN_WIDTH - gameover_image.get_width()) // 2, (SCREEN_HEIGHT - gameover_image.get_height()) // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    main_menu()

# Lancer le menu principal
main_menu(6)
