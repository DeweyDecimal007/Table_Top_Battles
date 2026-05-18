"""
tactical/islands/tarawa.py
Tarawa tactical map backed by the Godot island project.
"""

from pathlib import Path

from tactical.godot_map import GodotTacticalMap


class TarawaTacticalMap(GodotTacticalMap):
    def __init__(self):
        super().__init__(
            island_name="Tarawa",
            project_path=Path(r"C:\Interactive War Game Rules\Island_Maps\tarawa"),
            scene_path="res://Tarawa_Island_Map.tscn",
        )