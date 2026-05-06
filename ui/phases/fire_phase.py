"""
ui/phases/fire_phase.py
UI Only - Layout + Display.
"""

import customtkinter as ctk
import random
from tkinter import messagebox   # ← Add this line

from game_engine.combat_calculator import CombatCalculator
from game_engine.combat_resolver import CombatResolver


class FirePhase:
    def __init__(self, app):
        self.app = app
        self.result_textbox = None

    def build(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        # Title + Refresh
        top_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        top_row.pack(fill="x", pady=10, padx=40)
        self.fire_title = ctk.CTkLabel(top_row, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.fire_title.pack(side="left")
        ctk.CTkButton(top_row, text="🔄 Refresh Fire Phase", 
                      command=self.show_current_firing_unit,
                      fg_color="gray", width=180).pack(side="right", padx=10)

        self.current_unit_label = ctk.CTkLabel(self.frame, text="", font=ctk.CTkFont(size=16))
        self.current_unit_label.pack(pady=5, padx=40, anchor="w")

        # Main Layout
        main_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_row.pack(fill="both", expand=True, padx=40, pady=10)

        # Left - Inputs
        left = ctk.CTkFrame(main_row, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0,30))

        ctk.CTkLabel(left, text="Gun:").pack(anchor="w")
        self.gun_combo = ctk.CTkOptionMenu(left, values=["Select Gun"], height=28, width=320,
                                           command=self.update_ammo_dropdown)
        self.gun_combo.pack(fill="x", pady=5)

        ctk.CTkLabel(left, text="Ammunition:").pack(anchor="w")
        self.ammo_combo = ctk.CTkOptionMenu(left, values=["Select Ammo"], height=28, width=320)
        self.ammo_combo.pack(fill="x", pady=5)

        ctk.CTkLabel(left, text="Target:").pack(anchor="w")
        self.target_combo = ctk.CTkOptionMenu(left, values=["Select Target"], height=28, width=320)
        self.target_combo.pack(fill="x", pady=5)

        ctk.CTkLabel(left, text="Distance (meters):").pack(anchor="w")
        self.dist_entry = ctk.CTkEntry(left, placeholder_text="500", width=140, height=28)
        self.dist_entry.pack(anchor="w", pady=5)

        ctk.CTkLabel(left, text="Fire Type:").pack(anchor="w", pady=(12,5))
        self.fire_type_var = ctk.StringVar(value="Direct")
        ctk.CTkRadioButton(left, text="Direct", variable=self.fire_type_var, value="Direct").pack(anchor="w")
        ctk.CTkRadioButton(left, text="Indirect", variable=self.fire_type_var, value="Indirect").pack(anchor="w")

        # Buttons
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.pack(pady=25, fill="x")
        ctk.CTkButton(btn_frame, text="🔥 Resolve Fire", command=self.resolve_current_unit_fire,
                      fg_color="darkred", width=170, height=42, font=ctk.CTkFont(size=15, weight="bold")).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Next Unit →", command=self.next_firing_unit,
                      fg_color="darkgreen", width=170, height=42).pack(side="left", padx=8)

        # Result Display Box
        ctk.CTkLabel(left, text="Resolution Result:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20,5))
        self.result_textbox = ctk.CTkTextbox(left, height=260, font=ctk.CTkFont(size=13))
        self.result_textbox.pack(fill="x", pady=5)

        # ====================== RIGHT SIDE - ARMOR FACING ======================
        right = ctk.CTkFrame(main_row, fg_color="#1f1f1f", width=360)
        right.pack(side="right", fill="y", padx=20, pady=10)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="TARGET ARMOR FACING", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        facing_frame = ctk.CTkFrame(right, fg_color="transparent")
        facing_frame.pack(pady=10, fill="x", padx=20)

        # Save button references
        self.front_btn = ctk.CTkButton(facing_frame, text="FRONT", width=140, height=40,
                                       command=lambda: self.select_facing("FRONT"))
        self.front_btn.pack(pady=6)

        self.left_side_btn = ctk.CTkButton(facing_frame, text="LEFT SIDE", width=140, height=40,
                                           command=lambda: self.select_facing("LEFT SIDE"))
        self.left_side_btn.pack(pady=6)

        self.right_side_btn = ctk.CTkButton(facing_frame, text="RIGHT SIDE", width=140, height=40,
                                            command=lambda: self.select_facing("RIGHT SIDE"))
        self.right_side_btn.pack(pady=6)

        self.rear_btn = ctk.CTkButton(facing_frame, text="REAR", width=140, height=40,
                                      command=lambda: self.select_facing("REAR"))
        self.rear_btn.pack(pady=6)

        self.top_btn = ctk.CTkButton(facing_frame, text="TOP", width=140, height=40,
                                     command=lambda: self.select_facing("TOP"))
        self.top_btn.pack(pady=6)

        self.populate_initial_facing()

    def populate_initial_facing(self):
        self.app.selected_facing.set("FRONT")
        self.update_facing_buttons()

    def select_facing(self, facing):
        self.app.selected_facing.set(facing)
        self.update_facing_buttons()

    def update_facing_buttons(self):
        selected = self.app.selected_facing.get()
        for btn, name in [
            (self.front_btn, "FRONT"),
            (self.left_side_btn, "LEFT SIDE"),
            (self.right_side_btn, "RIGHT SIDE"),
            (self.rear_btn, "REAR"),
            (self.top_btn, "TOP")
        ]:
            if btn:
                btn.configure(fg_color="green" if selected == name else "#1f6aa5")

    # ====================== YOUR WORKING METHODS ======================
    def show_current_firing_unit(self):
        if not self.app.activation_order or self.app.current_fire_index >= len(self.app.activation_order):
            self.fire_title.configure(text="Fire Phase")
            self.current_unit_label.configure(text="No units left to fire")
            self.gun_combo.configure(values=["Select Gun"])
            return

        unit_name, unit_number = self.app.activation_order[self.app.current_fire_index]
        self.fire_title.configure(text=f"Firing Unit #{unit_number}")

        unit_dict = next((u for u in self.app.blue_units + self.app.red_units if u["name"] == unit_name), None)
        if unit_dict:
            display = f"{unit_dict['country']} {unit_dict.get('tank', 'Unknown')} {unit_name}"
            self.current_unit_label.configure(text=f"Currently Firing: {display}")

        if not unit_dict or unit_dict.get("tank") == "Select Tank":
            self.gun_combo.configure(values=["Select Gun"])
            return

        tank_data = unit_dict.get("tank_data")
        if not tank_data:
            self.gun_combo.configure(values=["Select Gun"])
            print(f"⚠️ No tank_data for {unit_dict['tank']}")
            return

        # Strong Gun Matching
        tank_model = str(unit_dict.get("tank") or "").strip().lower()
        gun_field = str(tank_data.get("GUN") or "").strip().lower()

        print(f"\n🔍 DEBUG FIRING UNIT: {unit_dict['name']} | Tank: '{tank_model}' | GUN field: '{gun_field}'")

        gun_options = ["Select Gun"]
        found = 0

        for g in self.app.data.guns.get(unit_dict["country"], []):
            gun_tank_field = str(g.get("TANK") or g.get("Tank") or "").strip().lower()
            gun_name = str(g.get("GUN") or g.get("NAME") or "").strip()

            if not gun_name:
                continue

            match = False
            if gun_tank_field and (tank_model in gun_tank_field or gun_tank_field in tank_model):
                match = True
            elif gun_field and gun_field in gun_tank_field:
                match = True
            elif any(word in gun_tank_field for word in gun_field.split(",")):
                match = True

            if match:
                rs = str(g.get("RANGE_S", "???"))
                rm = str(g.get("RANGE_M", "???"))
                rl = str(g.get("RANGE_L", "???"))
                display_gun = f"{gun_name} ({rs}/{rm}/{rl})"[:48]
                gun_options.append(display_gun)
                found += 1
                print(f"   ✅ MATCHED GUN: {gun_name} (TANK field = '{gun_tank_field}')")

        print(f"✅ Found {found} guns for this tank")

        self.gun_combo.configure(values=gun_options)
        self.ammo_combo.configure(values=["Select Ammo"])

        # Targets
        is_blue = unit_dict["country"] == self.app.blue_country
        opposing = self.app.red_units if is_blue else self.app.blue_units
        target_list = [f"{u['country']} {u.get('tank','Unknown')} {u['name']}"[:48] for u in opposing]
        self.target_combo.configure(values=target_list if target_list else ["No targets available"])

    def update_ammo_dropdown(self, selected_gun=None):
        if not selected_gun or selected_gun == "Select Gun":
            self.ammo_combo.configure(values=["Select Ammo"])
            return

        clean_gun = selected_gun.split(" (")[0].strip()
        unit_name = self.app.activation_order[self.app.current_fire_index][0]
        unit_dict = next((u for u in self.app.blue_units + self.app.red_units if u["name"] == unit_name), None)

        if unit_dict:
            ammo_list = self.app.data.get_ammo_for_gun(unit_dict["country"], clean_gun)
            print(f"🔍 Ammo search for '{clean_gun}' → Found {len(ammo_list)} types: {ammo_list}")
            self.ammo_combo.configure(values=["Select Ammo"] + ammo_list)

    def next_firing_unit(self):
        self.app.current_fire_index += 1
        if self.app.current_fire_index >= len(self.app.activation_order):
            messagebox.showinfo("Fire Phase Complete", "All units have fired this phase!")
            return
        self.show_current_firing_unit()

    # ====================== RESOLVE FIRE ======================
    def resolve_current_unit_fire(self):
        if self.app.current_fire_index >= len(self.app.activation_order):
            messagebox.showinfo("Fire Phase", "All units have fired.")
            return

        unit_name = self.app.activation_order[self.app.current_fire_index][0]
        target_display = self.target_combo.get()
        gun_full = self.gun_combo.get()
        ammo = self.ammo_combo.get()
        distance = int(self.dist_entry.get().strip() or "500")
        fire_type = self.fire_type_var.get()
        facing = self.app.selected_facing.get()

        gun = gun_full.split(" (")[0] if " (" in gun_full else gun_full

        firing_unit = next((u for u in self.app.blue_units + self.app.red_units if u["name"] == unit_name), None)
        target_unit = next((u for u in self.app.blue_units + self.app.red_units if u["name"] == target_display.split()[-1]), None)

        if not firing_unit or not target_unit:
            messagebox.showerror("Error", "Unit not found.")
            return

        # Get gun data
        gun_data = None
        for g in self.app.data.guns.get(firing_unit["country"], []):
            if str(g.get("GUN") or "").strip().lower() == gun.lower():
                gun_data = g
                break

        if not gun_data:
            messagebox.showwarning("Gun Data", f"Could not find data for gun '{gun}'.")
            return

        # ====================== MODIFIERS & TO HIT ======================
        range_mod, range_text = CombatCalculator.get_range_modifier(distance, gun_data)
        if range_mod is None:
            self.result_textbox.delete("1.0", "end")
            self.result_textbox.insert("end", "Target is OUT OF RANGE!")
            return

        troop_mod = firing_unit.get("troop_modifier", 0)
        order_mod = CombatCalculator.get_order_modifier(firing_unit.get("order", "Hold Position"))

        needed, total_mod = CombatCalculator.calculate_to_hit_needed(
            base=11, 
            troop_mod=troop_mod, 
            range_mod=range_mod,
            order_mod=order_mod          # ← Now included
        )

        hit, roll, hit_text = CombatResolver.resolve_to_hit(needed)

        # ====================== PENETRATION ======================
        armor_key = {"FRONT": "ARMOR_FRONT", "REAR": "ARMOR_REAR", "TOP": "ARMOR_TOP",
                     "LEFT SIDE": "ARMOR_SIDE", "RIGHT SIDE": "ARMOR_SIDE"}.get(facing, "ARMOR_FRONT")
        
        armor_value = int(target_unit.get("tank_data", {}).get(armor_key) or 0)

        gun_pen, pen_key = CombatCalculator.calculate_penetration_x(gun_data, distance)
        x = gun_pen - armor_value

        x_val, needed_roll, pen_roll, penetrated, is_catastrophic = CombatResolver.resolve_penetration(gun_pen, armor_value)

        # ====================== BUILD RESULT ======================
        result = f"**FIRING UNIT:** {unit_name} ({firing_unit.get('tank', 'Unknown')})\n"
        result += f"**TROOP CLASS:** {firing_unit.get('troop_class', 'Unknown')} ({troop_mod:+})\n"
        result += f"**ORDER:** {firing_unit.get('order', '—')} ({order_mod:+})\n"
        result += f"**RANGE:** {range_text} ({distance}m) → {range_mod:+}\n"
        result += f"**TARGET:** {target_display}\n"
        result += f"**FACING:** {facing}\n"
        result += f"**GUN:** {gun} | **AMMO:** {ammo}\n\n"

        # Detailed To Hit Breakdown
        result += f"**TO HIT CALCULATION:**\n"
        result += f"Base Needed: 11\n"
        result += f"Troop Modifier: {troop_mod:+}\n"
        result += f"Order Modifier: {order_mod:+}\n"
        result += f"Range Modifier: {range_mod:+}\n"
        result += f"────────────────────\n"
        result += f"Total Modifier: {total_mod:+}\n"
        result += f"Final Needed: ≤{needed}\n"
        result += f"Rolled: {roll} → {'✅ HIT' if hit else '❌ MISS'}\n\n"

        if hit:
            result += f"**PENETRATION:** x = {gun_pen} - {armor_key}({armor_value}) = **{x}**\n"
            result += f"Needed ≤{needed_roll} | Rolled {pen_roll} → {'✅ PENETRATED!' if penetrated else '❌ Failed'}\n\n"
            result += CombatResolver.get_damage_text(penetrated, is_catastrophic)

        # Display in textbox
        self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("end", result)
        print(result)