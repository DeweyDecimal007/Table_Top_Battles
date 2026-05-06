"""
tactical/island_registry.py
Easy lookup for island tactical maps
"""

from tactical.islands.industrial_hub import IndustrialHubTacticalMap   # example

ISLAND_MAPS = {
    "Industrial Hub": IndustrialHubTacticalMap,
    # Add more as we create them: "Guadalcanal": GuadalcanalTacticalMap,
}

def get_tactical_map(island_name: str):
    cls = ISLAND_MAPS.get(island_name)
    if cls:
        return cls()
    raise ValueError(f"No tactical map defined for {island_name}")