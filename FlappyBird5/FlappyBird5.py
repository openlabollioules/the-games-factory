import pygame
import sys
import random
import time

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600

# Couleurs
WHITE = (255, 255, 255)

# Création de la fenêtre
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Chargement des ressources
background_image = pygame.image.load("fond.png")
bird_image = pygame.image.load("bird.png")
pipe_image = pygame.image.load("pipe.png")
pipe_flipped = pygame.transform.flip(pipe_image, False, True)
game_over_image = pygame.image.load("gameover.png")
pied_image = pygame.image.load("pied.png")
background_music = "background_music.mp3"

# Ajustement des images
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
bird_image = pygame.transform.scale(bird_image, (50, 50))
pipe_image = pygame.transform.scale(pipe_image, (80, 400))
pipe_flipped = pygame.transform.scale(pipe_flipped, (80, 400))
game_over_image = pygame.transform.scale(game_over_image, (300, 200))
pied_image = pygame.transform.scale(pied_image, (80, 400))

# Musique de fond
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)

# Police
font = pygame.font.Font(None, 74)

# Constantes du jeu
GRAVITY = 0.25
BIRD_JUMP = -6
PIPE_SPEED = -5
PIPE_GAP = 200

# Variables du jeu
bird = pygame.Rect(100, WINDOW_HEIGHT // 2, 50, 50)
bird_movement = 0
pipes = []
score = 0
game_active = False
collision_occurred = False
pipe_disappear_time = None
pipes_visible = True

# Timer pour les tuyaux
pipe_timer = pygame.USEREVENT
pygame.time.set_timer(pipe_timer, 1200)

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= WINDOW_HEIGHT:
            if pipes_visible:
                screen.blit(pipe_image, pipe)
            else:
                screen.blit(pied_image, pipe)
        else:
            if pipes_visible:
                screen.blit(pipe_flipped, pipe)
            else:
                flipped_pied = pygame.transform.flip(pied_image, False, True)
                screen.blit(flipped_pied, pipe)

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx += PIPE_SPEED
    return [pipe for pipe in pipes if pipe.right > 0]

def check_collision(pipes):
    global collision_occurred
    for pipe in pipes:
        if bird.colliderect(pipe):
            collision_occurred = True
            return False
    if bird.top <= 0 or bird.bottom >= WINDOW_HEIGHT:
        collision_occurred = True
        return False
    return True

def display_score():
    score_surface = font.render(str(score), True, WHITE)
    score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(score_surface, score_rect)

def main_menu():
    screen.fill(WHITE)
    title = font.render("Flappy Bird", True, (0, 0, 0))
    play_text = font.render("Press SPACE to Play", True, (0, 0, 0))
    quit_text = font.render("Press ESC to Quit", True, (0, 0, 0))

    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
    screen.blit(play_text, (WINDOW_WIDTH // 2 - play_text.get_width() // 2, 300))
    screen.blit(quit_text, (WINDOW_WIDTH // 2 - quit_text.get_width() // 2, 400))

    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active:
                    bird.center = (100, WINDOW_HEIGHT // 2)
                    bird_movement = 0
                    pipes = []
                    score = 0
                    game_active = True
                    collision_occurred = False
                    pipes_visible = True
                    pipe_disappear_time = None
                else:
                    bird_movement = BIRD_JUMP
            elif event.key == pygame.K_p:
                game_active = False
                collision_occurred = False
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pipe_timer and game_active:
            pipe_height = random.randint(200, 400)
            pipes.append(pipe_image.get_rect(midtop=(WINDOW_WIDTH, pipe_height)))
            pipes.append(pipe_image.get_rect(midbottom=(WINDOW_WIDTH, pipe_height - PIPE_GAP)))

    if game_active:
        # Gestion des tuyaux après 50 points
        if score > 50 and pipes_visible:
            pipe_disappear_time = pygame.time.get_ticks()
            pipes_visible = False
        if pipe_disappear_time and not pipes_visible:
            if pygame.time.get_ticks() - pipe_disappear_time >= 6000:
                pipes_visible = True

        # Fond d'écran (défilement)
        screen.blit(background_image, (0, 0))

        # Mouvement de l'oiseau
        bird_movement += GRAVITY
        bird.centery += bird_movement

        # Rotation de l'oiseau
        rotated_bird = pygame.transform.rotate(bird_image, -bird_movement * 3)
        screen.blit(rotated_bird, bird)

        # Tuyaux
        pipes = move_pipes(pipes)
        draw_pipes(pipes)

        # Collisiond
        game_active = check_collision(pipes)

        # Score
        if not collision_occurred:
            for pipe in pipes:
                if pipe.centerx == bird.centerx:
                    score += 1
        display_score()
    else:
        if collision_occurred:
            screen.fill(WHITE)
            screen.blit(game_over_image, (WINDOW_WIDTH // 2 - game_over_image.get_width() // 2, WINDOW_HEIGHT // 2 - game_over_image.get_height() // 2))
            pygame.display.flip()
            collision_occurred = False

        main_menu()
        continue

    pygame.display.update()
    pygame.time.Clock().tick(120)
