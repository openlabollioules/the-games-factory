import pygame
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash - Simplifié")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Variables du joueur
player_size = 40
player_x = 100
player_y = HEIGHT - player_size
player_color = BLUE
player_velocity_y = 0
is_jumping = False
jump_power = 20  # Hauteur de saut augmentée
gravity = 1
is_ship_mode = False  # Mode "vaisseau"
ship_velocity_y = 0
ship_gravity = 0.5
ship_thrust = -10

# Charger l'image du vaisseau
ship_image = pygame.image.load("ship.jpg")
ship_image = pygame.transform.scale(ship_image, (player_size, player_size))

# Charger l'image de la porte
portal_image = pygame.image.load("portal.png")
portal_image = pygame.transform.scale(portal_image, (50, 50))

# Variables des obstacles
obstacle_speed = 5
obstacles = []
spawn_timer = 0
next_spawn_time = random.randint(60, 120)  # Temps aléatoire pour le prochain obstacle

# Variables des portes
portals = []
portal_size = 50
portal_spawn_time = 600
portal_timer = 0

# Variables de progression
speed_increase_interval = 300  # Intervalle pour augmenter la vitesse
frame_counter = 0  # Compteur de frames

# Horloge du jeu
clock = pygame.time.Clock()
FPS = 60


# Fonction pour générer un obstacle aléatoire
def generate_obstacle():
    shape_type = random.choice(["rect", "circle", "triangle"])
    x = WIDTH
    y = HEIGHT - random.randint(30, 70) if not is_ship_mode else random.randint(50, HEIGHT - 100)
    size = random.randint(20, 50)
    color = random.choice([RED, YELLOW])
    return {"type": shape_type, "x": x, "y": y, "size": size, "color": color}


# Fonction pour générer une porte
def generate_portal():
    x = WIDTH
    y = HEIGHT - portal_size - 10
    return {"x": x, "y": y, "size": portal_size}


# Fonction principale du jeu
def main():
    global player_y, player_velocity_y, is_jumping, spawn_timer, next_spawn_time, obstacle_speed, frame_counter
    global is_ship_mode, ship_velocity_y, portal_timer

    running = True
    while running:
        window.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Contrôle du joueur
        keys = pygame.key.get_pressed()
        if not is_ship_mode:
            if keys[pygame.K_UP] and not is_jumping:
                player_velocity_y = -jump_power
                is_jumping = True
        else:
            if keys[pygame.K_UP]:
                ship_velocity_y = ship_thrust

        # Appliquer la gravité
        if not is_ship_mode:
            player_velocity_y += gravity
            player_y += player_velocity_y
            if player_y >= HEIGHT - player_size:
                player_y = HEIGHT - player_size
                is_jumping = False
        else:
            ship_velocity_y += ship_gravity
            player_y += ship_velocity_y
            if player_y < 0:
                player_y = 0
            elif player_y > HEIGHT - player_size:
                player_y = HEIGHT - player_size

        # Gestion des obstacles
        spawn_timer += 1
        if spawn_timer > next_spawn_time:
            obstacles.append(generate_obstacle())
            spawn_timer = 0
            next_spawn_time = random.randint(60, 120)

        for obstacle in obstacles[:]:
            obstacle["x"] -= obstacle_speed
            if obstacle["x"] + obstacle.get("size", 40) < 0:
                obstacles.remove(obstacle)

        # Gestion des portes
        portal_timer += 1
        if portal_timer > portal_spawn_time:
            portals.append(generate_portal())
            portal_timer = 0

        for portal in portals[:]:
            portal["x"] -= obstacle_speed
            if portal["x"] + portal["size"] < 0:
                portals.remove(portal)

            # Collision avec la porte
            if (player_x < portal["x"] + portal["size"] and
                    player_x + player_size > portal["x"] and
                    player_y < portal["y"] + portal["size"] and
                    player_y + player_size > portal["y"]):
                is_ship_mode = not is_ship_mode
                portals.remove(portal)

        # Augmenter progressivement la vitesse
        frame_counter += 1
        if frame_counter % speed_increase_interval == 0:
            obstacle_speed += 1

        # Détection des collisions
        for obstacle in obstacles:
            if obstacle["type"] == "rect":
                if (player_x < obstacle["x"] + obstacle["size"] and
                        player_x + player_size > obstacle["x"] and
                        player_y < obstacle["y"] + obstacle["size"] and
                        player_y + player_size > obstacle["y"]):
                    running = False
            elif obstacle["type"] == "circle":
                circle_center = (obstacle["x"] + obstacle["size"] // 2, obstacle["y"] + obstacle["size"] // 2)
                player_center = (player_x + player_size // 2, player_y + player_size // 2)
                distance = ((circle_center[0] - player_center[0]) ** 2 + (
                            circle_center[1] - player_center[1]) ** 2) ** 0.5
                if distance < (obstacle["size"] // 2 + player_size // 2):
                    running = False
            elif obstacle["type"] == "triangle":
                triangle_points = [(obstacle["x"], obstacle["y"] + obstacle["size"]),
                                   (obstacle["x"] + obstacle["size"] // 2, obstacle["y"]),
                                   (obstacle["x"] + obstacle["size"], obstacle["y"] + obstacle["size"])]
                player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
                if player_rect.collidepoint(triangle_points[0]) or player_rect.collidepoint(
                        triangle_points[1]) or player_rect.collidepoint(triangle_points[2]):
                    running = False

        # Dessiner le joueur
        if not is_ship_mode:
            pygame.draw.rect(window, player_color, (player_x, player_y, player_size, player_size))
        else:
            window.blit(ship_image, (player_x, player_y))

        # Dessiner les obstacles
        for obstacle in obstacles:
            if obstacle["type"] == "rect":
                pygame.draw.rect(window, obstacle["color"],
                                 (obstacle["x"], obstacle["y"], obstacle["size"], obstacle["size"]))
            elif obstacle["type"] == "circle":
                pygame.draw.circle(window, obstacle["color"],
                                   (obstacle["x"] + obstacle["size"] // 2, obstacle["y"] + obstacle["size"] // 2),
                                   obstacle["size"] // 2)
            elif obstacle["type"] == "triangle":
                triangle_points = [(obstacle["x"], obstacle["y"] + obstacle["size"]),
                                   (obstacle["x"] + obstacle["size"] // 2, obstacle["y"]),
                                   (obstacle["x"] + obstacle["size"], obstacle["y"] + obstacle["size"])]
                pygame.draw.polygon(window, obstacle["color"], triangle_points)

        # Dessiner les portes
        for portal in portals:
            window.blit(portal_image, (portal["x"], portal["y"]))

        # Mettre à jour l'écran
        pygame.display.flip()

        # Contrôler le FPS
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
