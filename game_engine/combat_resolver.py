"""
game_engine/combat_resolver.py
Resolution logic and result text generation
"""

import random


class CombatResolver:
    """Takes math results and produces final outcomes + text"""

    @staticmethod
    def resolve_to_hit(needed):
        roll = random.randint(1, 20)
        hit = roll <= needed
        return hit, roll, f"Needed ≤{needed} | Rolled {roll}"

    @staticmethod
    def resolve_penetration(gun_pen, armor_value, distance=None):
        x = gun_pen - armor_value

        lookup = {15:20,14:19,13:18,12:17,11:16,10:15,9:14,8:13,7:12,6:11,
                  5:10,4:9,3:8,2:7,1:6,0:5,-1:4,-2:3,-3:2,-4:1}
        needed_roll = lookup.get(x, 1)

        pen_roll = random.randint(1, 20)
        penetrated = pen_roll <= needed_roll
        is_catastrophic = penetrated and (pen_roll <= (x // 2) if x > 0 else False)

        return x, needed_roll, pen_roll, penetrated, is_catastrophic

    @staticmethod
    def get_damage_text(penetrated, is_catastrophic):
        if not penetrated:
            roll = random.randint(1, 6)
            if roll == 1:
                return "Radio knocked out"
            elif roll in (2, 3):
                return "Machineguns disabled"
            else:
                return "No significant damage"

        if is_catastrophic:
            return "💥 CATASTROPHIC PENETRATION! Vehicle destroyed, crew KIA."

        roll = random.randint(1, 6)
        texts = ["Engine knocked out", "Turret disabled", "Main gun disabled",
                 "Crew damage", "Tracks damaged", "Minor damage"]
        return texts[roll-1]
    
    @staticmethod
    def resolve_melee_casualties(winner, loser, loser_pool_size):
        """75% Wounded / 25% KIA split"""
        if loser_pool_size <= 0:
            return "No casualties."

        # Base casualties roughly based on pool size difference
        base_casualties = max(1, loser_pool_size // 3)

        kia = max(1, int(base_casualties * 0.25))
        wounded = base_casualties - kia

        if winner == "attacker":
            return f"**MELEE RESULT:** Attacker wins!\n" \
                   f"Loser suffers {wounded} Wounded + {kia} KIA"
        else:
            return f"**MELEE RESULT:** Defender wins!\n" \
                   f"Attacker suffers {wounded} Wounded + {kia} KIA"    