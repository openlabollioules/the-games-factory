import pygame
import random
import sys

pygame.init()

# Configuration de l'affichage et des couleurs
WIDTH, HEIGHT = 300, 600
ROWS, COLS = 20, 10
CELL_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Types de formes et leurs rotations
SHAPES = [
    [[[1], [1], [1], [1]]],  # I
    [[[1, 1], [1, 1]]],  # O
    [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],  # T
    [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],  # L
    [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],  # J
    [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],  # S
    [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]]  # Z
]

SHAPES_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Initialisation de la fenêtre de jeu
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

# Chargement de la musique de fond
pygame.mixer.music.load('background.mp3')
pygame.mixer.music.play(-1)

# Classe pour les pièces du jeu
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPES_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

# Création de la grille de jeu
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
    return grid

# Conversion des coordonnées de la pièce en cases de la grille
def convert_shape_format(piece):
    positions = []
    shape_format = piece.image()

    for i, line in enumerate(shape_format):
        for j, column in enumerate(line):
            if column == 1:
                positions.append((piece.x + j, piece.y + i))
    return positions

# Vérification des positions valides
def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(COLS) if grid[i][j] == BLACK] for i in range(ROWS)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] >= 0:
                return False
    return True

# Vérifier si une pièce est hors des limites de la grille
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

# Choisir une pièce aléatoire
def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

# Dessiner la grille de jeu
def draw_grid(surface, grid):
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j], (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    draw_grid_lines(surface)

# Dessiner les lignes de la grille
def draw_grid_lines(surface):
    for i in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))
    for j in range(COLS):
        pygame.draw.line(surface, GRAY, (j * CELL_SIZE, 0), (j * CELL_SIZE, HEIGHT))

# Effacer les lignes complétées
def clear_rows(grid, locked):
    increment = 0
    for i in range(ROWS - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            increment += 1
            ind = i
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + increment)
                locked[new_key] = locked.pop(key)
    return increment

# Dessiner la fenêtre de jeu
def draw_window(surface, grid, score, lines):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, WHITE)
    surface.blit(label, (10, 10))
    lines_label = font.render(f'Lines: {lines}', 1, WHITE)
    surface.blit(lines_label, (10, 40))

# Boucle principale du jeu
def main():
    locked_positions = {}
    grid = create_grid()
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    score = 0
    lines_cleared = 0
    fall_speed = 0.8
    fall_time = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)
        for pos in shape_pos:
            x, y = pos
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared = clear_rows(grid, locked_positions)
            score += cleared * 10
            lines_cleared += cleared
            if lines_cleared >= 10:
                fall_speed -= 0.02
                lines_cleared = 0

        draw_window(screen, grid, score, lines_cleared)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    pygame.display.quit()
    sys.exit()

if __name__ == '__main__':
    main()
