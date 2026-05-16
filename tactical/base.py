"""
tactical/base.py
Stable flat-top hex grid with correct overlay scaling and centering
"""

import pygame
import math
from pathlib import Path
from typing import Dict, Tuple

class TacticalMapBase:
    def __init__(self, island_name: str, grid_width: int = 24, grid_height: int = 24):
        pygame.init()
        self.island_name = island_name
        self.grid_width = grid_width
        self.grid_height = grid_height

        self.hex_size = 40
        self.horizontal_spacing = self.hex_size * 1.5
        self.vertical_spacing = math.sqrt(3) * self.hex_size

        self.screen = pygame.display.set_mode((1600, 1000))
        pygame.display.set_caption(f"Tactical Map - {island_name}")

        self.terrain_images = self._load_terrain()
        self.overlay_images = self._load_overlays()

        self.grid: Dict[Tuple[int, int], str] = {}
        self.overlays_grid: Dict[Tuple[int, int], str] = {}

        self.generate_base_layout()

        self.camera_x = 200
        self.camera_y = 100

    def _load_terrain(self) -> Dict[str, pygame.Surface]:
        terrain_dir = Path("images/hex_terrain")
        images = {}
        for file in terrain_dir.glob("*.png"):
            key = file.stem.lower()
            try:
                img = pygame.image.load(file).convert_alpha()
                img = pygame.transform.scale(img, (int(self.hex_size * 2), int(self.hex_size * 1.732)))
                images[key] = img
            except Exception as e:
                print(f"⚠️ Failed to load terrain {file.name}: {e}")
        print(f"✅ Loaded {len(images)} terrain tiles")
        return images

    def _load_overlays(self) -> Dict[str, pygame.Surface]:
        overlay_dir = Path("images/hex_terrain/Overlays_Bridges_Rivers_Roads")
        overlays = {}
        if overlay_dir.exists():
            for file in overlay_dir.glob("*.png"):
                key = file.stem.lower()
                try:
                    img = pygame.image.load(file).convert_alpha()
                    img = pygame.transform.scale(img, (int(self.hex_size * 2), int(self.hex_size * 1.732)))
                    overlays[key] = img
                    print(f"   Loaded overlay: {key}")
                except Exception as e:
                    print(f"⚠️ Failed to load overlay {file.name}: {e}")
        return overlays

    def hexagon_points(self, center_x: float, center_y: float):
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.radians(angle_deg)
            x = center_x + self.hex_size * math.cos(angle_rad)
            y = center_y + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
        return points

    def generate_base_layout(self):
        pass

    def draw_hex(self, col: int, row: int):
        x = col * self.horizontal_spacing + self.hex_size * 1.5 + self.camera_x
        y = row * self.vertical_spacing + self.hex_size * 1.5 + self.camera_y

        if col % 2 == 1:
            y += self.vertical_spacing / 2

        terrain_key = self.grid.get((col, row), "deepsea002")
        overlay_key = self.overlays_grid.get((col, row))

        # Draw base terrain
        if terrain_key in self.terrain_images:
            self.screen.blit(self.terrain_images[terrain_key], (x - self.hex_size, y - self.hex_size * 0.866))

        # Draw overlay on top - same position and size
        if overlay_key and overlay_key in self.overlay_images:
            self.screen.blit(self.overlay_images[overlay_key], (x - self.hex_size, y - self.hex_size * 0.866))

    def draw_grid(self):
        for col in range(self.grid_width):
            for row in range(self.grid_height):
                self.draw_hex(col, row)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        dragging = False
        last_pos = (0, 0)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dragging = True
                    last_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    dx = event.pos[0] - last_pos[0]
                    dy = event.pos[1] - last_pos[1]
                    self.camera_x += dx
                    self.camera_y += dy
                    last_pos = event.pos

            self.screen.fill((5, 15, 45))
            self.draw_grid()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()