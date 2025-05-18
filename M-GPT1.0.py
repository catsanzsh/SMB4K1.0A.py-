import tkinter as tk
from tkinter import ttk
import random
import pygame
import threading
from pygame.locals import *

class EvolutionaryMarioDataset:
    def __init__(self):
        self.base_patterns = {
            'ground': ['GGGG', 'G  G'],
            'platform': ['PP', '-PP-'],
            'pipe': ['||', ' || '],
            'gap': ['  G  ', 'G   G'],
            'stairs': [' G ', 'GG ']
        }
        self.population = self.initialize_population()
        
    def initialize_population(self):
        return [random.choice(p) for p in random.choice(list(self.base_patterns.values()))]
    
    def mutate(self, pattern):
        if random.random() < 0.3 and len(pattern) > 1:
            idx = random.randint(0, len(pattern)-1)
            return pattern[:idx] + pattern[idx+1:]
        else:
            return pattern + random.choice(['G', '-', 'P'])
    
    def crossover(self, parent1, parent2):
        min_len = min(len(parent1), len(parent2))
        split = random.randint(1, min_len-1)
        return parent1[:split] + parent2[split:]
    
    def evolve(self, fitness_scores):
        sorted_pop = [x for _,x in sorted(zip(fitness_scores, self.population))]
        elites = sorted_pop[-2:]
        new_pop = elites.copy()
        
        while len(new_pop) < 10:
            parent1, parent2 = random.choices(sorted_pop[-4:], k=2)
            child = self.crossover(parent1, parent2)
            new_pop.append(self.mutate(child))
        
        self.population = new_pop

class MarioGPT:
    def __init__(self):
        self.dataset = EvolutionaryMarioDataset()
        self.fitness_cache = {}
        
    def calculate_fitness(self, pattern):
        key = ''.join(pattern)
        if key in self.fitness_cache:
            return self.fitness_cache[key]
        
        score = len(pattern) * 0.2
        score += pattern.count('G') * 0.5
        score -= pattern.count(' ') * 0.3
        self.fitness_cache[key] = score
        return score
    
    def generate_level(self, prompt):
        self.dataset.evolve([self.calculate_fitness(p) for p in self.dataset.population])
        selected = random.choices(
            self.dataset.population,
            weights=[self.calculate_fitness(p) for p in self.dataset.population],
            k=10
        )
        return '\n'.join(selected)

class PygameSimulator(threading.Thread):
    def __init__(self, level_data):
        super().__init__()
        self.level_data = level_data
        self.running = True
        self.daught_exception = None
        
    def run(self):
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            self.clock = pygame.time.Clock()
            
            self.all_sprites = pygame.sprite.Group()
            self.platforms = pygame.sprite.Group()
            
            for y, row in enumerate(self.level_data.split('\n')):
                for x, char in enumerate(row):
                    if char == 'G':
                        Platform(x*32, y*32, self.platforms)
            
            self.player = Player(100, 100, self.platforms)
            self.all_sprites.add(self.player)
            
            while self.running:
                self.screen.fill((135, 206, 235))
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.running = False
                
                self.all_sprites.update()
                self.platforms.draw(self.screen)
                self.all_sprites.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(30)
                
        except Exception as e:
            self.daught_exception = e
        finally:
            pygame.quit()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms):
        super().__init__()
        self.image = pygame.Surface((32,64))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.platforms = platforms
        self.velocity = pygame.Vector2(0,0)
        self.on_ground = True
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = (keys[K_RIGHT] - keys[K_LEFT]) * 5
        if keys[K_SPACE] and self.on_ground:
            self.velocity.y = -15
            
        self.velocity.y += 0.8
        self.rect.x += self.velocity.x
        self.collide('x')
        self.rect.y += self.velocity.y
        self.collide('y')
        
    def collide(self, axis):
        hits = pygame.sprite.spritecollide(self, self.platforms, False)
        for platform in hits:
            if axis == 'x':
                if self.velocity.x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = platform.rect.right
            else:
                if self.velocity.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = platform.rect.bottom

class MarioGPTApp:
    def __init__(self, root):
        self.root = root
        self.generator = MarioGPT()
        self.simulator = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.prompt_entry = ttk.Entry(main_frame, width=50)
        self.prompt_entry.pack(pady=10)
        
        generate_btn = ttk.Button(
            main_frame,
            text="Generate and Simulate",
            command=self.generate_and_simulate
        )
        generate_btn.pack()
        
    def generate_and_simulate(self):
        level = self.generator.generate_level(self.prompt_entry.get())
        
        if self.simulator:
            self.simulator.running = False
            self.simulator.join()
            
        self.simulator = PygameSimulator(level)
        self.simulator.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MarioGPTApp(root)
    root.mainloop()
