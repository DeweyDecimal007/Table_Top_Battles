"""
tactical/base.py
Base class for all island tactical maps
"""

import pygame
import os
from pathlib import Path

class TacticalMapBase:
    def __init__(self, island_name: str, grid_width: int, grid_height: int):
        pygame.init()
        self.island_name = island_name
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        self.hex_width = 80   # scaled down from 509px for smooth play
        self.hex_height = 70  # adjust if you want different aspect
        
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption(f"Tactical Map - {island_name}")
        
        self.terrain_images = self.load_terrain_images()
        self.overlays = self.load_overlays()
        
        self.units = []  # list of unit dicts later
        self.camera_x = self.camera_y = 0

    def load_terrain_images(self):
        """Load all base hex terrain from your folder"""
        terrain_dir = Path("images/hex_terrain")
        images = {}
        for file in terrain_dir.glob("*.png"):
            name = file.stem.lower()
            try:
                img = pygame.image.load(file).convert_alpha()
                img = pygame.transform.scale(img, (self.hex_width, self.hex_height))
                images[name] = img
            except Exception as e:
                print(f"⚠️ Could not load {file}: {e}")
        print(f"✅ Loaded {len(images)} base terrain tiles")
        return images

    def load_overlays(self):
        """Load river/road/bridge overlays"""
        overlay_dir = Path("images/hex_terrain/Overlays_Bridges_Rivers_Roads")
        overlays = {}
        if overlay_dir.exists():
            for file in overlay_dir.glob("*.png"):
                name = file.stem.lower()
                try:
                    img = pygame.image.load(file).convert_alpha()
                    img = pygame.transform.scale(img, (self.hex_width, self.hex_height))
                    overlays[name] = img
                except Exception as e:
                    print(f"⚠️ Could not load overlay {file}: {e}")
            print(f"✅ Loaded {len(overlays)} overlays")
        return overlays

    def draw_hex(self, screen, col, row, terrain_key, overlay_key=None):
        # Simple axial hex positioning (flat-top)
        x = col * (self.hex_width * 0.75) + self.camera_x
        y = row * self.hex_height * 0.5 + (col % 2) * (self.hex_height * 0.5) + self.camera_y
        
        if terrain_key in self.terrain_images:
            screen.blit(self.terrain_images[terrain_key], (x, y))
        if overlay_key and overlay_key in self.overlays:
            screen.blit(self.overlays[overlay_key], (x, y))

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.fill((0, 20, 60))
            # Example draw - replace with real island layout
            for col in range(self.grid_width):
                for row in range(self.grid_height):
                    self.draw_hex(self.screen, col, row, "grass002")  # default for now
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()