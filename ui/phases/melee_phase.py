"""
ui/phases/melee_phase.py
"""

import customtkinter as ctk
from tkinter import messagebox

from game_engine.combat_calculator import CombatCalculator
from game_engine.combat_resolver import CombatResolver


class MeleePhase:
    def __init__(self, app):
        self.app = app
        self.attacker_checks = []
        self.defender_checks = []
        self.result_textbox = None

    def build(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(self.frame, text="PHASE 3: MELEE PHASE", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=15)

        # Refresh Button
        ctk.CTkButton(self.frame, text="🔄 Refresh Unit Lists", 
                      command=self.populate_unit_lists,
                      fg_color="#1f6aa5").pack(pady=8)

        # Attacker Section
        ctk.CTkLabel(self.frame, text="ATTACKERS (Select Multiple)", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=40, pady=(15,5))
        self.attacker_frame = ctk.CTkFrame(self.frame)
        self.attacker_frame.pack(fill="x", padx=40, pady=5)

        # Defender Section
        ctk.CTkLabel(self.frame, text="DEFENDERS (Select Multiple)", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=40, pady=(15,5))
        self.defender_frame = ctk.CTkFrame(self.frame)
        self.defender_frame.pack(fill="x", padx=40, pady=5)

        ctk.CTkButton(self.frame, text="⚔️ Resolve Melee Combat", 
                      command=self.resolve_melee,
                      fg_color="darkred", height=50, 
                      font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

        # Result Box
        ctk.CTkLabel(self.frame, text="Melee Resolution Result:", 
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=40, pady=(10,5))
        self.result_textbox = ctk.CTkTextbox(self.frame, height=300, font=ctk.CTkFont(size=13))
        self.result_textbox.pack(fill="x", padx=40, pady=5)

        ctk.CTkButton(self.frame, text="Advance to Fire Phase →", 
                      command=lambda: self.app.tabview.set("4. Fire Phase"),
                      height=45).pack(pady=20)

        # Auto-populate when tab is built
        self.populate_unit_lists()

    def populate_unit_lists(self):
        """Populate attacker and defender lists from all saved units"""
        # Clear old widgets
        for widget in self.attacker_frame.winfo_children():
            widget.destroy()
        for widget in self.defender_frame.winfo_children():
            widget.destroy()

        all_units = self.app.blue_units + self.app.red_units
        if not all_units:
            ctk.CTkLabel(self.attacker_frame, text="No units assigned yet.\nGo to Unit Name Assignments first.").pack(pady=40)
            return

        self.attacker_checks.clear()
        self.defender_checks.clear()

        for unit in all_units:
            display_name = f"{unit['country']} {unit.get('unit_name', unit.get('tank', unit.get('name', 'Unknown')))}"

            # Attacker checkbox
            var_a = ctk.BooleanVar()
            chk_a = ctk.CTkCheckBox(self.attacker_frame, text=display_name, variable=var_a)
            chk_a.pack(anchor="w", pady=2, padx=10)
            self.attacker_checks.append((unit, var_a))

            # Defender checkbox
            var_d = ctk.BooleanVar()
            chk_d = ctk.CTkCheckBox(self.defender_frame, text=display_name, variable=var_d)
            chk_d.pack(anchor="w", pady=2, padx=10)
            self.defender_checks.append((unit, var_d))

    def resolve_melee(self):
        attackers = [u for u, v in self.attacker_checks if v.get()]
        defenders = [u for u, v in self.defender_checks if v.get()]

        if not attackers or not defenders:
            messagebox.showwarning("Selection Required", "Please select at least one attacker and one defender.")
            return

        result_text = "**MELEE COMBAT RESOLUTION**\n\n"

        for attacker in attackers:
            for defender in defenders:
                a_pool = CombatCalculator.calculate_melee_dice_pool(attacker)
                d_pool = CombatCalculator.calculate_melee_dice_pool(defender, terrain_modifier=-1)

                outcome = CombatCalculator.resolve_opposed_melee(a_pool, d_pool)
                damage = CombatResolver.resolve_melee_casualties(
                    outcome["winner"], "loser", 
                    d_pool if outcome["winner"] == "attacker" else a_pool
                )

                result_text += f"**{attacker.get('unit_name', attacker.get('tank', attacker['name']))}** vs "
                result_text += f"**{defender.get('unit_name', defender.get('tank', defender['name']))}**\n"
                result_text += f"Attacker Pool: {a_pool} | Defender Pool: {d_pool}\n"
                result_text += f"Result: {damage}\n\n"

        self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("end", result_text)