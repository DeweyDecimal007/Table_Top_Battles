"""
tactical/godot_map.py
Lightweight bridge for tactical maps built as Godot projects.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class GodotTacticalMap:
    def __init__(self, island_name: str, project_path: Path, scene_path: str):
        self.island_name = island_name
        self.project_path = Path(project_path)
        self.scene_path = scene_path

    @property
    def project_file(self) -> Path:
        return self.project_path / "project.godot"

    def _godot_executable(self) -> Optional[str]:
        configured_path = os.environ.get("GODOT_EXECUTABLE") or os.environ.get("GODOT_PATH")
        if configured_path:
            return configured_path

        return shutil.which("godot") or shutil.which("godot4")

    def run(self):
        if not self.project_file.exists():
            raise FileNotFoundError(f"Godot project not found: {self.project_file}")

        godot_exe = self._godot_executable()
        if godot_exe:
            subprocess.Popen([godot_exe, "--path", str(self.project_path), self.scene_path])
            print(f"Opened {self.island_name} Godot tactical map: {self.scene_path}")
            return

        if os.name == "nt":
            os.startfile(self.project_file)
            print(
                f"Opened {self.island_name} Godot project. "
                "Set GODOT_EXECUTABLE to launch the tactical scene directly."
            )
            return

        raise RuntimeError("Godot executable was not found. Set GODOT_EXECUTABLE to your Godot binary.")
