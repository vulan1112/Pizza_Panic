import os
import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🍕 Pizza Panic")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BG_COLOR = (200, 0, 0)

clock = pygame.time.Clock()

font_game = pygame.font.SysFont("Times New Roman", 30)
font_menu = pygame.font.SysFont("Times New Roman", 50, bold=True)
font_small_menu = pygame.font.SysFont("Times New Roman", 28)

# Load background image
try:
    background_image = pygame.image.load("assets/images/background.png").convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background_image = None
    print("Không thể tải background.png")

# Load nhạc nền
try:
    pygame.mixer.music.load("assets/sound/background_music.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
except:
    print("Không thể tải nhạc nền")

try:
    catch_sound = pygame.mixer.Sound("assets/sound/catch.wav")
    miss_sound = pygame.mixer.Sound("assets/sound/miss.wav")
except:
    catch_sound = miss_sound = pygame.mixer.Sound(buffer=b"\x00"*1000)

# Class Pizza
class Pizza(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.original_image, (205, 133, 63), (25, 25), 25)
        pygame.draw.circle(self.original_image, (255, 223, 0), (25, 25), 22)
        pygame.draw.circle(self.original_image, (255, 69, 0), (25, 25), 17)
        for _ in range(5):
            x = random.randint(10, 40)
            y = random.randint(10, 40)
            pygame.draw.circle(self.original_image, (178, 34, 34), (x, y), 3)
        for _ in range(2):
            sx = random.randint(5, 25)
            sy = random.randint(5, 35)
            pygame.draw.ellipse(self.original_image, (139, 0, 0), (sx, sy, 30, 6))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = speed
        self.angle = 0

    def update(self):
        self.rect.y += self.speed
        self.angle = (self.angle + 5) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            game_state['missed'] += 1
            miss_sound.play()

# Class Pan
class Pan(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((130, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (80, 80, 80), (0, 8, 130, 24))
        pygame.draw.ellipse(self.image, (50, 50, 50), (5, 13, 120, 14))
        pygame.draw.ellipse(self.image, (120, 120, 120), (10, 16, 30, 8))
        c_x = self.image.get_width() // 2
        c_y = self.image.get_height() // 2
        pygame.draw.circle(self.image, (80, 80, 80), (c_x, c_y), 12)
        pygame.draw.circle(self.image, (140, 140, 140), (c_x, c_y), 5)
        self.rect = self.image.get_rect()
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - self.rect.width // 2
        self.rect.clamp_ip(screen.get_rect())

def draw_small_pizza(x, y):
    pizza = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(pizza, (205, 133, 63), (15, 15), 15)
    pygame.draw.circle(pizza, (255, 223, 0), (15, 15), 12)
    pygame.draw.circle(pizza, (255, 69, 0), (15, 15), 8)
    screen.blit(pizza, (x, y))

def show_start_menu():
    screen.fill(BG_COLOR)
    positions = [(random.randint(0, SCREEN_WIDTH-30), random.randint(0, SCREEN_HEIGHT-30)) for _ in range(25)]
    for pos in positions:
        draw_small_pizza(*pos)
    title = font_menu.render(" Pizza Panic ", True, WHITE)
    start_msg = font_small_menu.render("Nhấn phím bất kỳ để chơi!", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 140))
    screen.blit(start_msg, (SCREEN_WIDTH//2 - start_msg.get_width()//2, 250))
    pygame.display.flip()
    wait_key()

def show_game_over_menu():
    screen.fill(BG_COLOR)
    positions = [(random.randint(0, SCREEN_WIDTH-30), random.randint(0, SCREEN_HEIGHT-30)) for _ in range(25)]
    for pos in positions:
        draw_small_pizza(*pos)
    over_msg = font_menu.render("GAME OVER!", True, WHITE)
    restart_msg = font_small_menu.render("Nhấn phím bất kỳ để chơi lại", True, WHITE)
    score_msg = font_small_menu.render(f"Điểm lượt vừa rồi: {game_state['score']}", True, WHITE)
    high_msg = font_small_menu.render(f"Điểm cao nhất: {best_score['high']}", True, WHITE)
    screen.blit(over_msg, (SCREEN_WIDTH//2 - over_msg.get_width()//2, 100))
    screen.blit(score_msg, (SCREEN_WIDTH//2 - score_msg.get_width()//2, 180))
    screen.blit(high_msg, (SCREEN_WIDTH//2 - high_msg.get_width()//2, 220))
    screen.blit(restart_msg, (SCREEN_WIDTH//2 - restart_msg.get_width()//2, 280))
    pygame.display.flip()
    wait_key()

def wait_key():
    waiting = True
    while waiting:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

def run_game():
    global game_state
    all_sprites = pygame.sprite.Group()
    pizza_group = pygame.sprite.Group()
    pan = Pan()
    all_sprites.add(pan)
    game_state = {'score': 0, 'missed': 0, 'speed': 3}
    ADD_PIZZA = pygame.USEREVENT + 1
    pygame.time.set_timer(ADD_PIZZA, 1000)
    running = True
    paused = False

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
            elif event.type == ADD_PIZZA and not paused:
                pizza = Pizza(game_state['speed'])
                all_sprites.add(pizza)
                pizza_group.add(pizza)

        if not paused:
            all_sprites.update()

            hits = pygame.sprite.spritecollide(pan, pizza_group, True)
            for hit in hits:
                game_state['score'] += 1
                catch_sound.play()
                if game_state['score'] % 5 == 0:
                    game_state['speed'] += 1

        # Vẽ background ảnh
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BG_COLOR)

        all_sprites.draw(screen)

        score_text = font_game.render(f"Điểm: {game_state['score']}", True, BLACK)
        miss_text = font_game.render(f"số pizza rớt: {game_state['missed']}", True, RED)
        screen.blit(score_text, (10, 10))
        screen.blit(miss_text, (10, 50))

        if paused:
            pause_msg = font_game.render("[Tạm dừng] Nhấn P để tiếp tục", True, WHITE)
            screen.blit(pause_msg, (SCREEN_WIDTH//2 - pause_msg.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.flip()

        if game_state['missed'] >= 3:
            if game_state['score'] > best_score['high']:
                best_score['high'] = game_state['score']
            running = False

    show_game_over_menu()

best_score = {'high': 0}

while True:
    show_start_menu()
    run_game()
