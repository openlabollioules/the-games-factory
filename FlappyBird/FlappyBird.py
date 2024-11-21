import pygame
import random
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRAVITY = 0.6
FLAP_POWER = -10
PIPE_GAP = 200
PIPE_WIDTH = 80
PIPE_SPEED = 5

# Colors
WHITE = (255, 255, 255)

# Load assets
background_img = pygame.transform.scale(pygame.image.load("background.png"), (WIDTH, HEIGHT))
bird_img = pygame.image.load("bird.png")
pipe_img = pygame.transform.scale(pygame.image.load("pipe.png"), (PIPE_WIDTH, HEIGHT - 100))
rotated_pipe_img = pygame.transform.flip(pipe_img, False, True)
game_over_img = pygame.transform.scale(pygame.image.load("game_over.png"), (400, 200))

# Background music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Multiplayer")
clock = pygame.time.Clock()


# Bird class
class Bird:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(image, (50, 50))
        self.vel = 0
        self.score = 0
        self.alive = True

    def flap(self):
        if self.alive:
            self.vel = FLAP_POWER

    def update(self):
        if self.alive:
            self.vel += GRAVITY
            self.y += self.vel

            # Rotate bird based on velocity
            self.image_rotated = pygame.transform.rotate(self.image, -self.vel * 2)

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image_rotated, (self.x, self.y))

    def get_rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

    def check_collision(self, pipes):
        if self.y > HEIGHT or self.y < 0:
            self.alive = False
        for pipe in pipes:
            if self.get_rect().colliderect(pipe.get_rects()[0]) or self.get_rect().colliderect(pipe.get_rects()[1]):
                self.alive = False


# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(50, HEIGHT - PIPE_GAP - 150)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        screen.blit(pipe_img, (self.x, self.height + PIPE_GAP))
        screen.blit(rotated_pipe_img, (self.x, self.height - rotated_pipe_img.get_height()))

    def get_rects(self):
        bottom_pipe_rect = pipe_img.get_rect(topleft=(self.x, self.height + PIPE_GAP))
        top_pipe_rect = rotated_pipe_img.get_rect(topleft=(self.x, self.height - rotated_pipe_img.get_height()))
        return bottom_pipe_rect, top_pipe_rect


# Main menu
def main_menu():
    while True:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 74)
        text = font.render("Flappy Bird Multiplayer", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        one_player_text = font.render("1 Player", True, (0, 0, 0))
        two_player_text = font.render("2 Players", True, (0, 0, 0))
        quit_text = font.render("Quit", True, (0, 0, 0))

        screen.blit(one_player_text, (WIDTH // 2 - one_player_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(two_player_text, (WIDTH // 2 - two_player_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_loop(1)
                if event.key == pygame.K_2:
                    game_loop(2)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# Game loop
def game_loop(num_players):
    birds = [Bird(200, HEIGHT // 2, bird_img)]
    if num_players == 2:
        birds.append(Bird(300, HEIGHT // 2, bird_img))

    pipes = [Pipe(WIDTH + i * 300) for i in range(3)]
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(birds) > 0:
                    birds[0].flap()
                if num_players == 2 and event.key == pygame.K_LSHIFT and len(birds) > 1:
                    birds[1].flap()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.blit(background_img, (0, 0))

        # Update birds
        for bird in birds:
            bird.update()
            bird.check_collision(pipes)
            bird.draw(screen)

        # Update pipes
        for pipe in pipes:
            pipe.update()
            pipe.draw(screen)
            for bird in birds:
                if not pipe.passed and pipe.x < bird.x and bird.alive:
                    bird.score += 1
                    pipe.passed = True

        # Remove off-screen pipes and add new ones
        if pipes[0].x < -PIPE_WIDTH:
            pipes.pop(0)
            pipes.append(Pipe(WIDTH))

        # Check if game is over
        if all(not bird.alive for bird in birds):
            game_over = True

        # Draw scores
        font = pygame.font.Font(None, 74)
        for i, bird in enumerate(birds):
            if bird.alive or not bird.alive:
                score_text = font.render(f"Player {i + 1}: {bird.score}", True, (0, 0, 0))
                screen.blit(score_text, (10, 10 + i * 40))

        pygame.display.flip()
        clock.tick(60)

    # Display game over message
    screen.blit(game_over_img,
                (WIDTH // 2 - game_over_img.get_width() // 2, HEIGHT // 2 - game_over_img.get_height() // 2))
    # Display scores on game over
    for i, bird in enumerate(birds):
        score_text = font.render(f"Player {i + 1}: {bird.score}", True, (0, 0, 0))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + (i * 40) + 100))
    pygame.display.flip()
    pygame.time.wait(4000)

    main_menu()


# Start the game
main_menu()
