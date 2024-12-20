import pygame
import sys
import random

# Initialiser Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Créer la fenêtre du jeu
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brawl Stars")
clock = pygame.time.Clock()

# Charger les ressources
bg_image = pygame.image.load("background.jpg")
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (50, 50))

bot_image = pygame.image.load("bot.png")
bot_image = pygame.transform.scale(bot_image, (50, 50))

# Charger la musique
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = 5000
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Empêcher le joueur de sortir de l'écran
        self.rect.clamp_ip(screen.get_rect())

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 5
        health_ratio = self.health / 5000
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bot_image
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 5000
        self.speed = random.choice([-2, 2])
        self.direction = random.choice(["horizontal", "vertical"])

    def update(self):
        if self.health <= 0:
            self.kill()
        else:
            if self.direction == "horizontal":
                self.rect.x += self.speed
                if self.rect.left < 0 or self.rect.right > WIDTH:
                    self.speed = -self.speed
            elif self.direction == "vertical":
                self.rect.y += self.speed
                if self.rect.top < 0 or self.rect.bottom > HEIGHT:
                    self.speed = -self.speed

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.centery, -10)

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 5
        health_ratio = self.health / 5000
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# Fonctions

def main_menu():
    while True:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        text = font.render("Brawl Stars", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        font = pygame.font.Font(None, 36)
        play_text = font.render("Press Enter to Play", True, WHITE)
        quit_text = font.render("Press Escape to Quit", True, WHITE)

        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def game():
    player = Player()
    bots = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bot_bullets = pygame.sprite.Group()

    # Créer des bots
    for _ in range(5):
        x, y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
        bots.add(Bot(x, y))

    all_sprites = pygame.sprite.Group(player, bots)

    eliminations = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.centery, 10)
                    bullets.add(bullet)
                    all_sprites.add(bullet)

        keys = pygame.key.get_pressed()
        player.update(keys)

        # Mise à jour des sprites
        bots.update()
        bullets.update()
        bot_bullets.update()

        # Les bots tirent
        for bot in bots:
            if random.randint(1, 100) == 1:  # Probabilité de tir
                bot_bullet = bot.shoot()
                bot_bullets.add(bot_bullet)
                all_sprites.add(bot_bullet)

        # Collision des balles avec les bots
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, bots, False)
            for hit in hits:
                hit.health -= 1000
                bullet.kill()

        # Collision des balles des bots avec le joueur
        if pygame.sprite.spritecollide(player, bot_bullets, True):
            player.health -= 1000

        # Fin de partie
        if player.health <= 0:
            return "GAME OVER"
        if not bots:
            return "YOU WIN"

        # Affichage
        screen.blit(bg_image, (0, 0))
        all_sprites.draw(screen)

        # Dessiner les barres de santé
        player.draw_health_bar(screen)
        for bot in bots:
            bot.draw_health_bar(screen)

        # Afficher le nombre d'éliminations
        font = pygame.font.Font(None, 36)
        elim_text = font.render(f"Eliminations: {eliminations}", True, WHITE)
        screen.blit(elim_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    while True:
        main_menu()
        result = game()

        # Afficher le résultat de la partie
        screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        result_text = font.render(result, True, WHITE)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)

if __name__ == "__main__":
    main()
