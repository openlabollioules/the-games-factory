
import sys
import math
import os
import random
import struct
import tempfile
import wave
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knight Platformer - 3 niveaux")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 26)
BIG_FONT = pygame.font.SysFont("arial", 52, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 19)
PIXEL_FONT = pygame.font.SysFont("couriernew", 22, bold=True)

WHITE = (245, 245, 245)
BLACK = (18, 18, 22)
RED = (220, 60, 55)
DARK_RED = (125, 30, 35)
BLUE = (65, 145, 230)
YELLOW = (250, 210, 65)
GRAY = (120, 125, 140)
DARK_GRAY = (55, 60, 75)
PURPLE = (145, 85, 215)
ORANGE = (245, 112, 34)

THEMES = {
    "forest": {
        "sky": (26, 33, 52), "back": (42, 49, 75), "far": (55, 60, 75),
        "ground": (40, 120, 65), "top": (65, 190, 95),
        "fog": (35, 42, 64), "sun": (215, 220, 235),
    },
    "desert": {
        "sky": (225, 157, 86), "back": (193, 112, 62), "far": (150, 78, 54),
        "ground": (164, 104, 48), "top": (231, 181, 91),
        "fog": (203, 126, 66), "sun": (255, 226, 133),
    },
    "hell": {
        "sky": (35, 5, 12), "back": (82, 15, 22), "far": (125, 30, 22),
        "ground": (78, 35, 45), "top": (195, 55, 35),
        "fog": (52, 8, 14), "sun": (255, 80, 28),
    },
}

GRAVITY = 0.7
PLAYER_SPEED = 5
JUMP_SPEED = -14
DASH_SPEED = 14
DASH_DURATION = 10
DASH_COOLDOWN = 45
COYOTE_FRAMES = 7
JUMP_BUFFER_FRAMES = 9


# ---------------------------------------------------------------------------
# MUSIQUES 8-BIT GÉNÉRÉES PAR LE PROGRAMME
# ---------------------------------------------------------------------------
def square(freq, t):
    if freq <= 0:
        return 0.0
    return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0


def create_8bit_music(name, melody, bass, beat_duration, drum=False):
    sample_rate = 22050
    path = os.path.join(tempfile.gettempdir(), f"knight_{name}_8bit.wav")

    frames = bytearray()
    steps = max(len(melody), len(bass))

    for step in range(steps):
        lead_freq = melody[step % len(melody)]
        bass_freq = bass[step % len(bass)]
        count = int(sample_rate * beat_duration)

        for i in range(count):
            t = i / sample_rate
            envelope = min(1.0, i / 130, (count - i) / 260)
            lead = square(lead_freq, t) * 0.19
            low = square(bass_freq, t) * 0.10

            percussion = 0.0
            if drum and i < sample_rate * 0.035:
                # Petit bruit pseudo-aléatoire pour la percussion.
                noise = 1.0 if ((i * 1103515245 + step * 12345) & 512) else -1.0
                percussion = noise * (1 - i / (sample_rate * 0.035)) * 0.09

            value = int(32767 * max(-1, min(1, (lead + low + percussion) * envelope)))
            frames.extend(struct.pack("<h", value))

    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(frames)
    return path


MUSIC_DATA = {
    1: (
        "forest",
        [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 293.66, 349.23,
         440.00, 523.25, 440.00, 349.23, 329.63, 392.00, 293.66, 261.63],
        [130.81, 130.81, 196.00, 196.00, 146.83, 146.83, 174.61, 174.61],
        0.22, False,
    ),
    2: (
        "desert",
        [220.00, 261.63, 293.66, 329.63, 293.66, 261.63, 233.08, 220.00,
         174.61, 220.00, 261.63, 293.66, 261.63, 233.08, 220.00, 174.61],
        [110.00, 110.00, 146.83, 146.83, 98.00, 98.00, 130.81, 130.81],
        0.24, True,
    ),
    3: (
        "hellrock",
        [164.81, 164.81, 196.00, 164.81, 246.94, 220.00, 196.00, 146.83,
         164.81, 164.81, 196.00, 220.00, 246.94, 293.66, 246.94, 196.00],
        [82.41, 82.41, 98.00, 82.41, 123.47, 110.00, 98.00, 73.42],
        0.14, True,
    ),
}


def play_level_music(level):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        name, melody, bass, beat, drum = MUSIC_DATA[level]
        path = create_8bit_music(name, melody, bass, beat, drum)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.34 if level != 3 else 0.42)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def play_victory_music():
    """Jingle 8-bit joué une seule fois après le QTE final."""
    try:
        melody = [261.63, 329.63, 392.00, 523.25, 659.25, 523.25,
                  587.33, 659.25, 783.99, 1046.50, 783.99, 1046.50]
        bass = [130.81, 164.81, 196.00, 261.63, 196.00, 261.63]
        path = create_8bit_music("victory", melody, bass, 0.18, True)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.48)
        pygame.mixer.music.play(0)
    except pygame.error:
        pass


# ---------------------------------------------------------------------------
# OBJETS GÉNÉRAUX
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.enabled = enabled

    def draw(self, surface):
        hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        color = (65, 65, 72) if not self.enabled else (BLUE if hovered else DARK_GRAY)
        border = GRAY if not self.enabled else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=9)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=9)
        text = SMALL_FONT.render(self.text, True, border)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, camera_x, theme):
        rect = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, theme["ground"], rect)
        pygame.draw.rect(surface, theme["top"], (rect.x, rect.y, rect.width, 8))


class Flag:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 38, 110)

    def draw(self, surface, camera_x):
        x, y = self.rect.x - camera_x, self.rect.y
        pygame.draw.rect(surface, WHITE, (x + 8, y, 7, 110))
        pygame.draw.polygon(surface, YELLOW, [(x + 15, y + 5), (x + 55, y + 22), (x + 15, y + 40)])
        pygame.draw.rect(surface, GRAY, (x, y + 105, 28, 8))


class Enemy:
    def __init__(self, x, y, min_x, max_x):
        self.rect = pygame.Rect(x, y, 42, 38)
        self.speed = 2
        self.min_x = min_x
        self.max_x = max_x
        self.alive = True
        self.invincible = False

    def update(self):
        if not self.alive:
            return
        self.rect.x += self.speed
        if self.rect.left <= self.min_x:
            self.rect.left = self.min_x
            self.speed = abs(self.speed)
        if self.rect.right >= self.max_x:
            self.rect.right = self.max_x
            self.speed = -abs(self.speed)

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        rect = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, RED, rect, border_radius=7)
        pygame.draw.rect(surface, DARK_RED, (rect.x, rect.bottom - 9, rect.width, 9), border_radius=4)
        for eye_x in (rect.x + 12, rect.x + 30):
            pygame.draw.circle(surface, WHITE, (eye_x, rect.y + 13), 5)
            pygame.draw.circle(surface, BLACK, (eye_x, rect.y + 13), 2)


class SpikeEnemy(Enemy):
    def __init__(self, x, y, min_x, max_x):
        super().__init__(x, y, min_x, max_x)
        self.rect = pygame.Rect(x, y, 48, 42)
        self.speed = 1.7
        self.invincible = True

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        rect = self.rect.move(-camera_x, 0)
        spike_h = 11
        body = pygame.Rect(rect.x, rect.y + spike_h, rect.width, rect.height - spike_h)
        pygame.draw.rect(surface, (92, 78, 70), body, border_radius=7)
        pygame.draw.rect(surface, (55, 48, 45), (body.x, body.bottom - 9, body.width, 9), border_radius=4)

        spike_count = 5
        for i in range(spike_count):
            left = rect.x + i * rect.width / spike_count
            right = rect.x + (i + 1) * rect.width / spike_count
            center = (left + right) / 2
            pygame.draw.polygon(surface, WHITE, [
                (round(left), body.top + 1),
                (round(center), rect.y),
                (round(right), body.top + 1),
            ])

        for eye_x in (rect.x + 14, rect.x + 34):
            pygame.draw.circle(surface, YELLOW, (eye_x, rect.y + 26), 4)
            pygame.draw.circle(surface, BLACK, (eye_x, rect.y + 26), 2)


class Player:
    def __init__(self, x, y):
        self.spawn_x, self.spawn_y = x, y
        self.rect = pygame.Rect(x, y, 38, 52)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.facing = 1
        self.lives = 5
        self.invincibility = 0
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

    def reset_position(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.velocity_x = self.velocity_y = 0
        self.dash_timer = self.coyote_timer = self.jump_buffer_timer = 0

    def lose_life(self):
        if self.invincibility > 0:
            return
        self.lives -= 1
        self.invincibility = 90
        self.reset_position()

    def start_dash(self):
        if self.dash_cooldown <= 0 and self.dash_timer <= 0:
            self.dash_timer = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            self.velocity_y = 0

    def handle_input(self, keys):
        if self.dash_timer > 0:
            self.velocity_x = DASH_SPEED * self.facing
            return
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_a]:
            self.velocity_x = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = PLAYER_SPEED
            self.facing = 1

    def request_jump(self):
        self.jump_buffer_timer = JUMP_BUFFER_FRAMES

    def perform_buffered_jump(self):
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0 and self.dash_timer <= 0:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0

    def move_and_collide(self, platforms):
        self.rect.x += int(self.velocity_x)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

        if self.dash_timer <= 0:
            self.velocity_y = min(self.velocity_y + GRAVITY, 18)

        self.rect.y += int(self.velocity_y)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
        self.rect.left = max(0, self.rect.left)

    def update(self, platforms):
        self.invincibility = max(0, self.invincibility - 1)
        self.dash_cooldown = max(0, self.dash_cooldown - 1)
        self.dash_timer = max(0, self.dash_timer - 1)
        self.coyote_timer = max(0, self.coyote_timer - 1)
        self.jump_buffer_timer = max(0, self.jump_buffer_timer - 1)

        self.move_and_collide(platforms)
        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES
        self.perform_buffered_jump()

    def draw(self, surface, camera_x=0):
        if self.invincibility > 0 and (self.invincibility // 6) % 2 == 0:
            return

        rect = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, BLUE, rect, border_radius=7)

        if self.facing == 1:
            cape = (rect.x - 7, rect.y + 12, 9, rect.height - 16)
            eye = (rect.x + 27, rect.y + 15)
            nose = [(rect.right - 2, rect.y + 21), (rect.right + 6, rect.y + 25), (rect.right - 2, rect.y + 29)]
        else:
            cape = (rect.right - 2, rect.y + 12, 9, rect.height - 16)
            eye = (rect.x + 11, rect.y + 15)
            nose = [(rect.x + 2, rect.y + 21), (rect.x - 6, rect.y + 25), (rect.x + 2, rect.y + 29)]

        pygame.draw.rect(surface, PURPLE, cape, border_radius=4)
        pygame.draw.circle(surface, WHITE, eye, 5)
        pygame.draw.circle(surface, BLACK, eye, 2)
        pygame.draw.polygon(surface, (225, 175, 130), nose)


# ---------------------------------------------------------------------------
# BOSS DU NIVEAU 3
# ---------------------------------------------------------------------------
class Projectile:
    def __init__(self, x, y, vx, vy, kind="fire", gravity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.kind = kind
        self.radius = 8 if kind != "meteor" else 12
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2
        )

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        if self.x < -80 or self.x > WIDTH + 80 or self.y < -100 or self.y > HEIGHT + 100:
            self.alive = False

    def draw(self, surface):
        color = YELLOW if self.kind == "fire" else ORANGE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), max(3, self.radius - 4))
        if self.kind == "meteor":
            pygame.draw.line(surface, ORANGE, (int(self.x), int(self.y - 18)), (int(self.x), int(self.y - 5)), 5)


class BossHand:
    def __init__(self, x, y, side):
        self.base_x = x
        self.base_y = y
        self.side = side
        self.rect = pygame.Rect(x, y, 82, 42)
        self.health = 4
        self.vulnerable = False
        self.flash = 0

    @property
    def destroyed(self):
        return self.health <= 0

    def update_position(self, timer):
        if self.destroyed:
            return
        bob = int(math.sin(timer * 0.07 + (0 if self.side == "left" else math.pi)) * 8)
        self.rect.topleft = (self.base_x, self.base_y + bob)
        self.flash = max(0, self.flash - 1)

    def hit(self):
        if self.vulnerable and not self.destroyed and self.flash <= 0:
            self.health -= 1
            self.flash = 15
            return True
        return False

    def draw(self, surface):
        if self.destroyed:
            return
        color = WHITE if self.flash > 0 else ((245, 95, 50) if self.vulnerable else (105, 45, 50))
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        # Doigts pixelisés.
        for i in range(4):
            pygame.draw.rect(surface, color, (self.rect.x + 8 + i * 17, self.rect.y - 9, 11, 14))
        if self.vulnerable:
            pygame.draw.rect(surface, YELLOW, self.rect, 3, border_radius=10)


class HellBoss:
    QTE_KEYS = [pygame.K_a, pygame.K_z, pygame.K_e, pygame.K_r,
                pygame.K_q, pygame.K_s, pygame.K_d, pygame.K_f]
    QTE_NAMES = {
        pygame.K_a: "A", pygame.K_z: "Z", pygame.K_e: "E", pygame.K_r: "R",
        pygame.K_q: "Q", pygame.K_s: "S", pygame.K_d: "D", pygame.K_f: "F",
    }

    def __init__(self):
        self.timer = 0
        self.phase_timer = 0
        self.pattern_index = 0
        self.phase = 1
        self.patterns_phase_1 = ["fan", "rain", "sweep", "rest"]
        self.patterns_phase_2 = ["wide_gaps", "slow_orbits", "meteor_rows", "alternating_fire", "rest"]
        self.projectiles = []
        self.left_hand = BossHand(115, 300, "left")
        self.right_hand = BossHand(603, 300, "right")
        self.lava_y = 600.0
        self.qte_active = False
        self.qte_sequence = []
        self.qte_index = 0
        self.qte_timer = 0
        self.qte_max_time = 5 * FPS
        self.qte_error_flash = 0
        self.defeated = False
        self.victory_timer = 0
        self.victory_music_started = False
        self.intro_timer = 4 * FPS

    @property
    def patterns(self):
        return self.patterns_phase_1 if self.phase == 1 else self.patterns_phase_2

    def reset_pattern(self):
        self.phase_timer = 0
        self.pattern_index = (self.pattern_index + 1) % len(self.patterns)

    def aimed_shot(self, start_x, start_y, target_x, target_y, speed=5.2, kind="fire"):
        dx, dy = target_x - start_x, target_y - start_y
        length = max(1, math.hypot(dx, dy))
        self.projectiles.append(Projectile(start_x, start_y, dx / length * speed, dy / length * speed, kind))

    def start_qte(self):
        self.projectiles.clear()
        self.qte_active = True
        self.qte_sequence = random.sample(self.QTE_KEYS, 3)
        self.qte_index = 0
        self.qte_timer = self.qte_max_time
        self.left_hand.vulnerable = False
        self.right_hand.vulnerable = False

    def fail_qte(self, player):
        player.lose_life()
        self.qte_sequence = random.sample(self.QTE_KEYS, 3)
        self.qte_index = 0
        self.qte_timer = self.qte_max_time
        self.qte_error_flash = 30

    def handle_qte_key(self, key, player):
        if not self.qte_active or self.defeated:
            return
        expected = self.qte_sequence[self.qte_index]
        if key == expected:
            self.qte_index += 1
            if self.qte_index >= len(self.qte_sequence):
                self.qte_active = False
                self.defeated = True
                self.victory_timer = 0
                if not self.victory_music_started:
                    play_victory_music()
                    self.victory_music_started = True
        elif key in self.QTE_KEYS:
            self.fail_qte(player)

    def update_phase(self):
        remaining = max(0, self.left_hand.health) + max(0, self.right_hand.health)
        if self.phase == 1 and remaining <= 4:
            self.phase = 2
            self.pattern_index = 0
            self.phase_timer = 0
            self.projectiles.clear()
            # Les mains remontent légèrement pour rester accessibles depuis les plateformes.
            self.left_hand.base_y = 250
            self.right_hand.base_y = 250

    def add_wall_with_gap(self, from_left, gap_y):
        x = -20 if from_left else WIDTH + 20
        vx = 6.2 if from_left else -6.2
        for y in range(115, 485, 42):
            if abs(y - gap_y) > 58:
                self.projectiles.append(Projectile(x, y, vx, 0, "fire"))

    def update(self, player):
        self.timer += 1
        self.qte_error_flash = max(0, self.qte_error_flash - 1)

        if self.defeated:
            self.victory_timer += 1
            return

        if self.qte_active:
            self.qte_timer -= 1
            if self.qte_timer <= 0:
                self.fail_qte(player)
            return

        self.update_phase()
        self.left_hand.update_position(self.timer)
        self.right_hand.update_position(self.timer)

        # Quatre secondes de calme au début du combat pour laisser le joueur se placer.
        if self.intro_timer > 0:
            self.intro_timer -= 1
            self.left_hand.vulnerable = False
            self.right_hand.vulnerable = False
            return

        self.phase_timer += 1

        if self.phase == 2:
            self.lava_y = max(475.0, self.lava_y - 1.15)
            if player.rect.bottom >= self.lava_y:
                player.lose_life()

        if self.left_hand.destroyed and self.right_hand.destroyed:
            self.start_qte()
            return

        pattern = self.patterns[self.pattern_index]
        self.left_hand.vulnerable = pattern == "rest"
        self.right_hand.vulnerable = pattern == "rest"

        if pattern == "fan":
            if self.phase_timer % 38 == 1:
                for angle in (-28, -14, 0, 14, 28):
                    rad = math.radians(angle)
                    self.projectiles.append(Projectile(400, 175, math.sin(rad) * 5.3, math.cos(rad) * 5.3, "fire"))
            if self.phase_timer > 210:
                self.reset_pattern()

        elif pattern == "rain":
            if self.phase_timer % 24 == 1:
                safe_lane = (self.phase_timer // 24) % 5
                for lane in range(5):
                    if lane != safe_lane and random.random() < 0.72:
                        x = 100 + lane * 150 + random.randint(-25, 25)
                        self.projectiles.append(Projectile(x, -15, random.uniform(-0.5, 0.5), 4.5, "meteor", 0.07))
            if self.phase_timer > 220:
                self.reset_pattern()

        elif pattern == "sweep":
            if self.phase_timer in (30, 90, 150):
                direction = 1 if (self.phase_timer // 30) % 2 else -1
                start_x = -20 if direction == 1 else WIDTH + 20
                for y in (430, 315):
                    self.projectiles.append(Projectile(start_x, y, 7.0 * direction, 0, "fire"))
            if self.phase_timer % 70 == 35:
                self.aimed_shot(400, 170, player.rect.centerx, player.rect.centery, 6.0)
            if self.phase_timer > 220:
                self.reset_pattern()

        elif pattern == "wide_gaps":
            # Deux murs lents avec une très grande ouverture commune.
            if self.phase_timer in (35, 125):
                gap = 300 if self.phase_timer == 35 else 390
                x_left, x_right = -20, WIDTH + 20
                for y in range(145, 465, 48):
                    if abs(y - gap) > 95:
                        self.projectiles.append(Projectile(x_left, y, 4.6, 0, "fire"))
                        self.projectiles.append(Projectile(x_right, y, -4.6, 0, "fire"))
            if self.phase_timer > 215:
                self.reset_pattern()

        elif pattern == "slow_orbits":
            # Quelques tirs circulaires lents, espacés pour laisser des passages.
            if self.phase_timer % 28 == 1:
                base = self.phase_timer * 0.055
                for offset in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
                    angle = base + offset
                    self.projectiles.append(Projectile(400, 205, math.cos(angle) * 3.25, math.sin(angle) * 3.25, "fire"))
            if self.phase_timer > 210:
                self.reset_pattern()

        elif pattern == "meteor_rows":
            # Pluie en lignes avec deux couloirs sûrs au lieu d'un seul.
            if self.phase_timer % 58 == 1:
                safe_a = (self.phase_timer // 58) % 6
                safe_b = (safe_a + 3) % 6
                for lane in range(6):
                    if lane not in (safe_a, safe_b):
                        x = 65 + lane * 134
                        self.projectiles.append(Projectile(x, -20, 0, 4.3, "meteor", 0.025))
            if self.phase_timer > 220:
                self.reset_pattern()

        elif pattern == "alternating_fire":
            # Salves alternées : une attaque à la fois, avec avertissement et grand espace.
            if self.phase_timer in (40, 105, 170):
                high = (self.phase_timer // 65) % 2 == 0
                y = 260 if high else 420
                direction = 1 if self.phase_timer != 105 else -1
                start_x = -20 if direction == 1 else WIDTH + 20
                for offset in (-34, 34):
                    self.projectiles.append(Projectile(start_x, y + offset, 5.1 * direction, 0, "fire"))
            if self.phase_timer in (75, 140):
                # Un seul tir dirigé, suffisamment lent pour être esquivé.
                self.aimed_shot(400, 180, player.rect.centerx, player.rect.centery, 4.2)
            if self.phase_timer > 225:
                self.reset_pattern()

        elif pattern == "rest":
            if self.phase_timer == 1:
                self.projectiles.clear()
            limit = 165 if self.phase == 2 else 190
            if self.phase_timer > limit:
                self.reset_pattern()

        for projectile in self.projectiles:
            projectile.update()
            if projectile.alive and projectile.rect.colliderect(player.rect):
                player.lose_life()
                projectile.alive = False
        self.projectiles = [p for p in self.projectiles if p.alive]

    def handle_player_stomp(self, player):
        if self.qte_active or self.defeated:
            return
        for hand in (self.left_hand, self.right_hand):
            if hand.destroyed or not hand.vulnerable:
                continue
            if player.rect.colliderect(hand.rect):
                previous_bottom = player.rect.bottom - int(player.velocity_y)
                stomp = player.velocity_y > 0 and previous_bottom <= hand.rect.top + 14
                if stomp and hand.hit():
                    player.rect.bottom = hand.rect.top
                    player.velocity_y = -11
                    return

    def draw_lava(self, surface):
        if self.phase != 2:
            return
        y = int(self.lava_y)
        pygame.draw.rect(surface, RED, (0, y, WIDTH, HEIGHT - y))
        for x in range(-25, WIDTH + 25, 42):
            wave = int(math.sin(self.timer * 0.12 + x * 0.05) * 6)
            pygame.draw.circle(surface, ORANGE, (x, y + wave), 24)
        pygame.draw.line(surface, YELLOW, (0, y), (WIDTH, y), 4)

        if self.intro_timer > 0 and not self.qte_active and not self.defeated:
            seconds = math.ceil(self.intro_timer / FPS)
            ready = BIG_FONT.render(f"PRÉPARE-TOI... {seconds}", True, YELLOW)
            surface.blit(ready, ready.get_rect(center=(400, 265)))

    def draw_qte(self, surface):
        if not self.qte_active:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 0, 0, 175))
        surface.blit(overlay, (0, 0))
        title_color = RED if self.qte_error_flash else YELLOW
        title = BIG_FONT.render("COUP FINAL !", True, title_color)
        surface.blit(title, title.get_rect(center=(400, 175)))
        remaining_seconds = max(0, self.qte_timer / FPS)
        timer_text = FONT.render(f"Temps : {remaining_seconds:.1f} s", True, WHITE)
        surface.blit(timer_text, timer_text.get_rect(center=(400, 225)))

        start_x = 280
        for i, key in enumerate(self.qte_sequence):
            rect = pygame.Rect(start_x + i * 90, 280, 70, 70)
            done = i < self.qte_index
            current = i == self.qte_index
            color = (45, 145, 75) if done else ((200, 65, 40) if current else DARK_GRAY)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, rect, 3, border_radius=8)
            letter = BIG_FONT.render(self.QTE_NAMES[key], True, WHITE)
            surface.blit(letter, letter.get_rect(center=rect.center))

        instruction = SMALL_FONT.render("Appuie sur les 3 touches dans l'ordre avant la fin du temps !", True, WHITE)
        surface.blit(instruction, instruction.get_rect(center=(400, 390)))

    def draw(self, surface):
        color = (125, 20, 24) if self.phase == 2 else (88, 16, 23)
        pygame.draw.circle(surface, color, (400, 172), 125)
        pygame.draw.polygon(surface, (65, 10, 18), [(305, 105), (330, 15), (370, 85)])
        pygame.draw.polygon(surface, (65, 10, 18), [(430, 85), (475, 15), (495, 110)])
        eye_color = WHITE if self.defeated else YELLOW
        pygame.draw.circle(surface, eye_color, (355, 150), 15)
        pygame.draw.circle(surface, eye_color, (445, 150), 15)
        pygame.draw.rect(surface, BLACK, (348, 144, 14, 12))
        pygame.draw.rect(surface, BLACK, (438, 144, 14, 12))
        pygame.draw.rect(surface, BLACK, (350, 205, 100, 22), border_radius=5)
        for x in range(360, 445, 20):
            pygame.draw.polygon(surface, WHITE, [(x, 205), (x + 8, 219), (x + 16, 205)])

        self.left_hand.draw(surface)
        self.right_hand.draw(surface)
        for projectile in self.projectiles:
            projectile.draw(surface)

        remaining = max(0, self.left_hand.health) + max(0, self.right_hand.health)
        pygame.draw.rect(surface, DARK_GRAY, (210, 72, 380, 22))
        pygame.draw.rect(surface, RED, (214, 76, int(372 * remaining / 8), 14))
        label = SMALL_FONT.render(f"TITAN INFERNAL - PHASE {self.phase}", True, WHITE)
        surface.blit(label, label.get_rect(center=(400, 56)))

        if self.patterns[self.pattern_index] == "rest" and not self.qte_active and not self.defeated:
            message = PIXEL_FONT.render("POINTS FAIBLES OUVERTS !", True, YELLOW)
            surface.blit(message, message.get_rect(center=(400, 115)))
        if self.phase == 2 and not self.qte_active and not self.defeated:
            warning = SMALL_FONT.render("PHASE 2 : LE SOL EST EN LAVE !", True, ORANGE)
            surface.blit(warning, warning.get_rect(center=(400, 135)))

        self.draw_qte(surface)


# ---------------------------------------------------------------------------
# NIVEAUX
# ---------------------------------------------------------------------------
def create_level_1():
    platforms = [
        Platform(0, 520, 430, 80), Platform(500, 470, 180, 30),
        Platform(750, 405, 180, 30), Platform(1000, 500, 300, 100),
        Platform(1390, 445, 190, 30), Platform(1640, 370, 180, 30),
        Platform(1880, 475, 260, 30), Platform(2220, 405, 190, 30),
        Platform(2490, 500, 300, 100), Platform(2860, 430, 180, 30),
        Platform(3100, 355, 170, 30), Platform(3330, 500, 270, 100),
    ]
    enemies = [
        Enemy(560, 432, 510, 670), Enemy(1080, 462, 1010, 1280),
        Enemy(1450, 407, 1400, 1570), Enemy(1940, 437, 1890, 2130),
        Enemy(2560, 462, 2500, 2780), Enemy(3380, 462, 3340, 3580),
    ]
    return platforms, enemies, Flag(3510, 390), 3600, "forest"


def create_level_2():
    # Les plateformes des ennemis à piques ont été nettement agrandies.
    platforms = [
        Platform(0, 520, 320, 80),
        Platform(380, 465, 150, 30),
        Platform(590, 400, 230, 30),      # pique
        Platform(890, 335, 150, 30),
        Platform(1110, 455, 210, 30),
        Platform(1390, 520, 330, 80),     # pique

        Platform(1800, 445, 160, 30),
        Platform(2030, 365, 250, 30),     # pique
        Platform(2350, 285, 150, 30),
        Platform(2580, 390, 180, 30),
        Platform(2840, 500, 330, 100),    # pique

        Platform(3250, 430, 150, 30),
        Platform(3470, 350, 250, 30),     # pique
        Platform(3790, 270, 150, 30),
        Platform(4020, 390, 250, 30),     # pique
        Platform(4350, 480, 270, 120),

        Platform(4700, 410, 250, 30),     # pique
        Platform(5030, 330, 150, 30),
        Platform(5260, 250, 250, 30),     # pique
        Platform(5590, 370, 180, 30),
        Platform(5850, 500, 380, 100),
    ]

    enemies = [
        Enemy(415, 427, 390, 520),
        SpikeEnemy(650, 358, 600, 805),
        Enemy(925, 297, 900, 1025),
        Enemy(1155, 417, 1120, 1310),
        SpikeEnemy(1470, 478, 1400, 1700),
        Enemy(1585, 482, 1400, 1700),

        Enemy(1840, 407, 1810, 1950),
        SpikeEnemy(2100, 323, 2040, 2270),
        Enemy(2385, 247, 2360, 2490),
        Enemy(2625, 352, 2590, 2750),
        SpikeEnemy(2940, 458, 2850, 3160),
        Enemy(3050, 462, 2850, 3160),

        Enemy(3280, 392, 3260, 3390),
        SpikeEnemy(3545, 308, 3480, 3710),
        Enemy(3825, 232, 3800, 3930),
        SpikeEnemy(4090, 348, 4030, 4260),
        Enemy(4410, 442, 4360, 4610),

        SpikeEnemy(4770, 368, 4710, 4940),
        Enemy(4875, 372, 4710, 4940),
        Enemy(5065, 292, 5040, 5165),
        SpikeEnemy(5330, 208, 5270, 5500),
        Enemy(5625, 332, 5600, 5760),
        Enemy(5920, 462, 5860, 6220),
        SpikeEnemy(6060, 458, 5860, 6220),
    ]
    return platforms, enemies, Flag(6140, 390), 6230, "desert"


def create_level_3():
    # Arène entièrement suspendue : en phase 2, tomber entre les plateformes mène à la lave.
    platforms = [
        Platform(45, 470, 185, 28),
        Platform(305, 430, 190, 28),
        Platform(570, 470, 185, 28),
        Platform(95, 335, 145, 25),
        Platform(327, 300, 146, 25),
        Platform(560, 335, 145, 25),
    ]
    return platforms, [], None, 800, "hell"


# ---------------------------------------------------------------------------
# DÉCORS ET INTERFACE
# ---------------------------------------------------------------------------
def draw_background(surface, camera_x, theme_name):
    theme = THEMES[theme_name]
    surface.fill(theme["sky"])

    if theme_name == "hell":
        # Lave en mouvement et silhouettes de forteresse.
        for x in range(0, WIDTH, 80):
            height = 90 + ((x // 80) % 3) * 35
            pygame.draw.rect(surface, theme["back"], (x, 500 - height, 55, height))
            pygame.draw.polygon(surface, theme["far"], [(x, 500 - height), (x + 27, 455 - height), (x + 55, 500 - height)])
        for x in range(-40, WIDTH + 40, 70):
            wave_y = 505 + int(math.sin((pygame.time.get_ticks() / 180) + x) * 5)
            pygame.draw.circle(surface, ORANGE, (x, wave_y), 42)
        pygame.draw.rect(surface, RED, (0, 520, WIDTH, 80))
        return

    pygame.draw.circle(surface, theme["sun"], (680, 100), 45)
    offset = int(camera_x * 0.15) % 800
    for i in range(-1, 3):
        x = i * 800 - offset
        if theme_name == "desert":
            pygame.draw.polygon(surface, theme["back"], [(x, 500), (x + 200, 330), (x + 400, 500)])
            pygame.draw.polygon(surface, theme["far"], [(x + 290, 500), (x + 570, 285), (x + 800, 500)])
            cactus = (71, 112, 63)
            pygame.draw.rect(surface, cactus, (x + 120, 420, 14, 80), border_radius=5)
            pygame.draw.rect(surface, cactus, (x + 98, 446, 28, 12), border_radius=5)
            pygame.draw.rect(surface, cactus, (x + 98, 431, 12, 27), border_radius=5)
            pygame.draw.rect(surface, cactus, (x + 129, 454, 27, 12), border_radius=5)
            pygame.draw.rect(surface, cactus, (x + 144, 438, 12, 28), border_radius=5)
        else:
            pygame.draw.polygon(surface, theme["back"], [(x, 500), (x + 180, 250), (x + 370, 500)])
            pygame.draw.polygon(surface, theme["far"], [(x + 250, 500), (x + 520, 300), (x + 790, 500)])
    pygame.draw.rect(surface, theme["fog"], (0, 500, WIDTH, 100))


def draw_hud(surface, player, level_number):
    surface.blit(FONT.render(f"Vies : {player.lives}", True, WHITE), (20, 18))
    level_text = FONT.render(f"Niveau {level_number}", True, WHITE)
    surface.blit(level_text, level_text.get_rect(center=(WIDTH // 2, 30)))
    dash_text = "Dash prêt" if player.dash_cooldown <= 0 else "Recharge du dash"
    dash_color = YELLOW if player.dash_cooldown <= 0 else GRAY
    dash = SMALL_FONT.render(dash_text, True, dash_color)
    surface.blit(dash, (WIDTH - dash.get_width() - 20, 20))
    controls = SMALL_FONT.render("Q/D ou flèches : bouger | Espace : sauter | Shift : dash", True, WHITE)
    surface.blit(controls, (20, HEIGHT - 28))


def draw_standard_level(player, platforms, enemies, flag, camera_x, theme_name, level_number):
    theme = THEMES[theme_name]
    draw_background(screen, camera_x, theme_name)
    for platform in platforms:
        platform.draw(screen, camera_x, theme)
    for enemy in enemies:
        enemy.draw(screen, camera_x)
    flag.draw(screen, camera_x)
    player.draw(screen, camera_x)
    draw_hud(screen, player, level_number)


def draw_boss_level(player, platforms, boss):
    theme = THEMES["hell"]
    draw_background(screen, 0, "hell")
    boss.draw(screen)
    boss.draw_lava(screen)
    for platform in platforms:
        platform.draw(screen, 0, theme)
    player.draw(screen)
    draw_hud(screen, player, 3)

    if not boss.qte_active and not boss.defeated:
        hint = SMALL_FONT.render("Saute sur les mains lorsqu'elles brillent en jaune.", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 55)))


# ---------------------------------------------------------------------------
# BOUCLE PRINCIPALE
# ---------------------------------------------------------------------------
def main():
    state = "menu"
    level_2_unlocked = False
    level_3_unlocked = False
    current_level = 1
    secret_buffer = ""
    secret_message_timer = 0

    level1_button = Button(265, 225, 270, 48, "Niveau 1 - Forêt")
    level2_button = Button(265, 285, 270, 48, "Niveau 2 - verrouillé", False)
    level3_button = Button(265, 345, 270, 48, "Niveau 3 - verrouillé", False)
    quit_button = Button(265, 415, 270, 48, "Quitter")
    replay_button = Button(270, 340, 260, 60, "Rejouer")
    menu_button = Button(270, 420, 260, 60, "Menu principal")

    player = None
    platforms, enemies, flag = [], [], None
    camera_x = 0
    world_width = 3600
    theme_name = "forest"
    boss = None

    def start_level(number):
        nonlocal player, platforms, enemies, flag, camera_x
        nonlocal world_width, theme_name, current_level, boss

        current_level = number
        boss = None

        if number == 1:
            platforms, enemies, flag, world_width, theme_name = create_level_1()
            player = Player(70, 450)
        elif number == 2:
            platforms, enemies, flag, world_width, theme_name = create_level_2()
            player = Player(70, 450)
        else:
            platforms, enemies, flag, world_width, theme_name = create_level_3()
            player = Player(375, 365)
            boss = HellBoss()

        camera_x = 0
        play_level_music(number)

    running = True
    while running:
        clock.tick(FPS)

        secret_message_timer = max(0, secret_message_timer - 1)
        level2_button.enabled = level_2_unlocked
        level3_button.enabled = level_3_unlocked
        level2_button.text = "Niveau 2 - Désert" if level_2_unlocked else "Niveau 2 - verrouillé"
        level3_button.text = "Niveau 3 - Titan infernal" if level_3_unlocked else "Niveau 3 - verrouillé"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        secret_buffer = secret_buffer[:-1]
                    elif event.unicode and event.unicode.isalpha():
                        secret_buffer = (secret_buffer + event.unicode.lower())[-5:]
                        if secret_buffer == "messi":
                            level_2_unlocked = True
                            level_3_unlocked = True
                            secret_message_timer = 180
                            secret_buffer = ""

                if level1_button.clicked(event):
                    start_level(1)
                    state = "playing"
                elif level2_button.clicked(event):
                    start_level(2)
                    state = "playing"
                elif level3_button.clicked(event):
                    start_level(3)
                    state = "playing"
                elif quit_button.clicked(event):
                    running = False

            elif state == "playing" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    state = "menu"
                elif current_level == 3 and boss is not None and boss.qte_active:
                    boss.handle_qte_key(event.key, player)
                elif event.key == pygame.K_SPACE:
                    player.request_jump()
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    player.start_dash()

            elif state == "game_over":
                if replay_button.clicked(event):
                    start_level(current_level)
                    state = "playing"
                elif menu_button.clicked(event):
                    pygame.mixer.music.stop()
                    state = "menu"

        if state == "menu":
            screen.fill(THEMES["forest"]["sky"])
            title = BIG_FONT.render("KNIGHT PLATFORMER", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 105)))
            subtitle = SMALL_FONT.render("Termine chaque niveau pour débloquer le suivant", True, GRAY)
            screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 165)))
            secret_hint = SMALL_FONT.render("Un code secret peut être tapé directement au clavier...", True, GRAY)
            screen.blit(secret_hint, secret_hint.get_rect(center=(WIDTH // 2, 195)))
            if secret_message_timer > 0:
                unlocked = PIXEL_FONT.render("CODE ACCEPTÉ : TOUS LES NIVEAUX DÉBLOQUÉS !", True, YELLOW)
                screen.blit(unlocked, unlocked.get_rect(center=(WIDTH // 2, 500)))
            level1_button.draw(screen)
            level2_button.draw(screen)
            level3_button.draw(screen)
            quit_button.draw(screen)

        elif state == "playing":
            qte_freeze = current_level == 3 and boss is not None and boss.qte_active
            if qte_freeze:
                player.velocity_x = 0
            else:
                player.handle_input(pygame.key.get_pressed())
                player.update(platforms)

            if current_level in (1, 2):
                for enemy in enemies:
                    enemy.update()
                    if enemy.alive and player.rect.colliderect(enemy.rect):
                        previous_bottom = player.rect.bottom - int(player.velocity_y)
                        stomp = player.velocity_y > 0 and previous_bottom <= enemy.rect.top + 10
                        if stomp and not enemy.invincible:
                            enemy.alive = False
                            player.velocity_y = -9
                        else:
                            player.lose_life()

                if player.rect.top > HEIGHT + 120:
                    player.lose_life()

                if player.lives <= 0:
                    state = "game_over"
                elif player.rect.colliderect(flag.rect):
                    if current_level == 1:
                        level_2_unlocked = True
                    elif current_level == 2:
                        level_3_unlocked = True
                    pygame.mixer.music.stop()
                    state = "menu"

                target = max(0, min(player.rect.centerx - WIDTH // 2, world_width - WIDTH))
                camera_x += (target - camera_x) * 0.12
                camera_x = int(camera_x)
                draw_standard_level(player, platforms, enemies, flag, camera_x, theme_name, current_level)

            else:
                boss.update(player)
                boss.handle_player_stomp(player)

                if player.rect.top > HEIGHT + 120:
                    player.lose_life()

                if player.lives <= 0:
                    state = "game_over"
                elif boss.defeated and boss.victory_timer > 240:
                    pygame.mixer.music.stop()
                    state = "menu"

                draw_boss_level(player, platforms, boss)

                if boss.defeated:
                    victory = BIG_FONT.render("TITAN VAINCU !", True, YELLOW)
                    screen.blit(victory, victory.get_rect(center=(WIDTH // 2, 250)))
                    sub = FONT.render("QTE réussi - victoire !", True, WHITE)
                    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 310)))

        elif state == "game_over":
            screen.fill((25, 18, 24))
            title = BIG_FONT.render("GAME OVER", True, RED)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 220)))
            message = FONT.render("Les 5 vies ont été perdues.", True, WHITE)
            screen.blit(message, message.get_rect(center=(WIDTH // 2, 285)))
            replay_button.draw(screen)
            menu_button.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
