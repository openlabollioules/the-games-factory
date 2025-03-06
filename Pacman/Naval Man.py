import pygame
import random

# Initialisation de pygame
pygame.init()

# Définition des constantes
WIDTH, HEIGHT = 800, 800  # Agrandissement du background
GRID_SIZE = 50  # Augmentation de la taille des éléments pour un meilleur ajustement
FPS = 10

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Chargement des images
background_img = pygame.image.load("background.png")  # Remplacez par le chemin de votre image de fond
game_over_img = pygame.image.load("gameover.png")  # Image de Game Over
pacman_img = pygame.image.load("character.png")  # Remplacez par le chemin de votre personnage
pellet_img = pygame.image.load("pellet.png")  # Remplacez par le chemin de l'image des pastilles

# Redimensionnement des images
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
game_over_img = pygame.transform.scale(game_over_img, (300, 200))
pacman_size = (GRID_SIZE, GRID_SIZE)
pellet_size = (GRID_SIZE // 1.5, GRID_SIZE // 1.5)  # Augmentation de la taille des pastilles

pacman_img = pygame.transform.scale(pacman_img, pacman_size)
pellet_img = pygame.transform.scale(pellet_img, pellet_size)

# Chargement de la musique
pygame.mixer.music.load("background_music.mp3")  # Remplacez par le chemin de votre fichier audio
pygame.mixer.music.play(-1)  # Lecture en boucle

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")

# Police pour le score et le nom du joueur
font = pygame.font.Font(None, 36)


# Fonction pour entrer le nom du joueur
def get_player_name():
    name = ""
    entering_name = True
    while entering_name:
        screen.fill(BLACK)
        prompt_text = font.render("Entrez votre nom: " + name, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 4, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum():
                    name += event.unicode


# Définition du Pac-Man
class PacMan:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = 0
        self.dy = 0
        self.speed = GRID_SIZE // 2

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Vérifier si Pac-Man touche les bords de l'écran
        if self.x < 0 or self.x >= WIDTH or self.y < 0 or self.y >= HEIGHT:
            game_over()

    def draw(self):
        screen.blit(pacman_img, (self.x, self.y))


# Définition des pastilles
class Pellet:
    def __init__(self):
        self.x = random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE
        self.y = random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE

    def draw(self):
        screen.blit(pellet_img, (self.x + GRID_SIZE // 4, self.y + GRID_SIZE // 4))


# Fonction de fin de jeu
def game_over():
    screen.fill(BLACK)
    screen.blit(game_over_img, ((WIDTH - game_over_img.get_width()) // 2, (HEIGHT - game_over_img.get_height()) // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    main()


# Fonction principale pour démarrer le jeu
def main():
    pygame.mixer.music.play(-1)  # S'assurer que la musique tourne en boucle même après Game Over
    global player_name, pacman, pellets, score
    player_name = get_player_name()
    pacman = PacMan()
    pellets = [Pellet() for _ in range(10)]
    score = 0

    # Boucle de jeu
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.blit(background_img, (0, 0))

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman.dx = -pacman.speed
                    pacman.dy = 0
                elif event.key == pygame.K_RIGHT:
                    pacman.dx = pacman.speed
                    pacman.dy = 0
                elif event.key == pygame.K_UP:
                    pacman.dx = 0
                    pacman.dy = -pacman.speed
                elif event.key == pygame.K_DOWN:
                    pacman.dx = 0
                    pacman.dy = pacman.speed

        pacman.move()
        pacman.draw()

        # Dessiner les pastilles et vérifier la collision
        for pellet in pellets[:]:
            pellet.draw()
            if pacman.x == pellet.x and pacman.y == pellet.y:
                pellets.remove(pellet)
                pellets.append(Pellet())  # Ajouter une nouvelle pastille lorsqu'une est récupérée
                score += 1  # Incrémenter le score

        # Afficher le score et le nom du joueur
        score_text = font.render(f"{player_name} - Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


# Lancer le jeu
main()
