import pygame
import random
import sys
import json

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
            pygame.draw.rect(screen, BLACK, (self.x, self.y - self.height, self.width, self.height))
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y - self.height), 
                           (self.x + self.width, self.y), 3)
        elif self.is_jumping:
            # Jumping dino
            pygame.draw.rect(screen, BLACK, (self.x, self.y - self.height, self.width, self.height))
        elif self.is_ducking:
            # Ducking dino with animation
            if self.current_frame == 0:
                pygame.draw.rect(screen, BLACK, (self.x, self.y - self.duck_height, self.width, self.duck_height))
            else:
                pygame.draw.rect(screen, BLACK, (self.x, self.y - self.duck_height + 5, self.width, self.duck_height - 5))
        else:
            # Running dino with animation
            if self.current_frame == 0:
                pygame.draw.rect(screen, BLACK, (self.x, self.y - self.height, self.width, self.height))
            else:
                pygame.draw.rect(screen, BLACK, (self.x, self.y - self.height + 5, self.width, self.height - 5))
    
    def get_mask(self):
        mask_surface = pygame.Surface((self.width, self.height if not self.is_ducking else self.duck_height), pygame.SRCALPHA)
        mask_surface.fill((255, 255, 255, 255))
        return pygame.mask.from_surface(mask_surface)
    
    def get_rect(self):
        if self.is_ducking:
            return pygame.Rect(self.x, self.y - self.duck_height, self.width, self.duck_height)
        return pygame.Rect(self.x, self.y - self.height, self.width, self.height)

class Cactus:
    def __init__(self, x):
        self.x = x
        self.type = random.choice(["small", "large", "multi"])
        
        if self.type == "small":
            self.width = 30
            self.height = 60
            self.y = GROUND_HEIGHT - self.height
        elif self.type == "large":
            self.width = 40
            self.height = 80
            self.y = GROUND_HEIGHT - self.height
        else:
            self.width = 60
            self.height = 70
            self.y = GROUND_HEIGHT - self.height
    
    def update(self, game_speed):
        self.x -= game_speed
    
    def draw(self, screen):
        if self.type == "small":
            pygame.draw.rect(screen, (0, 100, 0), (self.x, self.y, self.width, self.height))
        elif self.type == "large":
            pygame.draw.rect(screen, (0, 120, 0), (self.x, self.y, self.width, self.height))
        else:
            # Multi-part cactus
            pygame.draw.rect(screen, (0, 110, 0), (self.x, self.y + 20, 20, self.height - 20))
            pygame.draw.rect(screen, (0, 110, 0), (self.x + 15, self.y, 20, self.height))
            pygame.draw.rect(screen, (0, 110, 0), (self.x + 35, self.y + 10, 20, self.height - 10))
    
    def collide(self, dino):
        dino_rect = dino.get_rect()
        cactus_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return dino_rect.colliderect(cactus_rect)

class Bird:
    def __init__(self, x):
        self.x = x
        self.y = random.choice([GROUND_HEIGHT - 100, GROUND_HEIGHT - 50, GROUND_HEIGHT - 30])
        self.width = 60
        self.height = 50
        self.current_frame = 0
        self.animation_count = 0
    
    def update(self, game_speed):
        self.x -= game_speed * 1.2  # Birds move slightly faster
        self.animation_count += 1
        if self.animation_count >= 10:
            self.current_frame = 1 - self.current_frame
            self.animation_count = 0
    
    def draw(self, screen):
        # Draw bird with wing animation
        if self.current_frame == 0:
            # Wings up
            pygame.draw.ellipse(screen, (100, 100, 100), (self.x, self.y - self.height, self.width, self.height))
        else:
            # Wings down
            pygame.draw.ellipse(screen, (100, 100, 100), (self.x, self.y - self.height + 10, self.width, self.height - 10))
    
    def collide(self, dino):
        dino_rect = dino.get_rect()
        bird_rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
        return dino_rect.colliderect(bird_rect)

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, 150)
        self.speed = random.uniform(0.5, 1.5)
        self.width = random.randint(60, 120)
        self.height = 30
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, (240, 240, 240), (self.x, self.y, self.width, self.height))

class Ground:
    def __init__(self):
        self.x = 0
        self.width = SCREEN_WIDTH * 2
        self.height = 100
    
    def update(self, game_speed):
        self.x -= game_speed
        if self.x <= -SCREEN_WIDTH:
            self.x = 0
    
    def draw(self, screen):
        # Draw ground with texture
        pygame.draw.rect(screen, GROUND_COLOR, (self.x, GROUND_HEIGHT, self.width, self.height))
        
        # Draw ground details
        for i in range(0, int(self.width), 30):
            offset = random.randint(-5, 5)
            pygame.draw.line(screen, (210, 180, 140), 
                           (self.x + i, GROUND_HEIGHT + 5 + offset),
                           (self.x + i + 15, GROUND_HEIGHT + 5 + offset), 2)

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
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    restart_text = font_medium.render("Press SPACE to restart", True, WHITE)
    score_text = font_medium.render(f"Your Score: {score}", True, WHITE)
    
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 270))

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