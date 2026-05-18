"""
tactical/island_registry.py
Registry of all tactical island maps.
"""

from tactical.islands.tarawa import TarawaTacticalMap

ISLAND_MAPS = {
    "Tarawa": TarawaTacticalMap,
    # Add more islands here later:
    # "Industrial Hub": IndustrialHubTacticalMap,
}


def has_tactical_map(island_name: str) -> bool:
    return island_name in ISLAND_MAPS


def get_tactical_map(island_name: str):
    cls = ISLAND_MAPS.get(island_name)
    if cls:
        return cls()
    raise ValueError(f"No tactical map defined for island: {island_name}")