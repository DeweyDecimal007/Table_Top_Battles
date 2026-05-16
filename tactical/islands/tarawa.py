"""
tactical/islands/tarawa.py
Static 5x5 test map for Tarawa using your new short naming convention
"""

from tactical.base import TacticalMapBase

class TarawaTacticalMap(TacticalMapBase):
    def __init__(self):
        super().__init__("Tarawa", grid_width=5, grid_height=5)

    def generate_base_layout(self):
        self.grid = {
            (0,0): "wds", (1,0): "wds", (2,0): "w2", (3,0): "snm3", (4,0): "tm",
            (0,1): "w4", (1,1): "w3", (2,1): "w1", (3,1): "tm", (4,1): "h3",
            (0,2): "dn1", (1,2): "dn2", (2,2): "of", (3,2): "h4", (4,2): "h5",
            (0,3): "af", (1,3): "afd", (2,3): "tree1", (3,3): "mud", (4,3): "sv2",
            (0,4): "yd4", (1,4): "tree1", (2,4): "lm", (3,4): "sv1", (4,4): "t3",
        }
        print("✅ 5x5 Tarawa test grid loaded with short names")

if __name__ == "__main__":
    map_instance = TarawaTacticalMap()
    map_instance.run()