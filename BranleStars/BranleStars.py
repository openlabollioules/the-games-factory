import pygame
import sys
import random
import time

# Initialiser Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
POISON_COLOR = (0, 255, 0)  # Vert fluo

# Créer la fenêtre du jeu
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brawl Stars")
clock = pygame.time.Clock()

# Charger les ressources
bg_image = pygame.image.load("background.jpg")
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

player_skins = [
    pygame.image.load("player_skin1.png"),
    pygame.image.load("player_skin2.webp"),
    pygame.image.load("player_skin3.webp")
]
player_skins = [pygame.transform.scale(skin, (50, 50)) for skin in player_skins]

bot_image = pygame.image.load("bot.png")
bot_image = pygame.transform.scale(bot_image, (50, 50))

# Charger la musique
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self, skin):
        super().__init__()
        self.image = skin
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = 5000
        self.speed = 5
        self.last_damage_time = 0

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

    def regenerate_health(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > 3000:  # 3 secondes après avoir subi des dégâts
            self.health = min(self.health + 200, 5000)  # Régénérer jusqu'à 5000 max

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 5
        health_ratio = self.health / 5000

        # Barre rouge pour la santé perdue
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        # Barre verte pour la santé restante
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bot_image
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 5000
        self.speed = 2
        self.last_direction_change = pygame.time.get_ticks()
        self.last_damage_time = 0
        self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()

    def update(self, poison_rect):
        if self.health <= 0:
            self.kill()
        else:
            # Vérifier si le bot est proche de la zone de poison
            if not poison_rect.contains(self.rect):
                # Se déplacer dans une direction éloignant de la zone de poison
                if self.rect.left < poison_rect.left:
                    self.direction.x = 1
                elif self.rect.right > poison_rect.right:
                    self.direction.x = -1
                if self.rect.top < poison_rect.top:
                    self.direction.y = 1
                elif self.rect.bottom > poison_rect.bottom:
                    self.direction.y = -1

            # Modifier la direction aléatoirement toutes les 1,5 secondes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_direction_change > 1500:
                self.direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()
                self.last_direction_change = current_time

            # Appliquer la direction actuelle
            self.rect.x += int(self.direction.x * self.speed)
            self.rect.y += int(self.direction.y * self.speed)

            # Empêcher le bot de sortir de l'écran
            self.rect.clamp_ip(screen.get_rect())

    def regenerate_health(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > 3000:  # 3 secondes après avoir subi des dégâts
            self.health = min(self.health + 200, 5000)  # Régénérer jusqu'à 5000 max

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.centery, -10)

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 5
        health_ratio = self.health / 5000

        # Barre rouge pour la santé perdue
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        # Barre verte pour la santé restante
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, bar_width * health_ratio, bar_height))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

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
def draw_poison_zone(surface, rect):
    pygame.draw.rect(surface, POISON_COLOR, rect, 10)

def main_menu():
    selected_skin = 0
    while True:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        text = font.render("Brawl Stars", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        font = pygame.font.Font(None, 36)
        play_text = font.render("Press Enter to Play", True, WHITE)
        quit_text = font.render("Press Escape to Quit", True, WHITE)
        skin_text = font.render("Use Left/Right to Change Skin", True, WHITE)

        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))
        screen.blit(skin_text, (WIDTH // 2 - skin_text.get_width() // 2, HEIGHT // 2 + 100))

        # Afficher le skin sélectionné
        screen.blit(player_skins[selected_skin], (WIDTH // 2 - 25, HEIGHT // 2 - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return selected_skin
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LEFT:
                    selected_skin = (selected_skin - 1) % len(player_skins)
                if event.key == pygame.K_RIGHT:
                    selected_skin = (selected_skin + 1) % len(player_skins)

def game(selected_skin):
    player = Player(player_skins[selected_skin])
    bots = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bot_bullets = pygame.sprite.Group()

    # Créer des bots
    for _ in range(5):
        x, y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
        bots.add(Bot(x, y))

    all_sprites = pygame.sprite.Group(player, bots)

    eliminations = 0

    # Zone de poison initiale
    poison_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    poison_shrink_timer = pygame.time.get_ticks()
    poison_shrink_interval = 3000  # 3 secondes

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
        for bot in bots:
            bot.update(poison_rect)
            bot.regenerate_health()

        bullets.update()
        bot_bullets.update()

        # Les bots tirent sur le joueur
        for bot in bots:
            if random.randint(1, 100) == 1:  # Probabilité de tir
                bot_bullet = bot.shoot()
                bot_bullets.add(bot_bullet)
                all_sprites.add(bot_bullet)

        # Réduire la zone de poison toutes les 3 secondes
        current_time = pygame.time.get_ticks()
        if current_time - poison_shrink_timer > poison_shrink_interval:
            if poison_rect.width > 50 and poison_rect.height > 50:  # Ne pas rétrécir indéfiniment
                poison_rect.inflate_ip(-10, -10)  # Rétrécit vers le centre
            poison_shrink_timer = current_time

        # Appliquer les dégâts de poison
        if not poison_rect.contains(player.rect):
            player.health -= 500
            player.last_damage_time = pygame.time.get_ticks()
        for bot in bots:
            if not poison_rect.contains(bot.rect):
                bot.health -= 500
                bot.last_damage_time = pygame.time.get_ticks()

        # Régénération de santé
        player.regenerate_health()

        # Collision des balles avec les bots
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, bots, False)
            for hit in hits:
                hit.health -= 1000
                hit.last_damage_time = pygame.time.get_ticks()
                bullet.kill()
                if hit.health <= 0:
                    eliminations += 1

        # Collision des balles des bots avec le joueur
        if pygame.sprite.spritecollide(player, bot_bullets, True):
            player.health -= 1000
            player.last_damage_time = pygame.time.get_ticks()

        # Fin de partie
        if player.health <= 0:
            return "GAME OVER"
        if not bots:
            return "YOU WIN"

        # Affichage
        screen.blit(bg_image, (0, 0))
        player.draw(screen)
        for bot in bots:
            bot.draw(screen)

        # Dessiner la zone de poison
        draw_poison_zone(screen, poison_rect)

        # Dessiner les barres de santé
        player.draw_health_bar(screen)
        for bot in bots:
            bot.draw_health_bar(screen)

        # Afficher les tirs
        bullets.draw(screen)
        bot_bullets.draw(screen)

        # Afficher le nombre d'éliminations
        font = pygame.font.Font(None, 36)
        elim_text = font.render(f"Eliminations: {eliminations}", True, WHITE)
        screen.blit(elim_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    while True:
        selected_skin = main_menu()
        result = game(selected_skin)

        # Afficher le résultat de la partie
        screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        result_text = font.render(result, True, WHITE)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)

if __name__ == "__main__":
    main()
