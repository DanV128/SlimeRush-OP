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
BIRD_SPAWN_SCORE = 700

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (247, 247, 247)
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (244, 164, 96)
SCORE_COLOR = (83, 83, 83)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chrome Dinosaur Game")
clock = pygame.time.Clock()

# High score file
HIGH_SCORE_FILE = "highscore.json"

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(f"assets/{name}.png").convert_alpha()
    except:
        # Create a placeholder if image loading fails
        image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(image, (255, 0, 255), (0, 0, 50, 50))
        pygame.draw.line(image, (0, 0, 0), (0, 0), (50, 50), 2)
        pygame.draw.line(image, (0, 0, 0), (50, 0), (0, 50), 2)
    
    if scale != 1:
        new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
        image = pygame.transform.scale(image, new_size)
    return image

# Try to create assets directory if it doesn't exist
if not os.path.exists("assets"):
    os.makedirs("assets")

# Load or create placeholder images
try:
    # Dino sprites
    dino_run1 = load_image("dino_run1", 0.7)
    dino_run2 = load_image("dino_run2", 0.7)
    dino_duck1 = load_image("dino_duck1", 0.7)
    dino_duck2 = load_image("dino_duck2", 0.7)
    dino_jump = load_image("dino_jump", 0.7)
    dino_dead = load_image("dino_dead", 0.7)
    
    # Obstacle sprites
    cactus_small = load_image("cactus_small", 0.7)
    cactus_large = load_image("cactus_large", 0.7)
    cactus_multi = load_image("cactus_multi", 0.7)
    
    # Bird sprites
    bird_frame1 = load_image("bird_frame1", 0.7)
    bird_frame2 = load_image("bird_frame2", 0.7)
    
    # Environment sprites
    cloud_img = load_image("cloud", 0.7)
    ground_img = load_image("ground", 2.0)
    
    # Game UI
    game_over_img = load_image("game_over", 0.8)
    restart_img = load_image("restart", 0.8)
    
except Exception as e:
    print(f"Error loading images: {e}")
    # If image loading fails, the game will fall back to primitive shapes

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

# Load fonts
font_small = pygame.font.SysFont("Arial", 20)
font_medium = pygame.font.SysFont("Arial", 30, bold=True)
font_large = pygame.font.SysFont("Arial", 50, bold=True)

# Game objects
class Dinosaur:
    def __init__(self):
        self.x = 50
        self.y = GROUND_HEIGHT
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.current_frame = 0
        self.animation_count = 0
        self.dead = False
        self.width = 60
        self.height = 80
        self.duck_height = 40
        
        # Image dimensions
        self.run_images = [dino_run1, dino_run2]
        self.duck_images = [dino_duck1, dino_duck2]
        self.jump_image = dino_jump
        self.dead_image = dino_dead
    
    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Check if landed on ground
        if self.y >= GROUND_HEIGHT:
            self.y = GROUND_HEIGHT
            self.vel_y = 0
            self.is_jumping = False
        
        # Animation
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
            # Dead dino
            screen.blit(self.dead_image, (self.x, self.y - self.dead_image.get_height()))
        elif self.is_jumping:
            # Jumping dino
            screen.blit(self.jump_image, (self.x, self.y - self.jump_image.get_height()))
        elif self.is_ducking:
            # Ducking dino with animation
            screen.blit(self.duck_images[self.current_frame], 
                       (self.x, self.y - self.duck_images[self.current_frame].get_height()))
        else:
            # Running dino with animation
            screen.blit(self.run_images[self.current_frame], 
                       (self.x, self.y - self.run_images[self.current_frame].get_height()))
    
    def get_mask(self):
        if self.is_ducking:
            img = self.duck_images[self.current_frame]
        elif self.is_jumping:
            img = self.jump_image
        elif self.dead:
            img = self.dead_image
        else:
            img = self.run_images[self.current_frame]
        
        return pygame.mask.from_surface(img)
    
    def get_rect(self):
        if self.is_ducking:
            img = self.duck_images[self.current_frame]
        elif self.is_jumping:
            img = self.jump_image
        elif self.dead:
            img = self.dead_image
        else:
            img = self.run_images[self.current_frame]
        
        return pygame.Rect(self.x, self.y - img.get_height(), img.get_width(), img.get_height())

class Cactus:
    def __init__(self, x):
        self.x = x
        self.type = random.choice(["small", "large", "multi"])
        
        if self.type == "small":
            self.image = cactus_small
        elif self.type == "large":
            self.image = cactus_large
        else:
            self.image = cactus_multi
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.y = GROUND_HEIGHT - self.height
    
    def update(self, game_speed):
        self.x -= game_speed
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def collide(self, dino):
        dino_rect = dino.get_rect()
        cactus_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return dino_rect.colliderect(cactus_rect)

class Bird:
    def __init__(self, x):
        self.x = x
        self.y = random.choice([GROUND_HEIGHT - 100, GROUND_HEIGHT - 50, GROUND_HEIGHT - 30])
        self.images = [bird_frame1, bird_frame2]
        self.current_frame = 0
        self.animation_count = 0
        self.width = self.images[0].get_width()
        self.height = self.images[0].get_height()
    
    def update(self, game_speed):
        self.x -= game_speed * 1.2  # Birds move slightly faster
        self.animation_count += 1
        if self.animation_count >= 10:
            self.current_frame = 1 - self.current_frame
            self.animation_count = 0
    
    def draw(self, screen):
        screen.blit(self.images[self.current_frame], (self.x, self.y - self.height))
    
    def collide(self, dino):
        dino_rect = dino.get_rect()
        bird_rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
        return dino_rect.colliderect(bird_rect)

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
    
    def update(self, game_speed):
        self.x -= game_speed
        if self.x <= -SCREEN_WIDTH:
            self.x = 0
    
    def draw(self, screen):
        # Draw repeating ground image
        screen.blit(self.image, (self.x, GROUND_HEIGHT))
        screen.blit(self.image, (self.x + self.width, GROUND_HEIGHT))

def draw_score(screen, score, high_score):
    score_text = font_medium.render(f"SCORE: {score}", True, SCORE_COLOR)
    high_score_text = font_medium.render(f"HIGH SCORE: {high_score}", True, SCORE_COLOR)
    
    # Draw with background for better readability
    pygame.draw.rect(screen, (240, 240, 240, 150), (SCREEN_WIDTH - 250, 10, 240, 90), border_radius=5)
    screen.blit(score_text, (SCREEN_WIDTH - 240, 20))
    screen.blit(high_score_text, (SCREEN_WIDTH - 240, 50))

def draw_game_over(screen, score):
    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Game over text
    screen.blit(game_over_img, (SCREEN_WIDTH // 2 - game_over_img.get_width() // 2, 150))
    
    # Score text
    score_text = font_medium.render(f"Your Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))
    
    # Restart prompt
    screen.blit(restart_img, (SCREEN_WIDTH // 2 - restart_img.get_width() // 2, 270))

def draw_start_screen(screen):
    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Game title
    title_text = font_large.render("DINO RUNNER", True, WHITE)
    start_text = font_medium.render("Press SPACE to start", True, WHITE)
    controls_text = font_small.render("UP to jump | DOWN to crouch", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 220))
    screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 270))

def main():
    # Load high score
    high_score = load_high_score()
    
    # Game variables
    dino = Dinosaur()
    ground = Ground()
    clouds = []
    obstacles = []
    game_speed = GAME_SPEED_START
    score = 0
    game_over = False
    game_started = False
    obstacle_timer = 0
    cloud_timer = 0
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not game_started:
                        game_started = True
                    elif game_over:
                        # Reset game
                        dino = Dinosaur()
                        obstacles = []
                        clouds = []
                        game_speed = GAME_SPEED_START
                        score = 0
                        game_over = False
                        game_started = True
                    else:
                        dino.jump()
                elif event.key == pygame.K_DOWN:
                    dino.duck(True)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    dino.duck(False)
        
        # Fill background
        screen.fill(SKY_COLOR)
        
        if game_started and not game_over:
            # Update game state
            dino.update()
            ground.update(game_speed)
            
            # Update obstacles
            for obstacle in obstacles:
                obstacle.update(game_speed)
                if obstacle.collide(dino):
                    dino.dead = True
                    game_over = True
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
            
            # Remove off-screen obstacles
            obstacles = [obstacle for obstacle in obstacles if obstacle.x > -100]
            
            # Spawn new obstacles
            obstacle_timer += 1
            if obstacle_timer >= random.randint(50, 150):
                # Only spawn birds after reaching BIRD_SPAWN_SCORE
                if score >= BIRD_SPAWN_SCORE and random.random() < 0.3:
                    obstacles.append(Bird(SCREEN_WIDTH))
                else:
                    obstacles.append(Cactus(SCREEN_WIDTH))
                obstacle_timer = 0
            
            # Update clouds
            for cloud in clouds:
                cloud.update()
            
            # Remove off-screen clouds
            clouds = [cloud for cloud in clouds if cloud.x > -cloud.width]
            
            # Spawn new clouds
            cloud_timer += 1
            if cloud_timer >= random.randint(100, 300):
                clouds.append(Cloud())
                cloud_timer = 0
            
            # Increase score and difficulty
            score += 1
            game_speed += GAME_SPEED_INCREMENT
        
        # Draw everything
        # Draw clouds (background)
        for cloud in clouds:
            cloud.draw(screen)
        
        # Draw ground
        ground.draw(screen)
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        # Draw dino
        dino.draw(screen)
        
        # Draw score
        if game_started and not game_over:
            draw_score(screen, score, high_score)
        
        # Draw start screen or game over screen
        if not game_started:
            draw_start_screen(screen)
        elif game_over:
            draw_game_over(screen, score)
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()