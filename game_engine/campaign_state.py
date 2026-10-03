"""
game_engine/campaign_state.py
Campaign state (resources, industry, armies) and save-game management.
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime


SAVE_VERSION = 1

GAME_MODES = {
    "Grand Campaign": {
        "description": "Full theater war. Build industry, raise armies and fight for every island.",
        "turn_limit": None,
        "resource_multiplier": 1.0,
    },
    "Operational Campaign": {
        "description": "A shorter 20-turn campaign focused on the central island chain.",
        "turn_limit": 20,
        "resource_multiplier": 1.25,
    },
    "Tactical Skirmish": {
        "description": "Jump straight into battle with a generous war chest to build your force.",
        "turn_limit": 1,
        "resource_multiplier": 3.0,
    },
}

DIFFICULTIES = {
    "Recruit": 1.5,
    "Veteran": 1.0,
    "Elite": 0.7,
}

RESOURCES = {
    "RUs":      {"label": "Resource Units",     "color": "#d4a24c"},
    "CUs":      {"label": "Construction Units", "color": "#8fb3c9"},
    "Fuel":     {"label": "Fuel",               "color": "#c96f4a"},
    "RP":       {"label": "Research Points",    "color": "#9b8fd4"},
    "Manpower": {"label": "Manpower",           "color": "#7fbf7f"},
}

BASE_RESOURCES = {"RUs": 500, "CUs": 300, "Fuel": 200, "RP": 100, "Manpower": 400}

INDUSTRY = {
    "steel_mills": {
        "name": "Steel Mills",
        "description": "Smelt ore into the raw materials every war machine needs.",
        "produces": {"RUs": 40},
        "upgrade_cost": {"RUs": 80, "CUs": 60},
    },
    "factories": {
        "name": "Factories",
        "description": "Heavy industry for vehicles, guns and construction projects.",
        "produces": {"CUs": 30},
        "upgrade_cost": {"RUs": 100, "CUs": 40},
    },
    "refineries": {
        "name": "Oil Refineries",
        "description": "Fuel for armor, aircraft and the fleet.",
        "produces": {"Fuel": 25},
        "upgrade_cost": {"RUs": 90, "CUs": 70},
    },
    "research": {
        "name": "Research Institutes",
        "description": "Scientists and engineers developing new doctrine and weapons.",
        "produces": {"RP": 15},
        "upgrade_cost": {"RUs": 60, "CUs": 90},
    },
    "depots": {
        "name": "Recruitment Depots",
        "description": "Training grounds that turn civilians into soldiers.",
        "produces": {"Manpower": 50},
        "upgrade_cost": {"RUs": 50, "CUs": 50},
    },
    "shipyards": {
        "name": "Shipyards",
        "description": "Build and repair transports and warships. Each level adds naval capacity.",
        "produces": {"CUs": 10, "Fuel": 5},
        "upgrade_cost": {"RUs": 150, "CUs": 120},
    },
}

STARTING_INDUSTRY = {
    "steel_mills": 2,
    "factories": 2,
    "refineries": 1,
    "research": 1,
    "depots": 2,
    "shipyards": 1,
}


def upgrade_cost(building_key, current_level):
    base = INDUSTRY[building_key]["upgrade_cost"]
    factor = current_level + 1
    return {res: int(amount * factor) for res, amount in base.items()}


@dataclass
class CampaignState:
    name: str
    mode: str = "Grand Campaign"
    player_side: str = "Blue"
    blue_nation: str = ""
    red_nation: str = ""
    difficulty: str = "Veteran"
    turn: int = 1
    resources: dict = field(default_factory=dict)
    industry: dict = field(default_factory=lambda: dict(STARTING_INDUSTRY))
    armies: list = field(default_factory=list)
    log: list = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    last_saved: str = ""
    save_slot: str = ""
    dirty: bool = field(default=False, compare=False)

    @classmethod
    def new(cls, name, mode, player_side, blue_nation, red_nation, difficulty):
        multiplier = GAME_MODES[mode]["resource_multiplier"] * DIFFICULTIES[difficulty]
        state = cls(
            name=name,
            mode=mode,
            player_side=player_side,
            blue_nation=blue_nation,
            red_nation=red_nation,
            difficulty=difficulty,
            resources={k: int(v * multiplier) for k, v in BASE_RESOURCES.items()},
        )
        state.add_log(f"Campaign '{name}' begins. {player_side} command assumed.")
        state.dirty = True
        return state

    @property
    def player_nation(self):
        return self.blue_nation if self.player_side == "Blue" else self.red_nation

    @property
    def turn_limit(self):
        return GAME_MODES.get(self.mode, {}).get("turn_limit")

    def add_log(self, message):
        self.log.insert(0, f"T{self.turn}: {message}")
        del self.log[50:]
        self.dirty = True

    def production(self):
        totals = {k: 0 for k in RESOURCES}
        for key, level in self.industry.items():
            for res, amount in INDUSTRY[key]["produces"].items():
                totals[res] += amount * level
        return totals

    def can_afford(self, cost):
        return all(self.resources.get(res, 0) >= amount for res, amount in cost.items())

    def spend(self, cost):
        if not self.can_afford(cost):
            return False
        for res, amount in cost.items():
            self.resources[res] -= amount
        self.dirty = True
        return True

    def refund(self, cost, fraction=0.5):
        for res, amount in cost.items():
            self.resources[res] = self.resources.get(res, 0) + int(amount * fraction)
        self.dirty = True

    def upgrade_building(self, key):
        cost = upgrade_cost(key, self.industry.get(key, 0))
        if not self.spend(cost):
            return False
        self.industry[key] = self.industry.get(key, 0) + 1
        self.add_log(f"{INDUSTRY[key]['name']} expanded to level {self.industry[key]}.")
        return True

    def end_turn(self):
        produced = self.production()
        for res, amount in produced.items():
            self.resources[res] = self.resources.get(res, 0) + amount
        summary = ", ".join(f"+{v} {k}" for k, v in produced.items() if v)
        self.add_log(f"Industrial output: {summary}.")
        self.turn += 1
        self.add_log("New strategic turn begins.")
        return produced

    def to_dict(self):
        data = asdict(self)
        data.pop("dirty", None)
        data["version"] = SAVE_VERSION
        return data

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data.pop("version", None)
        known = {f for f in cls.__dataclass_fields__}
        state = cls(**{k: v for k, v in data.items() if k in known})
        for res, amount in BASE_RESOURCES.items():
            state.resources.setdefault(res, 0)
        for key in INDUSTRY:
            state.industry.setdefault(key, 0)
        return state


class SaveManager:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    @staticmethod
    def slot_id(slot_name):
        slug = re.sub(r"[^A-Za-z0-9_-]+", "_", slot_name.strip()).strip("_")
        return slug or "campaign"

    def path_for(self, slot_name):
        return os.path.join(self.save_dir, f"{self.slot_id(slot_name)}.json")

    def exists(self, slot_name):
        return os.path.exists(self.path_for(slot_name))

    def save(self, state, slot_name):
        state.last_saved = datetime.now().isoformat(timespec="seconds")
        state.save_slot = slot_name
        payload = state.to_dict()
        payload["slot_name"] = slot_name
        path = self.path_for(slot_name)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp_path, path)
        state.dirty = False
        return path

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        state = CampaignState.from_dict(data)
        state.save_slot = data.get("slot_name", state.save_slot or state.name)
        state.dirty = False
        return state

    def delete(self, path):
        if os.path.exists(path):
            os.remove(path)

    def list_saves(self):
        saves = []
        for filename in os.listdir(self.save_dir):
            if not filename.endswith(".json") or filename == "settings.json":
                continue
            path = os.path.join(self.save_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            saves.append({
                "path": path,
                "slot_name": data.get("slot_name", filename[:-5]),
                "name": data.get("name", "Unknown"),
                "mode": data.get("mode", ""),
                "turn": data.get("turn", 1),
                "side": data.get("player_side", ""),
                "nation": data.get("blue_nation") if data.get("player_side") == "Blue" else data.get("red_nation"),
                "last_saved": data.get("last_saved", ""),
                "mtime": os.path.getmtime(path),
            })
        saves.sort(key=lambda s: s["mtime"], reverse=True)
        return saves

    def latest(self):
        saves = self.list_saves()
        return saves[0] if saves else None

    def load_settings(self):
        path = os.path.join(self.save_dir, "settings.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def save_settings(self, settings):
        path = os.path.join(self.save_dir, "settings.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
