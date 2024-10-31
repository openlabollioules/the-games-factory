import os
import pygame
import importlib.util

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 80, 60
CARDS_PER_ROW = 4
CARD_PADDING = 20

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("The Games Factory")
clock = pygame.time.Clock()

# Scan for games in subdirectories
def scan_for_games():
    games = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)
        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                if file.endswith(".py"):
                    game_script = os.path.join(subdir_path, file)
                    thumbnail_path = os.path.join(subdir_path, "thumbnail.png")
                    if os.path.isfile(game_script) and os.path.isfile(thumbnail_path):
                        try:
                            thumbnail = pygame.image.load(thumbnail_path)
                            thumbnail = pygame.transform.scale(thumbnail, (CARD_WIDTH, CARD_HEIGHT))
                            games.append({
                                'name': os.path.splitext(file)[0],
                                'script': game_script,
                                'thumbnail': thumbnail,
                                'directory': subdir_path
                            })
                        except pygame.error as e:
                            print(f"Error loading thumbnail for {subdir}: {e}")
    return games

# Main screen to display available games
def main_screen(games):
    scrolling_offset = 0
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col = (mouse_x - CARD_PADDING) // (CARD_WIDTH + CARD_PADDING)
                    row = (mouse_y + scrolling_offset - CARD_PADDING) // (CARD_HEIGHT + CARD_PADDING)
                    idx = row * CARDS_PER_ROW + col
                    if 0 <= idx < len(games):
                        run_game(games[idx]['script'], games[idx]['directory'])

        # Draw game cards
        y_offset = CARD_PADDING - scrolling_offset
        for i, game in enumerate(games):
            row = i // CARDS_PER_ROW
            col = i % CARDS_PER_ROW
            x = CARD_PADDING + col * (CARD_WIDTH + CARD_PADDING)
            y = CARD_PADDING + row * (CARD_HEIGHT + CARD_PADDING) - scrolling_offset
            if 0 <= y < WINDOW_HEIGHT:
                screen.blit(game['thumbnail'], (x, y))
                # Draw game name below the thumbnail
                font = pygame.font.Font(None, 24)
                text_surface = font.render(game['name'], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT + 10))
                screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(60)

# Run selected game
def run_game(script_path, game_directory):
    original_cwd = os.getcwd()
    os.chdir(game_directory)
    try:
        spec = importlib.util.spec_from_file_location("game_module", script_path)
        game_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(game_module)
        try:
            game_module.main()
        except SystemExit:
            pass  # Catch exit so we can return to main screen
    finally:
        os.chdir(original_cwd)

# Load games and start main loop
if __name__ == "__main__":
    games = scan_for_games()
    if not games:
        print("No games found. Please ensure there are subdirectories with a Python file and 'thumbnail.png'.")
    main_screen(games)
    pygame.quit()