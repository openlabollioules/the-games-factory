import pygame
import random
import json

# Initialisation de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
FPS = 60

# Couleurs
WHITE = (255, 255, 255)

# Chargement des images
bg_image = pygame.image.load("background.png")  # Image personnalisée
player_image = pygame.image.load("character.png")  # Image personnalisée
coin_image = pygame.image.load("coin.png")  # Image de pièce
game_over_image = pygame.image.load("gameover.png")  # Image de Game Over
missile_image = pygame.image.load("missile.png")  # Image du missile

# Mise à l'échelle des images
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
player_image = pygame.transform.scale(player_image, (50, 50))
coin_image = pygame.transform.scale(coin_image, (30, 30))
game_over_image = pygame.transform.scale(game_over_image, (300, 200))
missile_image = pygame.transform.scale(missile_image, (40, 20))

# Musique de fond
pygame.mixer.music.load("background_music.mp3")  # Musique personnalisée
pygame.mixer.music.play(-1)  # Lecture en boucle

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jetpack Joyride Clone")
clock = pygame.time.Clock()


# Classe du joueur
class Player:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.width = 50
        self.height = 50
        self.velocity = 0
        self.gravity = 0.5
        self.fly_power = -8
        self.active = False

    def update(self, keys):
        if not self.active:
            return True
        if keys[pygame.K_SPACE]:
            self.velocity = self.fly_power
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y <= 0 or self.y + self.height >= HEIGHT:
            return False
        return True

    def draw(self, screen):
        screen.blit(player_image, (self.x, self.y))


# Classe pour les pièces
class Coin:
    def __init__(self):
        self.x = random.randint(WIDTH, WIDTH + 200)
        self.y = random.randint(50, HEIGHT - 50)
        self.width = 30
        self.height = 30
        self.collected = False

    def update(self):
        self.x -= 5
        return self.x > -self.width

    def draw(self, screen):
        if not self.collected:
            screen.blit(coin_image, (self.x, self.y))


# Classe pour les missiles
class Missile:
    def __init__(self):
        self.x = WIDTH + random.randint(100, 400)  # Moins de missiles, plus espacés
        self.y = random.randint(50, HEIGHT - 50)
        self.speed = 8  # Augmentation de la vitesse des missiles
        self.width = 40
        self.height = 20

    def update(self):
        self.x -= self.speed  # Déplacement de droite vers la gauche
        return self.x > -self.width

    def draw(self, screen):
        screen.blit(missile_image, (self.x, self.y))


# Fonction principale du jeu
def game_loop(player_name):
    player = Player()
    coins = [Coin() for _ in range(5)]
    missiles = []
    score = 0
    running = True
    bg_x = 0
    countdown = 5
    start_time = pygame.time.get_ticks()

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if keys[pygame.K_ESCAPE]:
                return

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        if elapsed_time < countdown:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 100)
            countdown_text = font.render(str(countdown - elapsed_time), True, WHITE)
            screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            continue
        else:
            player.active = True

        if not player.update(keys):
            screen.blit(game_over_image,
                        ((WIDTH - game_over_image.get_width()) // 2, (HEIGHT - game_over_image.get_height()) // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            return

        new_coins = []
        for coin in coins:
            if coin.update():
                new_coins.append(coin)
            if not coin.collected and player.x < coin.x + coin.width and player.x + player.width > coin.x and player.y < coin.y + coin.height and player.y + player.height > coin.y:
                score += 1
                coin.collected = True

        if len(new_coins) < 5:
            new_coins.append(Coin())
        coins = new_coins

        if random.randint(1, 100) > 99:  # Moins de missiles
            missiles.append(Missile())
        missiles = [missile for missile in missiles if missile.update()]

        for missile in missiles:
            if player.x < missile.x + missile.width and player.x + player.width > missile.x and player.y < missile.y + missile.height and player.y + player.height > missile.y:
                screen.blit(game_over_image,
                            ((WIDTH - game_over_image.get_width()) // 2, (HEIGHT - game_over_image.get_height()) // 2))
                pygame.display.flip()
                pygame.time.delay(2000)
                return

        bg_x -= 2
        if bg_x <= -WIDTH:
            bg_x = 0

        screen.blit(bg_image, (bg_x, 0))
        screen.blit(bg_image, (bg_x + WIDTH, 0))
        player.draw(screen)

        for coin in coins:
            coin.draw(screen)
        for missile in missiles:
            missile.draw(screen)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"{player_name} - Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()


# Menu principal
def main_menu():
    player_name = ""
    while True:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 50)
        title_text = font.render("Entrez votre nom: " + player_name, True, WHITE)
        screen.blit(title_text, (100, 250))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    game_loop(player_name)
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.unicode.isalnum():
                    player_name += event.unicode


# Lancer le menu principal
main_menu()
