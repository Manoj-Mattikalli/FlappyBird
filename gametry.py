import pygame
from pygame.locals import *
import random
import sys
import json
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)
small_font = pygame.font.SysFont('Arial', 40)

# Define colours
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
blue = (0, 0, 255)

# Define game variables
ground_scroll = 0
scroll_speed = 6
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
player_name = ""

# File path for storing scores
score_file = 'scores.json'

# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
button_quit_img = pygame.image.load('img/quit.png')

# Resize buttons for consistent size
button_img = pygame.transform.scale(button_img, (150, 75))
button_quit_img = pygame.transform.scale(button_quit_img, (150, 75))

# Calculate button positions
button_width, button_height = button_img.get_width(), button_img.get_height()
button_x = (screen_width - button_width) // 2
button_y = (screen_height - button_height) // 2 - 100
quit_button_x = (screen_width - button_width) // 2
quit_button_y = (screen_height - button_height) // 2 + 50

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    return 0

def load_scores():
    """Load scores from a JSON file."""
    if os.path.exists(score_file):
        with open(score_file, 'r') as file:
            return json.load(file)
    return {}

def save_scores(scores):
    """Save scores to a JSON file."""
    with open(score_file, 'w') as file:
        json.dump(scores, file, indent=4)

def update_score(player_name, score):
    """Update the player's score and high score."""
    scores = load_scores()
    if player_name not in scores:
        scores[player_name] = {'high_score': 0, 'history': []}
    scores[player_name]['history'].append(score)
    scores[player_name]['high_score'] = max(scores[player_name]['high_score'], score)
    save_scores(scores)
    return scores[player_name]['high_score']

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

button = Button(button_x, button_y, button_img)
quit_button = Button(quit_button_x, quit_button_y, button_quit_img)

def login_screen():
    global player_name

    username_box = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 100, 400, 50)
    password_box = pygame.Rect(screen_width // 2 - 200, screen_height // 2, 400, 50)
    username_color, password_color = gray, gray

    username_active, password_active = False, False
    username, password = "", ""

    running = True
    while running:
        screen.fill(black)

        draw_text("Login", font, blue, screen_width // 2 - 80, screen_height // 4 - 40)
        draw_text("Username:", small_font, white, username_box.x, username_box.y - 40)
        draw_text("Password:", small_font, white, password_box.x, password_box.y - 40)

        pygame.draw.rect(screen, username_color, username_box, 2)
        pygame.draw.rect(screen, password_color, password_box, 2)

        username_surface = small_font.render(username, True, white)
        password_surface = small_font.render("*" * len(password), True, white)

        screen.blit(username_surface, (username_box.x + 10, username_box.y + 10))
        screen.blit(password_surface, (password_box.x + 10, password_box.y + 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                username_active = username_box.collidepoint(event.pos)
                password_active = password_box.collidepoint(event.pos)
                username_color = white if username_active else gray
                password_color = white if password_active else gray
            if event.type == pygame.KEYDOWN:
                if username_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        username_active, password_active = False, True
                        username_color, password_color = gray, white
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode
                elif password_active:
                    if event.key == pygame.K_RETURN:
                        player_name, password = username, password
                        running = False
                    elif event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode

    return username, password

try:
    username, password = login_screen()
    print(f"Username: {username}, Password: {password}")

    high_score = load_scores().get(username, {}).get('high_score', 0)
    flying = False
    game_over = False
    score = 0

    run = True
    while run:
        clock.tick(fps)
        screen.blit(bg, (0, 0))
        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)
        pipe_group.update()
        screen.blit(ground_img, (ground_scroll, 768))
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        if not game_over and flying:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            if len(pipe_group) > 0:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                        and not pass_pipe:
                    pass_pipe = True
                if pass_pipe:
                    if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                        score += 1
                        pass_pipe = False

            draw_text(f"Score: {score}  High Score: {high_score}", font, white, 30, 20)

        if game_over:
            high_score = update_score(username, score)
            draw_text(f"High Score: {high_score}", font, white, screen_width // 2 - 200, screen_height // 2 + 150)

            if button.draw():
                game_over = False
                score = reset_game()
            if quit_button.draw():
                run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
                flying = True

        pygame.display.update()
finally:
    pygame.quit()
