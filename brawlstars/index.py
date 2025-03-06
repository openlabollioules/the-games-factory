import pygame
import random

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
WIDTH, HEIGHT = 800, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexagon Force Clone")

# Chargement du fond
BACKGROUND = pygame.image.load("background.png")  # Remplacez par l'image de fond de votre choix
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Vitesse du jeu
GRAVITY = 0.8
JUMP_STRENGTH = -12
SPEED = 6
DUAL_MODE = False  # Mode double activé plus tard


# Classes
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_y = 0
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT - 40:
            self.rect.bottom = HEIGHT - 40
            self.on_ground = True

    def draw(self):
        pygame.draw.rect(SCREEN, BLUE, self.rect)


class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def update(self):
        self.rect.x -= SPEED

    def draw(self):
        pygame.draw.rect(SCREEN, RED, self.rect)


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def update(self):
        self.rect.x -= SPEED

    def draw(self):
        pygame.draw.rect(SCREEN, GREEN, self.rect)


def main():
    clock = pygame.time.Clock()
    player1 = Player(100, HEIGHT - 100)
    player2 = Player(100, HEIGHT - 160)  # Deuxième joueur pour mode dual
    obstacles = [Obstacle(WIDTH + i * 300, HEIGHT - 70, 30, 50) for i in range(3)]
    platforms = [Platform(WIDTH + 400, HEIGHT - 120, 100, 10)]
    running = True
    global DUAL_MODE

    while running:
        SCREEN.blit(BACKGROUND, (0, 0))  # Affichage du fond

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player1.jump()
                    if DUAL_MODE:
                        player2.jump()
                if event.key == pygame.K_d:
                    DUAL_MODE = not DUAL_MODE  # Active/Désactive le mode dual

        player1.update()
        player1.draw()

        if DUAL_MODE:
            player2.update()
            player2.draw()

        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw()
            if obstacle.rect.x < -30:
                obstacle.rect.x = WIDTH + random.randint(200, 400)

        for platform in platforms:
            platform.update()
            platform.draw()
            if platform.rect.x < -100:
                platform.rect.x = WIDTH + random.randint(200, 400)

        for obstacle in obstacles:
            if player1.rect.colliderect(obstacle.rect) or (DUAL_MODE and player2.rect.colliderect(obstacle.rect)):
                running = False
                print("Game Over!")

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
