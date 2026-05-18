"""
strategic/strategic_map.py
FINAL CLEAN VERSION - Duplicate Fiji removed, everything else locked
"""

import pygame
import random
import math

from tactical.island_registry import get_tactical_map


class StrategicMap:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1720, 1020
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Strategic Command - Blue Horizon Theater")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False

        self.hex_radius = 26
        self.horizontal_spacing = self.hex_radius * math.sqrt(3)
        self.vertical_spacing = self.hex_radius * 1.5
        self.font = pygame.font.SysFont("arial", 13, bold=True)
        self.name_font = pygame.font.SysFont("arial", 11, bold=True)
        self.coord_font = pygame.font.SysFont("arial", 9)

        self.cam_x = 0
        self.cam_y = 0
        self.dragging = False
        self.last_mouse_pos = (0, 0)

        self.tiles = {}
        self.generate_theater()

    def generate_theater(self):
        random.seed(42)   # 100% static forever

        self.tiles = {}

        # Base grid
        for row in range(56):
            for col in range(80):
                x = col * self.horizontal_spacing + self.hex_radius
                y = row * self.vertical_spacing + self.hex_radius
                if row % 2 == 1:
                    x += self.horizontal_spacing / 2

                self.tiles[(col, row)] = {
                    "pos": (x, y),
                    "terrain": "deep_water",
                    "owner": "Neutral",
                    "infrastructure": [],
                    "name": "",
                    "industrial": False
                }

        island_names = [
            "Guadalcanal", "Bougainville", "New Georgia", "Malaita", "Santa Isabel", "Choiseul",
            "San Cristobal", "Rendova", "Vella Lavella", "Kolombangara", "Tulagi", "Gizo",
            "Russell Islands", "Florida Island", "Shortland Islands", "Tahiti", "Bora Bora",
            "Moorea", "Huahine", "Raiatea", "Tikehau", "Vanua Levu", "Taveuni",
            "Kadavu", "Viti Levu", "Ovalau", "New Caledonia", "Lifou", "Maré", "Île des Pins",
            "Grande Terre", "Vanuatu", "Espiritu Santo", "Tanna", "Efate", "Malekula",
            "Ambrym", "Hawaii", "Maui", "Kauai", "Oahu", "Big Island", "Molokai", "Bali",
            "Java", "Sumatra", "Borneo", "Sulawesi", "Lombok", "Madagascar", "Crete",
            "Cyprus", "Sicily", "Sardinia", "Corsica", "Iceland", "Greenland", "Newfoundland",
            "Prince Edward Island", "Vancouver Island", "Galápagos", "Easter Island",
            "Falkland Islands", "Azores", "Canary Islands", "Madeira", "Seychelles",
            "Mauritius", "Reunion", "Comoros", "Tonga", "Samoa", "Trobriand",
            "Bismarck Archipelago", "Admiralty Islands", "New Britain", "New Ireland",
            "Manus Island", "Yap", "Palau", "Chuuk", "Pohnpei", "Kosrae", "Majuro",
            "Kwajalein", "Tarawa", "Nauru", "Kiribati", "Tuvalu", "Vanikoro", "Tikopia"
        ]
        random.shuffle(island_names)
        name_idx = 0

        # RED HOME ISLAND + 3 PICKETS
        red_home = [(8,6),(9,6),(10,6),(7,7),(8,7),(9,7),(10,7),(9,8)]
        for c, r in red_home:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["terrain"] = "land"
                self.tiles[(c, r)]["owner"] = "Red"
        for c, r in [(7,7), (10,7)]:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["industrial"] = True
        if red_home:
            self.tiles[red_home[3]]["name"] = island_names[name_idx]
            name_idx += 1
        red_pickets = [(6,4), (11,4), (7,10)]
        for c, r in red_pickets:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["terrain"] = "land"
                self.tiles[(c, r)]["owner"] = "Red"
                self.tiles[(c, r)]["name"] = island_names[name_idx]
                name_idx += 1

        # BLUE HOME ISLAND + 3 PICKETS
        blue_home = [(68,44),(69,44),(70,44),(67,45),(68,45),(69,45),(70,45),(68,46)]
        for c, r in blue_home:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["terrain"] = "land"
                self.tiles[(c, r)]["owner"] = "Blue"
        for c, r in [(67,45), (70,45)]:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["industrial"] = True
        if blue_home:
            self.tiles[blue_home[4]]["name"] = island_names[name_idx]
            name_idx += 1
        blue_pickets = [(66,42), (71,42), (67,48)]
        for c, r in blue_pickets:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["terrain"] = "land"
                self.tiles[(c, r)]["owner"] = "Blue"
                self.tiles[(c, r)]["name"] = island_names[name_idx]
                name_idx += 1

        # EXACT CENTRAL ISLAND CHAIN from your docx
        central_chain = [
            (16,14),(17,13),(17,16),(18,15),(18,17),
            (22,17),(23,19),(28,20),(19,19),(29,22),
            (30,21),(34,23),(35,25),(40,26),(41,25),
            (42,27),(42,29),(46,29),(47,31),(52,32),
            (53,31),(53,34),(54,33),(55,35),(57,36),
            (58,35),(58,37)
        ]
        for c, r in central_chain:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["terrain"] = "land"
                self.tiles[(c, r)]["owner"] = "Neutral"
                self.tiles[(c, r)]["name"] = island_names[name_idx % len(island_names)]
                name_idx += 1

        # 6 N-S deep blue channels
        channels = [20, 26, 32, 38, 44, 50]
        for ch_col in channels:
            for r in range(10, 42):
                for dc in range(-1, 2):
                    if (ch_col + dc, r) in self.tiles:
                        self.tiles[(ch_col + dc, r)]["terrain"] = "deep_water"

        # Industrial Hub - LOCKED at 36,32
        hub = [(36,32),(35,32),(37,32),(36,31),(36,33)]
        for c, r in hub:
            if (c, r) in self.tiles:
                self.tiles[(c, r)]["terrain"] = "land"
                self.tiles[(c, r)]["owner"] = "Neutral"
                self.tiles[(c, r)]["infrastructure"] = ["hub"]
        self.tiles[(36,32)]["industrial"] = True
        self.tiles[(36,32)]["name"] = "Industrial Hub"

        # Random outer islands
        for _ in range(80):
            c = random.randint(0, 79)
            r = random.randint(0, 55)
            if (c, r) in self.tiles and self.tiles[(c, r)]["terrain"] == "deep_water":
                too_close = any(self.tiles.get((c+dc, r+dr), {}).get("terrain") == "land" for dc in range(-4,5) for dr in range(-4,5))
                if not too_close:
                    size = 2 if random.random() < 0.5 else 1
                    self.tiles[(c, r)]["terrain"] = "land"
                    self.tiles[(c, r)]["owner"] = random.choice(["Blue", "Red", "Neutral"])
                    self.tiles[(c, r)]["name"] = island_names[name_idx % len(island_names)]
                    name_idx += 1
                    if size == 2 and (c+1, r) in self.tiles and self.tiles[(c+1, r)]["terrain"] == "deep_water":
                        self.tiles[(c+1, r)]["terrain"] = "land"
                        self.tiles[(c+1, r)]["owner"] = self.tiles[(c, r)]["owner"]

        # Strict 1-hex shallow ring
        land_pos = [(c,r) for (c,r),t in self.tiles.items() if t["terrain"] in ["land", "mountain", "sand"]]
        for c, r in land_pos:
            for dc, dr in [(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]:
                nc, nr = c + dc, r + dr
                if (nc, nr) in self.tiles and self.tiles[(nc, nr)]["terrain"] == "deep_water":
                    self.tiles[(nc, nr)]["terrain"] = "shallow"

        # FORCE DEEP WATER PORTS
        for coord in [(67,44), (7,6), (35,31)]:
            if coord in self.tiles:
                self.tiles[coord]["terrain"] = "deep_water"
                self.tiles[coord]["name"] = ""
                self.tiles[coord]["industrial"] = False

        # NO islands on edges
        for c in range(80):
            for r in [0, 55]:
                if (c, r) in self.tiles and self.tiles[(c, r)]["terrain"] == "land":
                    self.tiles[(c, r)]["terrain"] = "deep_water"
                    self.tiles[(c, r)]["name"] = ""
                    self.tiles[(c, r)]["industrial"] = False
        for r in range(56):
            for c in [0, 79]:
                if (c, r) in self.tiles and self.tiles[(c, r)]["terrain"] == "land":
                    self.tiles[(c, r)]["terrain"] = "deep_water"
                    self.tiles[(c, r)]["name"] = ""
                    self.tiles[(c, r)]["industrial"] = False

        # Final cleanup
        for tile in self.tiles.values():
            if tile["terrain"] != "land":
                tile["name"] = ""

        print("🌍 STATIC MAP LOCKED - Duplicate Fiji removed, central chain fully named!")

    def hexagon_points(self, center_x, center_y, radius):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            points.append((x, y))
        return points

    def draw(self):
        self.screen.fill((5, 15, 45))
        for (col, row), tile in self.tiles.items():
            x = tile["pos"][0] + self.cam_x
            y = tile["pos"][1] + self.cam_y

            if tile.get("industrial"):
                base_color = (169, 169, 169)
            elif tile["terrain"] == "mountain":
                base_color = (139, 69, 19)
            elif tile["terrain"] == "sand":
                base_color = (238, 220, 130)
            elif tile["terrain"] == "land":
                base_color = (34, 139, 34)
            elif tile["terrain"] == "shallow":
                base_color = (100, 180, 255)
            else:
                base_color = (0, 35, 70)

            border_color = (220, 40, 40) if tile["owner"] == "Red" else \
                           (30, 120, 255) if tile["owner"] == "Blue" else (220, 220, 230)

            points = self.hexagon_points(x, y, self.hex_radius)
            pygame.draw.polygon(self.screen, base_color, points)
            pygame.draw.polygon(self.screen, border_color, points, 3)

            if tile.get("infrastructure"):
                label = self.font.render("★", True, (255, 255, 80))
                self.screen.blit(label, (x - 8, y - 12))

            if tile.get("name"):
                text = self.name_font.render(tile["name"], True, (255, 255, 220))
                self.screen.blit(text, (x - text.get_width()//2, y - 28))

            coord_text = self.coord_font.render(f"{col},{row}", True, (180, 180, 200))
            self.screen.blit(coord_text, (x - coord_text.get_width()//2, y + 8))

        pygame.display.flip()

    def tile_at_screen_pos(self, pos):
        click_x, click_y = pos
        closest_coord = None
        closest_distance = self.hex_radius

        for coord, tile in self.tiles.items():
            tile_x = tile["pos"][0] + self.cam_x
            tile_y = tile["pos"][1] + self.cam_y
            distance = math.hypot(click_x - tile_x, click_y - tile_y)
            if distance <= closest_distance:
                closest_coord = coord
                closest_distance = distance

        return closest_coord

    def handle_click(self, pos):
        coord = self.tile_at_screen_pos(pos)
        if coord is None:
            print(f"Clicked at {pos}; no strategic hex selected.")
            return

        tile = self.tiles[coord]
        island_name = tile.get("name")
        if not island_name:
            print(f"Clicked {coord}; no island tactical map at this hex.")
            return

        try:
            tactical_map = get_tactical_map(island_name)
        except ValueError:
            print(f"{island_name} selected at {coord}; no tactical map registered yet.")
            return

        tactical_map.run()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.WIDTH, self.HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging = False
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.cam_x += dx
                    self.cam_y += dy
                    self.last_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)

            self.draw()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    StrategicMap().run()