import pygame
import sys
import json
import time

# Initialiser Pygame
pygame.init()

# Charger la musique et la jouer en boucle
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.play(-1)

# Définir les dimensions de la fenêtre du jeu
WINDOW_WIDTH = 728
WINDOW_HEIGHT = 455

# Créer la fenêtre du jeu
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Jeu de plateformes inspiré de Super Mario Bros")

# Définir le framerate
FPS = 60
clock = pygame.time.Clock()

# Charger les images et les retailler
BACKGROUND_IMAGE = pygame.image.load('background.jpg').convert()
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WINDOW_WIDTH, WINDOW_HEIGHT))
PLAYER_IMAGE = pygame.image.load('player.png').convert_alpha()
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (50, 100))  # Redimensionner à 50x100 pixels
BLOCK_IMAGE = pygame.image.load('block.png').convert_alpha()
BLOCK_IMAGE = pygame.transform.scale(BLOCK_IMAGE, (50, 50))  # Redimensionner à 50x50 pixels
SURPRISE_BLOCK_IMAGE = pygame.image.load('surprise_block.jpg').convert_alpha()
SURPRISE_BLOCK_IMAGE = pygame.transform.scale(SURPRISE_BLOCK_IMAGE, (50, 50))  # Redimensionner à 50x50 pixels
ENEMY_IMAGE = pygame.image.load('enemy.png').convert_alpha()
ENEMY_IMAGE = pygame.transform.scale(ENEMY_IMAGE, (50, 50))  # Redimensionner à 50x50 pixels

# Définir les propriétés du personnage joueur
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100
PLAYER_START_X = 100
PLAYER_START_Y = WINDOW_HEIGHT - PLAYER_HEIGHT - 50
PLAYER_VELOCITY = 5
JUMP_VELOCITY = -20  # Ajusté pour permettre de sauter à 2 fois la hauteur du personnage
GRAVITY = 1

# Définir les propriétés des blocs
BLOCK_WIDTH = 50
BLOCK_HEIGHT = 50

# Définir les propriétés des ennemis
ENEMY_VELOCITY = 2

# Charger la disposition des blocs depuis un fichier JSON
def load_level(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Créer une classe pour le personnage joueur
class Player:
    def __init__(self):
        self.rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_y = 0
        self.on_ground = False
        self.scroll_x = 0

    def handle_movement(self):
        keys = pygame.key.get_pressed()

        # Mouvement gauche et droite
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_VELOCITY
            self.scroll_x -= PLAYER_VELOCITY
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_VELOCITY
            self.scroll_x += PLAYER_VELOCITY

        # Limiter la position du joueur à l'écran
        self.rect.x = max(200, min(self.rect.x, WINDOW_WIDTH - PLAYER_WIDTH))

        # Saut
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False

    def apply_gravity(self):
        # Appliquer la gravité
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Empêcher le joueur de tomber en dessous du sol
        if self.rect.bottom >= WINDOW_HEIGHT - 50:
            self.rect.bottom = WINDOW_HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True

    def check_collision(self, blocks, enemies):
        # Vérifier les collisions avec les blocs
        self.on_ground = False  # Réinitialiser l'état au début de chaque vérification
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.velocity_y > 0 and self.rect.bottom >= block.rect.top and self.rect.bottom <= block.rect.top + BLOCK_HEIGHT:
                    self.rect.bottom = block.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0 and self.rect.top <= block.rect.bottom:
                    self.rect.top = block.rect.bottom
                    self.velocity_y = 0
                    if block.is_surprise:
                        block.hit()
                        block.is_surprise = False  # Transformer en bloc normal

        # Empêcher le joueur de tomber en dessous du sol
        if self.rect.bottom >= WINDOW_HEIGHT - 50:
            self.rect.bottom = WINDOW_HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True

        # Vérifier les collisions avec les ennemis
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.velocity_y > 0 and self.rect.bottom >= enemy.rect.top:
                    enemies.remove(enemy)
                    print("Vous avez gagné une pièce d'or!")
                    self.velocity_y = JUMP_VELOCITY  # Rebondir après avoir sauté sur un ennemi
                else:
                    # Le joueur est touché par un ennemi - recommencer le niveau
                    print("Vous avez été touché par un ennemi! Recommencez le niveau.")
                    self.__init__()  # Réinitialiser la position du joueur

    def update(self, blocks, enemies):
        self.handle_movement()
        self.apply_gravity()
        self.check_collision(blocks, enemies)

    def draw(self, screen):
        screen.blit(PLAYER_IMAGE, self.rect)

# Créer une classe pour les blocs
class Block:
    def __init__(self, x, y, is_surprise=False):
        self.rect = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
        self.is_surprise = is_surprise
        self.hit_count = 0

    def hit(self):
        # Gérer le cas où un bloc surprise est frappé
        if self.is_surprise and self.hit_count == 0:
            print("Vous avez gagné une pièce d'or!")
            self.hit_count += 1

    def draw(self, screen, scroll_x):
        adjusted_rect = self.rect.move(-scroll_x, 0)
        image = SURPRISE_BLOCK_IMAGE if self.is_surprise else BLOCK_IMAGE
        screen.blit(image, adjusted_rect)

# Créer une classe pour les ennemis
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
        self.velocity = ENEMY_VELOCITY

    def update(self):
        # Déplacer l'ennemi horizontalement
        self.rect.x += self.velocity

        # Inverser la direction lorsque l'ennemi atteint les bords de la fenêtre
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.velocity = -self.velocity

    def draw(self, screen, scroll_x):
        adjusted_rect = self.rect.move(-scroll_x, 0)
        screen.blit(ENEMY_IMAGE, adjusted_rect)

# Boucle principale du jeu
def main():
    player = Player()
    blocks = []
    enemies = []

    # Charger les blocs depuis le fichier JSON
    level_data = load_level('niveau1.json')
    for block_data in level_data['blocks']:
        blocks.append(Block(block_data['x'], block_data['y'], block_data.get('is_surprise', False)))

    # Charger les ennemis depuis le fichier JSON
    for enemy_data in level_data['enemies']:
        enemies.append(Enemy(enemy_data['x'], enemy_data['y']))

    # Définir la limite de temps pour terminer le niveau
    start_time = time.time()
    time_limit = 60  # 60 secondes pour terminer le niveau

    # Définir la longueur du niveau
    level_end = 1500

    while True:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Calculer le temps restant
        elapsed_time = time.time() - start_time
        remaining_time = max(0, time_limit - int(elapsed_time))

        if remaining_time == 0:
            # Temps écoulé - recommencer le niveau
            print("Temps écoulé! Recommencez le niveau.")
            player = Player()
            start_time = time.time()

        # Mettre à jour le personnage joueur et les ennemis
        player.update(blocks, enemies)
        for enemy in enemies:
            enemy.update()

        # Vérifier si le joueur a atteint la fin du niveau
        if player.scroll_x >= level_end:
            print("Niveau terminé! Félicitations!")
            pygame.quit()
            sys.exit()

        # Dessiner le fond qui défile
        screen.fill((0, 0, 0))  # Effacer l'écran avant de redessiner
        screen.blit(BACKGROUND_IMAGE, (-player.scroll_x % WINDOW_WIDTH, 0))
        screen.blit(BACKGROUND_IMAGE, (-player.scroll_x % WINDOW_WIDTH - WINDOW_WIDTH, 0))

        # Dessiner le joueur, les blocs, et les ennemis
        player.draw(screen)
        for block in blocks:
            block.draw(screen, player.scroll_x)
        for enemy in enemies:
            enemy.draw(screen, player.scroll_x)

        # Afficher le temps restant
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f"Temps restant: {remaining_time}s", True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))

        # Mettre à jour l'écran
        pygame.display.flip()

        # Définir le framerate
        clock.tick(FPS)

# Lancer le jeu
if __name__ == "__main__":
    main()