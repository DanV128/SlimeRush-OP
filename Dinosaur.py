import pygame
import random
import sys
import json
import os

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 300
FPS = 60
GRAVITY = 1
JUMP_STRENGTH = -18
GAME_SPEED_START = 10
GAME_SPEED_INCREMENT = 0.0025
FIREBALL_SPAWN_SCORE = 700

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (247, 247, 247)
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (244, 164, 96)
SCORE_COLOR = (83, 83, 83)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slime Rush")
clock = pygame.time.Clock()

# High score file
HIGH_SCORE_FILE = "highscore.json"

def load_image(name, scale=1):
    try:
        image = pygame.image.load(f"assets/{name}.png").convert_alpha()
    except:
        image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(image, (255, 0, 255), (0, 0, 50, 50))
        pygame.draw.line(image, (0, 0, 0), (0, 0), (50, 50), 2)
        pygame.draw.line(image, (0, 0, 0), (50, 0), (0, 50), 2)
    
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    return image

if not os.path.exists("assets"):
    os.makedirs("assets")

try:
    slime_run1 = load_image("slime_run1", 0.7)
    slime_run2 = load_image("slime_run2", 0.7)
    slime_duck1 = load_image("slime_duck1", 0.7)
    slime_duck2 = load_image("slime_duck2", 0.7)
    slime_jump = load_image("slime_jump", 0.7)
    slime_dead = load_image("slime_dead", 0.7)
    
    spike_small = load_image("spike_small", 0.7)
    spike_large = load_image("spike_large", 0.7)
    spike_multi = load_image("spike_multi", 0.7)
    
    fireball_frame1 = load_image("fireball_frame1", 0.7)
    fireball_frame2 = load_image("fireball_frame2", 0.7)
    
    cloud_img = load_image("cloud", 0.7)
    ground_img = load_image("ground", 1.0)  
    
    game_over_img = load_image("game_over", 0.8)
    restart_img = load_image("restart", 0.8)
    
except Exception as e:
    print(f"Error loading images: {e}")

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_high_score(high_score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'high_score': high_score}, f)

font_small = pygame.font.SysFont("Arial", 20)
font_medium = pygame.font.SysFont("Arial", 30, bold=True)
font_large = pygame.font.SysFont("Arial", 50, bold=True)

class Slime:
    def __init__(self):
        self.x = 50
        self.y = GROUND_HEIGHT
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.current_frame = 0
        self.animation_count = 0
        self.dead = False
        
        self.run_images = [slime_run1, slime_run2]
        self.duck_images = [slime_duck1, slime_duck2]
        self.jump_image = slime_jump
        self.dead_image = slime_dead
        
        # Pre-calculate masks for better performance
        self.run_masks = [pygame.mask.from_surface(img) for img in self.run_images]
        self.duck_masks = [pygame.mask.from_surface(img) for img in self.duck_images]
        self.jump_mask = pygame.mask.from_surface(self.jump_image)
        self.dead_mask = pygame.mask.from_surface(self.dead_image)
    
    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        if self.y >= GROUND_HEIGHT:
            self.y = GROUND_HEIGHT
            self.vel_y = 0
            self.is_jumping = False
        
        if not self.is_jumping and not self.is_ducking:
            self.animation_count += 1
            if self.animation_count >= 10:
                self.current_frame = 1 - self.current_frame
                self.animation_count = 0
        elif self.is_ducking:
            self.animation_count += 1
            if self.animation_count >= 10:
                self.current_frame = 1 - self.current_frame
                self.animation_count = 0
    
    def jump(self):
        if not self.is_jumping and not self.dead:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True
    
    def duck(self, is_ducking):
        if not self.is_jumping and not self.dead:
            self.is_ducking = is_ducking
    
    def draw(self, screen):
        if self.dead:
            screen.blit(self.dead_image, (self.x, self.y - self.dead_image.get_height()))
        elif self.is_jumping:
            screen.blit(self.jump_image, (self.x, self.y - self.jump_image.get_height()))
        elif self.is_ducking:
            screen.blit(self.duck_images[self.current_frame], 
                       (self.x, self.y - self.duck_images[self.current_frame].get_height()))
        else:
            screen.blit(self.run_images[self.current_frame], 
                       (self.x, self.y - self.run_images[self.current_frame].get_height()))
    
    def get_mask(self):
        if self.is_ducking:
            return self.duck_masks[self.current_frame]
        elif self.is_jumping:
            return self.jump_mask
        elif self.dead:
            return self.dead_mask
        else:
            return self.run_masks[self.current_frame]
    
    def get_rect(self):
        mask = self.get_mask()
        rect = mask.get_bounding_rects()[0] if mask.get_bounding_rects() else pygame.Rect(0, 0, 0, 0)
        rect.x += self.x
        rect.y += self.y - (self.jump_image.get_height() if self.is_jumping else 
                           self.run_images[0].get_height() if not self.is_ducking else 
                           self.duck_images[0].get_height())
        return rect

class Spike:
    def __init__(self, x):
        self.x = x
        self.type = random.choice(["small", "large", "multi"])
        
        if self.type == "small":
            self.image = spike_small
        elif self.type == "large":
            self.image = spike_large
        else:
            self.image = spike_multi
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.y = GROUND_HEIGHT - self.height
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, game_speed):
        self.x -= game_speed
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y-15))
    
    def collide(self, slime):
        slime_mask = slime.get_mask()
        offset_x = self.x - slime.get_rect().x
        offset_y = self.y - slime.get_rect().y
        return slime_mask.overlap(self.mask, (offset_x, offset_y)) is not None

class Fireball:
    def __init__(self, x):
        self.x = x
        self.y = random.choice([GROUND_HEIGHT - 100, GROUND_HEIGHT - 50, GROUND_HEIGHT - 30])
        self.images = [fireball_frame1, fireball_frame2]
        self.current_frame = 0
        self.animation_count = 0
        self.width = self.images[0].get_width()
        self.height = self.images[0].get_height()
        self.masks = [pygame.mask.from_surface(img) for img in self.images]
    
    def update(self, game_speed):
        self.x -= game_speed * 1.2
        self.animation_count += 1
        if self.animation_count >= 10:
            self.current_frame = 1 - self.current_frame
            self.animation_count = 0
    
    def draw(self, screen):
        screen.blit(self.images[self.current_frame], (self.x, self.y - self.height))
    
    def collide(self, slime):
        slime_mask = slime.get_mask()
        offset_x = self.x - slime.get_rect().x
        offset_y = (self.y - self.height) - slime.get_rect().y
        return slime_mask.overlap(self.masks[self.current_frame], (offset_x, offset_y)) is not None

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, 150)
        self.speed = random.uniform(0.5, 1.5)
        self.image = cloud_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Ground:
    def __init__(self):
        self.x = 0
        self.image = ground_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        # Create enough ground tiles to cover the screen
        self.tiles = []
        for i in range(0, SCREEN_WIDTH * 2, self.width):
            self.tiles.append(i)
    
    def update(self, game_speed):
        self.x -= game_speed
        if self.x <= -self.width:
            self.x = 0
    
    def draw(self, screen):
        # Draw ground tiles
        for tile_x in self.tiles:
            screen.blit(self.image, (tile_x + self.x, GROUND_HEIGHT - self.height + 143))

def draw_score(screen, score, high_score):
    score_text = font_medium.render(f"SCORE: {score}", True, SCORE_COLOR)
    high_score_text = font_medium.render(f"HIGH SCORE: {high_score}", True, SCORE_COLOR)
    
    pygame.draw.rect(screen, (240, 240, 240, 150), (SCREEN_WIDTH - 250, 10, 240, 90), border_radius=5)
    screen.blit(score_text, (SCREEN_WIDTH - 240, 20))
    screen.blit(high_score_text, (SCREEN_WIDTH - 240, 50))

def draw_game_over(screen, score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    screen.blit(game_over_img, (SCREEN_WIDTH // 2 - game_over_img.get_width() // 2, 150))
    
    score_text = font_medium.render(f"Your Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))
    
    screen.blit(restart_img, (SCREEN_WIDTH // 2 - restart_img.get_width() // 2, 270))

def draw_start_screen(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    title_text = font_large.render("SLIME RUSH", True, WHITE)
    start_text = font_medium.render("Press SPACE to start", True, WHITE)
    controls_text = font_small.render("UP to jump | DOWN to crouch", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 220))
    screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 270))

def main():
    high_score = load_high_score()
    
    slime = Slime()
    ground = Ground()
    clouds = []
    obstacles = []
    game_speed = GAME_SPEED_START
    score = 0
    game_over = False
    game_started = False
    obstacle_timer = 0
    cloud_timer = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not game_started:
                        game_started = True
                    elif game_over:
                        slime = Slime()
                        obstacles = []
                        clouds = []
                        game_speed = GAME_SPEED_START
                        score = 0
                        game_over = False
                        game_started = True
                    else:
                        slime.jump()
                elif event.key == pygame.K_DOWN:
                    slime.duck(True)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    slime.duck(False)
        
        screen.fill(SKY_COLOR)
        
        if game_started and not game_over:
            slime.update()
            ground.update(game_speed)
            
            for obstacle in obstacles:
                obstacle.update(game_speed)
                if obstacle.collide(slime):
                    slime.dead = True
                    game_over = True
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
            
            obstacles = [obstacle for obstacle in obstacles if obstacle.x > -100]
            
            obstacle_timer += 1
            if obstacle_timer >= random.randint(50, 150):
                if score >= FIREBALL_SPAWN_SCORE and random.random() < 0.3:
                    obstacles.append(Fireball(SCREEN_WIDTH))
                else:
                    obstacles.append(Spike(SCREEN_WIDTH))
                obstacle_timer = 0
            
            for cloud in clouds:
                cloud.update()
            
            clouds = [cloud for cloud in clouds if cloud.x > -cloud.width]
            
            cloud_timer += 1
            if cloud_timer >= random.randint(100, 300):
                clouds.append(Cloud())
                cloud_timer = 0
            
            score += 1
            game_speed += GAME_SPEED_INCREMENT
        
        for cloud in clouds:
            cloud.draw(screen)
        
        ground.draw(screen)
        
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        slime.draw(screen)
        
        if game_started and not game_over:
            draw_score(screen, score, high_score)
        
        if not game_started:
            draw_start_screen(screen)
        elif game_over:
            draw_game_over(screen, score)
        
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()