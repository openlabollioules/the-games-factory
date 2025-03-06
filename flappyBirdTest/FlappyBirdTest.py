import pygame
import random

# Initialisation de pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
BIRD_Y_VELOCITY = -10
GRAVITY = 0.5
PIPE_GAP = 150
PIPE_WIDTH = 100
PIPE_SPEED = 3
BIRD_X = 200

# Charger les assets
bg_img = pygame.transform.scale(pygame.image.load("background.png"), (WIDTH, HEIGHT))
bird_img = pygame.transform.scale(pygame.image.load("bird.png"), (50, 35))  # Ajuster la taille de l'oiseau
pipe_img = pygame.transform.scale(pygame.image.load("pipe.png"), (PIPE_WIDTH, HEIGHT))
inverted_pipe_img = pygame.transform.flip(pipe_img, False, True)
game_over_img = pygame.image.load("gameover.png")

# Sons
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)


def main_menu():
    while True:
        screen.blit(bg_img, (0, 0))
        title_text = font.render("Flappy Bird", True, (255, 255, 255))
        start_text = font.render("Appuyez sur ESPACE pour jouer", True, (255, 255, 255))
        quit_text = font.render("Appuyez sur ESC pour quitter", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 150))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 250))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return


def game():
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes = []
    score = 0
    frame_count = 0
    running = True

    while running:
        screen.blit(bg_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = BIRD_Y_VELOCITY
                if event.key == pygame.K_ESCAPE:
                    return

        bird_velocity += GRAVITY
        bird_y += bird_velocity
        rotated_bird = pygame.transform.rotate(bird_img, -bird_velocity * 3)
        screen.blit(rotated_bird, (BIRD_X, bird_y))

        if frame_count % 100 == 0:
            pipe_height = random.randint(100, 400)
            pipes.append([WIDTH, pipe_height])

        for pipe in pipes:
            pipe[0] -= PIPE_SPEED
            screen.blit(pipe_img, (pipe[0], pipe[1] + PIPE_GAP))
            screen.blit(inverted_pipe_img, (pipe[0], pipe[1] - HEIGHT))
            if pipe[0] == BIRD_X:
                score += 1
            if (BIRD_X + bird_img.get_width() > pipe[0] and BIRD_X < pipe[0] + PIPE_WIDTH and
                    (bird_y < pipe[1] or bird_y + bird_img.get_height() > pipe[1] + PIPE_GAP)):
                game_over()
                return

        pipes = [pipe for pipe in pipes if pipe[0] > -PIPE_WIDTH]

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        if bird_y > HEIGHT:
            game_over()
            return

        frame_count += 1
        pygame.display.flip()
        clock.tick(30)


def game_over():
    screen.blit(game_over_img,
                (WIDTH // 2 - game_over_img.get_width() // 2, HEIGHT // 2 - game_over_img.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    main_menu()


main_menu()
