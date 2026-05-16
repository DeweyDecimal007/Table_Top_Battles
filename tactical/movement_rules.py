"""
tactical/movement_rules.py
Movement and passability rules for tactical maps
Uses the new short naming convention (DN1, W1, AF, V1, etc.)
"""

from typing import Set, Dict, Tuple

class MovementRules:
    """Centralized rules for which units can move onto which terrain types."""

    def __init__(self):
        # terrain_key -> set of unit types that can enter this hex
        self.passability: Dict[str, Set[str]] = {
            # === WATER ===
            "wds": {"ship", "submarine"},           # Deep Sea
            "w1": {"ship", "submarine", "amphibious"},
            "w2": {"ship", "submarine", "amphibious"},
            "w3": {"ship", "submarine", "amphibious"},
            "w4": {"ship", "submarine", "amphibious"},
            "w5": {"ship", "submarine", "amphibious"},

            # === COASTAL / BEACH ===
            "dn1": {"infantry", "vehicle", "amphibious"},   # Dunes - good for beach landings
            "dn2": {"infantry", "vehicle", "amphibious"},
            "dn3": {"infantry", "vehicle", "amphibious"},
            "dn4": {"infantry", "vehicle", "amphibious"},
            "dn5": {"infantry", "vehicle", "amphibious"},

            # === LAND ===
            "af": {"infantry", "vehicle", "aircraft"},      # Airfield
            "afd": {"infantry", "vehicle"},                 # Airfield Dirt
            "v1": {"infantry", "vehicle"},                  # Village001
            "v2": {"infantry", "vehicle"},
            "v3": {"infantry", "vehicle"},
            "v4": {"infantry", "vehicle"},
            "v5": {"infantry", "vehicle"},
            "t1": {"infantry", "vehicle"},                  # Town
            "t2": {"infantry", "vehicle"},
            "t3": {"infantry", "vehicle"},
            "t4": {"infantry", "vehicle"},
            "t5": {"infantry", "vehicle"},

            # === OTHER COMMON LAND ===
            "tree1": {"infantry", "vehicle"},
            "tree2": {"infantry", "vehicle"},
            "lm": {"infantry", "vehicle"},                  # Lumber
            "of": {"infantry", "vehicle"},                  # Oil Field
            "ps": {"infantry", "vehicle"},                  # Power Station
            "ref": {"infantry", "vehicle"},                 # Refinery

            # === IMPASSABLE or restricted ===
            # Add more as needed
        }

    def can_enter(self, terrain_key: str, unit_type: str) -> bool:
        """Return True if this unit type can enter the given terrain."""
        allowed = self.passability.get(terrain_key.lower(), set())
        return unit_type.lower() in allowed

    def get_allowed_units(self, terrain_key: str) -> Set[str]:
        """Return set of unit types allowed on this terrain."""
        return self.passability.get(terrain_key.lower(), set())

    def is_water(self, terrain_key: str) -> bool:
        """Quick check for water hexes."""
        key = terrain_key.lower()
        return key.startswith("w") or key in {"wds", "dc", "dt", "dv"}


# Singleton instance for easy import
movement_rules = MovementRules()