import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
LARGEUR, HAUTEUR = 800, 600
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Mini Brawl Stars")

# Couleurs
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
NOIR = (0, 0, 0)

# Classe Joueur
class Joueur(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLEU)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vitesse = 5
        self.sante = 100

    def deplacer(self):
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.vitesse
        if touches[pygame.K_RIGHT] and self.rect.right < LARGEUR:
            self.rect.x += self.vitesse
        if touches[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.vitesse
        if touches[pygame.K_DOWN] and self.rect.bottom < HAUTEUR:
            self.rect.y += self.vitesse

    def afficher_sante(self, surface):
        pygame.draw.rect(surface, ROUGE, (self.rect.x, self.rect.y - 10, 50, 5))
        pygame.draw.rect(surface, VERT, (self.rect.x, self.rect.y - 10, 50 * (self.sante / 100), 5))

# Classe Projectile
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, tireur):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(ROUGE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vitesse = 7 * direction
        self.tireur = tireur  # Pour savoir qui a tiré

    def update(self):
        self.rect.x += self.vitesse
        if self.rect.right < 0 or self.rect.left > LARGEUR:
            self.kill()

# Classe Bot
class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(ROUGE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vitesse = 3
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.last_shot = pygame.time.get_ticks()

    def deplacer(self):
        self.rect.x += self.vitesse * self.direction_x
        self.rect.y += self.vitesse * self.direction_y

        if self.rect.left <= 0 or self.rect.right >= LARGEUR:
            self.direction_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= HAUTEUR:
            self.direction_y *= -1

    def tirer(self):
        maintenant = pygame.time.get_ticks()
        if maintenant - self.last_shot > 2000:  # Tir toutes les 2 secondes
            self.last_shot = maintenant
            return Projectile(self.rect.centerx, self.rect.centery, -1, self)

# Initialisation des groupes
joueur = Joueur(LARGEUR // 2, HAUTEUR // 2)
projectiles = pygame.sprite.Group()
ennemis = pygame.sprite.Group()
tous_les_sprites = pygame.sprite.Group()
tous_les_sprites.add(joueur)

# Ajouter des bots
for _ in range(3):
    bot = Bot(random.randint(50, LARGEUR - 50), random.randint(50, HAUTEUR - 50))
    ennemis.add(bot)
    tous_les_sprites.add(bot)

# Système de score
score = 0

# Boucle principale
clock = pygame.time.Clock()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Tirer un projectile
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                projectile = Projectile(joueur.rect.centerx, joueur.rect.centery, 1, joueur)
                projectiles.add(projectile)
                tous_les_sprites.add(projectile)

    # Mettre à jour les sprites
    joueur.deplacer()
    projectiles.update()
    for bot in ennemis:
        bot.deplacer()
        tir = bot.tirer()
        if tir:
            projectiles.add(tir)
            tous_les_sprites.add(tir)

    # Vérifier les collisions
    for projectile in projectiles:
        if projectile.tireur != joueur and projectile.rect.colliderect(joueur.rect):
            joueur.sante -= 10
            projectile.kill()
        for bot in ennemis:
            if projectile.tireur == joueur and projectile.rect.colliderect(bot.rect):
                bot.kill()
                projectile.kill()
                score += 1

    if joueur.sante <= 0:
        print(f"Game Over! Score final: {score}")
        run = False

    # Dessiner tout
    fenetre.fill(BLANC)
    tous_les_sprites.draw(fenetre)
    joueur.afficher_sante(fenetre)

    # Afficher le score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, NOIR)
    fenetre.blit(score_text, (10, 10))

    # Rafraîchir l'écran
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
