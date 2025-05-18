import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 32
PLAYER_SPEED = 5
GRAVITY = 0.4
JUMP_FORCE = -9

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (139, 69, 19)
PLAYER_COLOR = (255, 0, 0)
PLATFORM_COLOR = (34, 139, 34)
ENEMY_COLOR = (0, 255, 0)

class LevelGenerator:
    def __init__(self):
        self.patterns = [
            self._create_platform,
            self._create_pit,
            self._create_stairs,
            self._create_enemy
        ]
        
    def generate_chunk(self):
        chunk = []
        # Base ground
        chunk.extend(['G'] * 10)
        
        # Random pattern
        pattern = random.choice(self.patterns)
        pattern(chunk)
        
        return chunk
    
    def _create_platform(self, chunk):
        chunk[4:7] = ['P'] * 3
        
    def _create_pit(self, chunk):
        chunk[5] = ' '
        
    def _create_stairs(self, chunk):
        chunk[3] = 'P'
        chunk[6] = 'P'
        chunk[8] = 'P'
        
    def _create_enemy(self, chunk):
        chunk[5] = 'E'

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(PLAYER_COLOR)
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

        # Collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity.y = 0

        self.rect.x += self.velocity.x

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1

    def update(self):
        self.rect.x += self.direction * 2
        if random.random() < 0.01:
            self.direction *= -1

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    generator = LevelGenerator()
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Generate initial level
    chunk_x = 0
    for _ in range(5):
        chunk = generator.generate_chunk()
        for x, tile in enumerate(chunk, start=chunk_x):
            y_pos = HEIGHT - TILE_SIZE * 2
            if tile == 'G':
                block = Block(x * TILE_SIZE, y_pos + TILE_SIZE, GROUND_COLOR)
            elif tile == 'P':
                block = Block(x * TILE_SIZE, y_pos - TILE_SIZE, PLATFORM_COLOR)
            elif tile == 'E':
                enemy = Enemy(x * TILE_SIZE, y_pos - TILE_SIZE)
                enemies.add(enemy)
                all_sprites.add(enemy)
            if tile in ['G', 'P']:
                platforms.add(block)
                all_sprites.add(block)
        chunk_x += len(chunk)
    
    player = Player()
    all_sprites.add(player)
    
    camera_x = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update
        player.update(platforms)
        enemies.update()
        
        # Camera follow
        camera_x = player.rect.x - WIDTH // 2
        
        # Draw
        screen.fill(SKY_BLUE)
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
