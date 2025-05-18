import tkinter as tk
from tkinter import ttk
import random
import json

class MarioDataset:
    """Simulated Mario 1 level structure patterns"""
    def __init__(self):
        self.patterns = {
            'ground': ['GGGGGGGG', 'G  G  G'],
            'platform': ['--PP--', 'PP  PP'],
            'pipe': ['  ||  ', '  ||  '],
            'gap': ['  G  G  ', 'G  G  G'],
            'stairs': ['  G', ' GG', 'GGG']
        }
        
    def get_random_pattern(self):
        category = random.choice(list(self.patterns.keys()))
        return random.choice(self.patterns[category])

class MarioGPT:
    """Simplified text-to-level generator"""
    def __init__(self):
        self.dataset = MarioDataset()
        self.model = self._build_model()
        
    def _build_model(self):
        # Simulated "trained" patterns
        return {
            'flat': ['GGGGGGGGGGGG' * 4],
            'platforms': ['--PP--PP--PP--' * 3],
            'pipes': ['  ||    ||    ||  ' * 3],
            'mixed': ['GG--||GGPP--||GG' * 4]
        }
    
    def generate_level(self, prompt):
        prompt = prompt.lower()
        if 'flat' in prompt:
            return self.model['flat']
        elif 'platform' in prompt:
            return self.model['platforms']
        elif 'pipe' in prompt:
            return self.model['pipes']
        return random.choice(list(self.model.values()))

class LevelVisualizer(tk.Canvas):
    def __init__(self, master, width=800, height=300):
        super().__init__(master, width=width, height=height)
        self.tile_size = 32
        self.colors = {
            'G': '#654321',  # Ground
            'P': '#00ff00',  # Platform
            '|': '#0000ff',  # Pipe
            '-': '#87ceeb'   # Sky
        }
        
    def draw_level(self, level_str):
        self.delete("all")
        rows = level_str.split('\n')
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                color = self.colors.get(char, '#ffffff')
                self.create_rectangle(
                    x * self.tile_size,
                    y * self.tile_size,
                    (x+1) * self.tile_size,
                    (y+1) * self.tile_size,
                    fill=color,
                    outline=""
                )

class MarioGPTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MarioGPT Text2Level")
        
        self.generator = MarioGPT()
        self.level_code = ""
        
        self.create_widgets()
        
    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)
        
        self.prompt_entry = ttk.Entry(input_frame, width=50)
        self.prompt_entry.pack(side=tk.LEFT, padx=5)
        
        generate_btn = ttk.Button(
            input_frame,
            text="Generate Level",
            command=self.generate_level
        )
        generate_btn.pack(side=tk.LEFT)
        
        # Visualization
        self.visualizer = LevelVisualizer(self.root)
        self.visualizer.pack(pady=10)
        
        # Code Output
        code_frame = ttk.Frame(self.root)
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        self.code_text = tk.Text(code_frame, height=10)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        save_btn = ttk.Button(
            self.root,
            text="Export Python Code",
            command=self.export_code
        )
        save_btn.pack(pady=5)
        
    def generate_level(self):
        prompt = self.prompt_entry.get()
        level_data = self.generator.generate_level(prompt)
        self.visualizer.draw_level('\n'.join(level_data))
        self.generate_python_code(level_data)
        
    def generate_python_code(self, level_data):
        code = [
            "import pygame\n",
            "class Level:",
            "    def __init__(self):",
            "        self.tiles = ["
        ]
        
        for row in level_data:
            code.append(f'            "{row}",')
        
        code += [
            "        ]",
            "        self.tile_size = 32",
            "",
            "    def create_platforms(self, group):",
            "        for y, row in enumerate(self.tiles):",
            "            for x, tile in enumerate(row):",
            "                if tile == 'G':",
            "                    Platform(x*32, y*32, group)",
            "",
            "class Platform(pygame.sprite.Sprite):",
            "    def __init__(self, x, y, group):",
            "        super().__init__(group)",
            "        self.image = pygame.Surface((32,32))",
            "        self.image.fill('#654321')",
            "        self.rect = self.image.get_rect(topleft=(x,y))"
        ]
        
        self.level_code = '\n'.join(code)
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, self.level_code)
        
    def export_code(self):
        with open("generated_level.py", "w") as f:
            f.write(self.level_code)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarioGPTApp(root)
    root.mainloop()
