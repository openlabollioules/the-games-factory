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
GAME_SPEED = 5

# Initialisation de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Dash")

# Chargement du fond d'écran
background = pygame.image.load("background.jpg")  # Remplacez par le chemin de votre image
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

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
        self.jump_speed = 15
        self.gravity = 1
        self.velocity = 0

    def update(self):
        if self.jump:
            self.velocity = -self.jump_speed
            self.jump = False

        self.velocity += self.gravity
        self.y += self.velocity

        # Empêche le joueur de descendre sous le sol
        if self.y > SCREEN_HEIGHT - self.size - 10:
            self.y = SCREEN_HEIGHT - self.size - 10
            self.velocity = 0

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 128, 255), (self.x, self.y, self.size, self.size))

# Classe pour les obstacles
class Obstacle:
    def __init__(self):
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
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 100))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 150))
        screen.blit(leaderboard_text, (SCREEN_WIDTH // 2 - leaderboard_text.get_width() // 2, 200))

        # Afficher les scores des joueurs
        for i, (player_name, player_score) in enumerate(sorted(players.items(), key=lambda x: x[1], reverse=True)):
            score_text = font.render(f"{i + 1}. {player_name}: {player_score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 240 + i * 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    return "register"
                if event.key == pygame.K_s:
                    return "start"

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
    global GAME_SPEED
    clock = pygame.time.Clock()
    players = {}
    current_player = None

    while True:
        action = main_menu(players)
        if action == "register":
            register_player(players)
        elif action == "start":
            if not players:
                continue

            current_player = max(players, key=players.get)
            player = Player()
            obstacles = []
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
                            if player.y >= SCREEN_HEIGHT - player.size - 10:
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
                        obstacles.append(Obstacle())
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

            # Mise à jour du score du joueur
            players[current_player] = max(players[current_player], score)

if __name__ == "__main__":
    main()
