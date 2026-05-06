"""
game_engine/combat_calculator.py
Pure math only
"""

import random   # ← Add this line


class CombatCalculator:

    """All math calculations"""

    @staticmethod
    def get_order_modifier(order_text):
        """Returns modifier based on Command Phase order"""
        if not order_text or order_text == "—":
            return 0
        order = order_text.strip().lower()
        
        if "hold position" in order:
            return 0
        elif "move cautious" in order:
            return -1
        elif "move full speed" in order:
            return -2
        elif "overwatch" in order:
            return +1
        elif "fire on last target" in order:
            return +3
        else:
            return 0

    @staticmethod
    def get_range_modifier(distance, gun_data):
        try:
            rs = int(gun_data.get("RANGE_S") or 0)
            rm = int(gun_data.get("RANGE_M") or 0)
            rl = int(gun_data.get("RANGE_L") or 0)
        except:
            return 0, "UNKNOWN"

        if distance > rl:
            return None, "OUT OF RANGE"
        elif distance <= rs:
            return 2, "SHORT"
        elif distance <= rm:
            return 0, "MEDIUM"
        else:
            return -2, "LONG"

    @staticmethod
    def calculate_to_hit_needed(base=11, troop_mod=0, range_mod=0, order_mod=0):
        """Calculate final To Hit needed with all modifiers"""
        total_mod = troop_mod + range_mod + order_mod
        needed = base + total_mod
        return max(2, min(20, needed)), total_mod

    @staticmethod
    def calculate_penetration_x(gun_data, distance):
        try:
            rs = int(gun_data.get("RANGE_S") or 0)
            rm = int(gun_data.get("RANGE_M") or 0)
            rl = int(gun_data.get("RANGE_L") or 0)
        except:
            rs = rm = rl = 0

        if distance <= rs:
            pen_key = "PENETRATION_S"
        elif distance <= rm:
            pen_key = "PENETRATION_M"
        else:
            pen_key = "PENETRATION_L"

        gun_pen = int(gun_data.get(pen_key) or 0)
        return gun_pen, pen_key
    
    @staticmethod
    def calculate_melee_dice_pool(unit, terrain_modifier=0):
        """Chain of Command style dice pool"""
        base = 4  # Average starting pool

        # Troop quality
        troop_mod = unit.get("troop_modifier", 0)
        quality = base + troop_mod * 2

        # Simple terrain/cover
        final_pool = max(2, quality + terrain_modifier)

        return final_pool

    @staticmethod
    def resolve_opposed_melee(attacker_pool, defender_pool):
        """Opposed roll - higher total wins"""
        attacker_rolls = [random.randint(1, 6) for _ in range(attacker_pool)]
        defender_rolls = [random.randint(1, 6) for _ in range(defender_pool)]

        attacker_total = sum(attacker_rolls)
        defender_total = sum(defender_rolls)

        return {
            "attacker_total": attacker_total,
            "defender_total": defender_total,
            "attacker_rolls": attacker_rolls,
            "defender_rolls": defender_rolls,
            "winner": "attacker" if attacker_total > defender_total else "defender" if defender_total > attacker_total else "tie"
        }    