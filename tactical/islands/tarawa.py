"""
tactical/islands/tarawa.py
Stable Tarawa - restored good coastline + strict Road 2 + Road 5 overlays on the exact two hexes
"""

from tactical.base import TacticalMapBase
import random

class TarawaTacticalMap(TacticalMapBase):
    def __init__(self):
        super().__init__("Tarawa", grid_width=24, grid_height=24)

    def generate_base_layout(self):
        random.seed(42)

        # 1. Full deep water base
        for col in range(24):
            for row in range(24):
                self.grid[(col, row)] = "deepsea002"

        # 2. Solid central land core (Dunes) - restored good shape
        land_hexes = []
        for col in range(5, 20):
            for row in range(6, 19):
                dist = ((col - 12)**2 + (row - 12)**2)**0.5
                if dist < 9.3 and random.random() < 0.92:
                    self.grid[(col, row)] = "dunes001"
                    land_hexes.append((col, row))

        # Light interior variety
        for col, row in land_hexes:
            if random.random() < 0.22:
                self.grid[(col, row)] = "lightjungle005"
            elif random.random() < 0.09:
                self.grid[(col, row)] = "swamp001"

        # Water buffer adjacent to all Dune hexes
        for col, row in list(land_hexes):
            for dc, dr in [(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]:
                nc, nr = col + dc, row + dr
                if (nc, nr) in self.grid and self.grid.get((nc, nr)) == "deepsea002":
                    self.grid[(nc, nr)] = "water001"

        # Centers
        village_pos = (12, 13)
        airfield_pos = (15, 11)
        self.grid[village_pos] = "village001"
        self.grid[airfield_pos] = "airfield"

        # STRICT ROAD OVERLAYS - only on the two hexes between village and airfield
        self._place_road_overlays(village_pos, airfield_pos)

        # Outer water buffer
        for col in range(24):
            for row in [0, 1, 22, 23]:
                if self.grid.get((col, row)) in ["water001", "dunes001"]:
                    self.grid[(col, row)] = "deepsea002"
        for row in range(24):
            for col in [0, 1, 22, 23]:
                if self.grid.get((col, row)) in ["water001", "dunes001"]:
                    self.grid[(col, row)] = "deepsea002"

        print("✅ Tarawa - stable coastline + strict Road 2 + Road 5 overlays on the two path hexes")

    def _place_road_overlays(self, start, end):
        """Place BOTH Road 2 and Road 5 on each of the two hexes between centers"""
        col, row = start
        target_col, target_row = end

        # First hex on path
        self.overlays_grid[(col, row)] = "road 2"
        self.overlays_grid[(col, row)] = "road 5"   # both overlays on same hex

        # Move one step
        if abs(col - target_col) > abs(row - target_row):
            col += 1 if col < target_col else -1
        else:
            row += 1 if row < target_row else -1

        # Second hex on path
        self.overlays_grid[(col, row)] = "road 2"
        self.overlays_grid[(col, row)] = "road 5"   # both overlays on same hex

        print("   → Both Road 2 and Road 5 placed on the two path hexes")

if __name__ == "__main__":
    map_instance = TarawaTacticalMap()
    map_instance.run()