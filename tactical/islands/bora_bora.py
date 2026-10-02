"""
tactical/islands/bora_bora.py
Bora Bora tactical map backed by the Godot island project in this repo.
"""

from pathlib import Path

from tactical.godot_map import GodotTacticalMap


class BoraBoraTacticalMap(GodotTacticalMap):
    def __init__(self):
        root = Path(__file__).resolve().parents[2]
        super().__init__(
            island_name="Bora Bora",
            project_path=root / "godot" / "islands" / "bora_bora",
            scene_path="res://Bora_Bora_Island_Map.tscn",
        )
