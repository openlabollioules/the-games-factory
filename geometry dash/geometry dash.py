import pygame
import random

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Vitesse initiale de jeu
INITIAL_GAME_SPEED = 5
GAME_SPEED = INITIAL_GAME_SPEED

# Initialisation de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Dash")

# Chargement du fond d'écran
background_square = pygame.image.load("background.jpg")
background_rocket = pygame.image.load("backround2.jpg")
background_square = pygame.transform.scale(background_square, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_rocket = pygame.transform.scale(background_rocket, (SCREEN_WIDTH, SCREEN_HEIGHT))
background = background_square

# Chargement des images du portail et de la fusée
portal_image = pygame.image.load("portai l.png")
portal_image = pygame.transform.scale(portal_image, (40, 40))

rocket_image = pygame.image.load("fusee.png")
rocket_image = pygame.transform.scale(rocket_image, (30, 30))

# Chargement de la musique
pygame.mixer.music.load("Taking Flight (1).mp3")  # Remplacez par le chemin de votre fichier musical
pygame.mixer.music.set_volume(0.5)  # Volume de la musique
pygame.mixer.music.play(-1)  # Lecture en boucle

# Police pour le texte
font = pygame.font.Font(None, 36)

# Classe pour le joueur
class Player:
    def __init__(self):
        self.size = 30
        self.x = 100
        self.y = SCREEN_HEIGHT - self.size - 10
        self.jump = False
        self.gravity = 1
        self.velocity = 0
        self.is_rocket = False

    def update(self):
        if self.is_rocket:
            self.velocity += self.gravity / 2  # Gravité réduite pour la fusée
            self.y += self.velocity
            self.y = max(0, min(self.y, SCREEN_HEIGHT - self.size))  # Limites de l'écran
        else:
            if self.jump:
                self.velocity = -15
                self.jump = False

            self.velocity += self.gravity
            self.y += self.velocity

            # Empêche le joueur de descendre sous le sol
            if self.y > SCREEN_HEIGHT - self.size - 10:
                self.y = SCREEN_HEIGHT - self.size - 10
                self.velocity = 0

    def draw(self, screen):
        if self.is_rocket:
            screen.blit(rocket_image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (0, 128, 255), (self.x, self.y, self.size, self.size))

# Classe pour les portails
class Portal:
    def __init__(self):
        self.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 800)
        self.y = SCREEN_HEIGHT - 40
        self.width = 40
        self.height = 40

    def update(self):
        self.x -= GAME_SPEED

    def draw(self, screen):
        screen.blit(portal_image, (self.x, self.y))

# Classe pour les obstacles
class Obstacle:
    def __init__(self, level):
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - 50
        self.width = random.randint(20, 50)
        self.height = random.randint(20, 50)
        self.type = random.choice(["rectangle", "circle", "triangle"])
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )
        if level == 2:
            self.distance = random.randint(100, 200)
            self.width = random.randint(20, 70)  # Variété de tailles plus larges
        else:
            self.distance = 200

    def update(self):
        self.x -= GAME_SPEED

    def draw(self, screen):
        if self.type == "rectangle":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        elif self.type == "circle":
            pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)
        elif self.type == "triangle":
            pygame.draw.polygon(screen, self.color, [
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height),
                (self.x + self.width // 2, self.y),
            ])

# Afficher le menu principal
def main_menu(players):
    while True:
        screen.fill(BLACK)
        title_text = font.render("Geometry Dash - Main Menu", True, WHITE)
        instruction_text = font.render("Press N to register a new player", True, WHITE)
        start_text = font.render("Press S to start the game", True, WHITE)
        leaderboard_text = font.render("Leaderboard:", True, WHITE)
        level_text = font.render("Press 1 or 2 to select level", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 100))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 150))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 200))
        screen.blit(leaderboard_text, (SCREEN_WIDTH // 2 - leaderboard_text.get_width() // 2, 250))

        # Afficher les scores des joueurs
        for i, (player_name, player_score) in enumerate(sorted(players.items(), key=lambda x: x[1], reverse=True)):
            score_text = font.render(f"{i + 1}. {player_name}: {player_score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300 + i * 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    return "register", 1
                if event.key == pygame.K_s:
                    return "start", 1
                if event.key == pygame.K_1:
                    return "start", 1
                if event.key == pygame.K_2:
                    return "start", 2

# Fonction d'enregistrement des joueurs
def register_player(players):
    input_active = True
    player_name = ""

    while input_active:
        screen.fill(BLACK)
        instruction_text = font.render("Enter your name: " + player_name, True, WHITE)
        screen.blit(instruction_text, (50, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    if player_name not in players:
                        players[player_name] = 0
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

# Afficher un compte à rebours avant de commencer
def countdown():
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        countdown_text = font.render(str(i), True, WHITE)
        screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2 - countdown_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(1000)

# Fonction principale du jeu
def main():
    global GAME_SPEED, background
    clock = pygame.time.Clock()
    players = {}
    current_player = None

    while True:
        action, level = main_menu(players)
        if action == "register":
            register_player(players)
        elif action == "start":
            if not players:
                continue

            GAME_SPEED = INITIAL_GAME_SPEED  # Réinitialiser la vitesse à celle de base
            current_player = max(players, key=players.get)
            player = Player()
            obstacles = []
            portals = [Portal() for _ in range(3)]
            running = True
            paused = False
            spawn_timer = 0
            score = 0

            countdown()  # Ajouter le compte à rebours avant de commencer

            while running:
                screen.blit(background, (0, 0))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not paused:
                            if player.is_rocket:
                                player.velocity = -5
                            elif player.y >= SCREEN_HEIGHT - player.size - 10:
                                player.jump = True
                        elif event.key == pygame.K_p:
                            paused = not paused

                if not paused:
                    # Mettre à jour le joueur
                    player.update()
                    player.draw(screen)

                    # Génération des obstacles
                    spawn_timer += 1
                    if spawn_timer > 60:  # Un obstacle toutes les 60 frames environ
                        obstacles.append(Obstacle(level))
                        spawn_timer = 0

                    # Mettre à jour les obstacles
                    for obstacle in obstacles[:]:
                        obstacle.update()
                        obstacle.draw(screen)

                        # Supprimer les obstacles hors écran et incrémenter le score
                        if obstacle.x + obstacle.width < 0:
                            obstacles.remove(obstacle)
                            score += 1

                        # Détection de collision
                        if (
                            player.x < obstacle.x + obstacle.width
                            and player.x + player.size > obstacle.x
                            and player.y < obstacle.y + obstacle.height
                            and player.y + player.size > obstacle.y
                        ):
                            running = False

                    # Mettre à jour les portails
                    for portal in portals[:]:
                        portal.update()
                        portal.draw(screen)

                        # Détection de collision avec le portail
                        if (
                            player.x < portal.x + portal.width
                            and player.x + player.size > portal.x
                            and player.y + player.size > portal.y
                            and player.y < portal.y + portal.height
                        ):
                            player.is_rocket = not player.is_rocket
                            background = background_rocket if player.is_rocket else background_square
                            portals.remove(portal)
                            portals.append(Portal())

                    # Augmenter la vitesse du jeu
                    if score > 0 and score % 3 == 0:
                        GAME_SPEED += 0.1

                # Afficher le texte en pause
                if paused:
                    pause_text = font.render("Game Paused - Press P to Resume", True, WHITE)
                    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
                else:
                    # Afficher le score
                    score_text = font.render(f"Score: {score}", True, WHITE)
                    screen.blit(score_text, (10, 10))

                pygame.display.flip()
                clock.tick(30)

            # Afficher le score final
            screen.fill(BLACK)
            game_over_text = font.render("Game Over!", True, WHITE)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get))

 # Mise à jour du score du joueur
            players[current_player] = max(players[current_player], score)

if __name__ == "__main__":
    main()
