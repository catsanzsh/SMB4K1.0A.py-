import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 32
PLAYER_SPEED = 5
GRAVITY = 0.4
JUMP_FORCE = -9

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.velocity.x = 0
        if keys[pygame.K_LEFT]:
            self.velocity.x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.velocity.x = PLAYER_SPEED

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity.y = JUMP_FORCE
            self.on_ground = False

        # Apply gravity
        self.velocity.y += GRAVITY
        self.rect.y += self.velocity.y

        # Platform collisions (vertical)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity.y = 0

        # Horizontal movement and collisions
        self.rect.x += self.velocity.x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = platform.rect.right

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x + TILE_SIZE//2, y + TILE_SIZE//2))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * 2
        if random.random() < 0.01:  # Random direction changes
            self.direction *= -1

class Overworld:
    def __init__(self):
        self.level_nodes = [
            (100, 100),
            (300, 150),
            (500, 100),
            (200, 300),
            (400, 350)
        ]
        self.current_node = 0

    def draw(self, screen):
        screen.fill(SKY_BLUE)
        
        # Draw paths
        for i in range(len(self.level_nodes)-1):
            pygame.draw.line(screen, WHITE, self.level_nodes[i], self.level_nodes[i+1], 5)
        
        # Draw nodes
        for i, (x, y) in enumerate(self.level_nodes):
            color = RED if i == self.current_node else WHITE
            pygame.draw.circle(screen, color, (x, y), 20)

def generate_smw_level():
    # Procedural level generation inspired by SMW
    level = []
    height = 15  # Number of vertical tiles
    
    # Generate empty space
    for _ in range(height):
        level.append([" "] * (WIDTH // TILE_SIZE))
    
    # Add ground
    level[-1] = ["B"] * (WIDTH // TILE_SIZE)
    
    # Add random platforms
    for _ in range(random.randint(3, 6)):
        x = random.randint(0, (WIDTH // TILE_SIZE) - 4)
        y = random.randint(height // 2, height - 2)
        length = random.randint(2, 5)
        for i in range(length):
            level[y][x + i] = "B"
    
    # Add random coins
    for _ in range(random.randint(5, 15)):
        x = random.randint(0, (WIDTH // TILE_SIZE) - 1)
        y = random.randint(0, height - 2)
        if level[y][x] == " ":
            level[y][x] = "C"
    
    # Add random pipes
    for _ in range(random.randint(2, 4)):
        x = random.randint(5, (WIDTH // TILE_SIZE) - 4)
        height = random.randint(2, 4)
        for y in range(1, height + 1):
            level[-y][x] = "B"
            level[-y][x + 1] = "B"
    
    return level

def create_level(level_layout):
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    for y, row in enumerate(level_layout):
        for x, tile in enumerate(row):
            if tile == 'B':
                platforms.add(Block(x * TILE_SIZE, y * TILE_SIZE))
            elif tile == 'C':
                coins.add(Coin(x * TILE_SIZE, y * TILE_SIZE))
            elif tile == 'E':
                enemies.add(Enemy(x * TILE_SIZE, y * TILE_SIZE))
    
    return platforms, coins, enemies

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    overworld = Overworld()
    game_state = "overworld"  # overworld | level | game_over
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if game_state == "overworld":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT and overworld.current_node < 4:
                        overworld.current_node += 1
                    if event.key == pygame.K_LEFT and overworld.current_node > 0:
                        overworld.current_node -= 1
                    if event.key == pygame.K_RETURN:
                        game_state = "level"
                        level_layout = generate_smw_level()
                        platforms, coins, enemies = create_level(level_layout)
                        player = Player()
                        player.rect.topleft = (100, HEIGHT - 150)
        
        if game_state == "level":
            player.update(platforms)
            enemies.update()
            
            # Check coin collection
            coins_collected = pygame.sprite.spritecollide(player, coins, True)
            
            # Check enemy collision
            if pygame.sprite.spritecollide(player, enemies, False):
                game_state = "overworld"
            
            # Draw level
            screen.fill(SKY_BLUE)
            platforms.draw(screen)
            coins.draw(screen)
            enemies.draw(screen)
            screen.blit(player.image, player.rect)
            
            # Return to overworld when reaching end
            if player.rect.x >= WIDTH - TILE_SIZE:
                game_state = "overworld"
        
        elif game_state == "overworld":
            overworld.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
