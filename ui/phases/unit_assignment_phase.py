"""
ui/phases/unit_assignment_phase.py
"""

import customtkinter as ctk
from tkinter import messagebox


class UnitAssignmentPhase:
    def __init__(self, app):
        self.app = app
        self.blue_assignments = []   # list of dicts for easier reference
        self.red_assignments = []

    def build(self, parent):
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(padx=30, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="UNIT NAME & TYPE ASSIGNMENTS", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        side_frame = ctk.CTkFrame(frame)
        side_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # ==================== BLUE FORCE ====================
        blue_f = ctk.CTkFrame(side_frame)
        blue_f.pack(side="left", fill="both", expand=True, padx=20)
        ctk.CTkLabel(blue_f, text="BLUE FORCE", text_color="cyan", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.blue_country_combo = ctk.CTkOptionMenu(blue_f, 
                                                     values=["Select Country"] + self.app.data.get_countries(), 
                                                     command=self.set_blue_country, width=200)
        self.blue_country_combo.set("Select Country")
        self.blue_country_combo.pack(pady=8)

        self.blue_assignments = []
        for i in range(8):
            row = ctk.CTkFrame(blue_f)
            row.pack(fill="x", pady=6, padx=10)
            
            ctk.CTkLabel(row, text=f"B{i+1}:").pack(side="left", padx=5)
            name_entry = ctk.CTkEntry(row, width=90, placeholder_text=f"B{i+1}")
            name_entry.pack(side="left", padx=5)

            type_combo = ctk.CTkOptionMenu(row, values=[
                "Select Type", "Tank / AFV", "Infantry Squad", 
                "Infantry Platoon", "Artillery Support", "Support Weapon Team"
            ], width=150)
            type_combo.set("Select Type")
            type_combo.pack(side="left", padx=5)

            unit_combo = ctk.CTkOptionMenu(row, values=["Select Unit"], width=200)
            unit_combo.pack(side="left", padx=5)

            class_combo = ctk.CTkOptionMenu(row, values=[
                "Select Class", "A - Elite (+2)", "B - Veteran (+1)", 
                "C - Battle Tested (0)", "D - Recruit (-1)", "E - Civilian (-2)"
            ], width=140)
            class_combo.set("Select Class")
            class_combo.pack(side="left", padx=5)

            # Store as dict for easier access
            self.blue_assignments.append({
                "row": row,
                "name_entry": name_entry,
                "type_combo": type_combo,
                "unit_combo": unit_combo,
                "class_combo": class_combo
            })

            # Bind type change
            type_combo.configure(command=lambda _, entry=self.blue_assignments[-1]: self.update_unit_options(entry))

        # ==================== RED FORCE ====================
        red_f = ctk.CTkFrame(side_frame)
        red_f.pack(side="right", fill="both", expand=True, padx=20)
        ctk.CTkLabel(red_f, text="RED FORCE", text_color="red", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.red_country_combo = ctk.CTkOptionMenu(red_f, 
                                                    values=["Select Country"] + self.app.data.get_countries(), 
                                                    command=self.set_red_country, width=200)
        self.red_country_combo.set("Select Country")
        self.red_country_combo.pack(pady=8)

        self.red_assignments = []
        for i in range(8):
            row = ctk.CTkFrame(red_f)
            row.pack(fill="x", pady=6, padx=10)
            
            ctk.CTkLabel(row, text=f"R{i+1}:").pack(side="left", padx=5)
            name_entry = ctk.CTkEntry(row, width=90, placeholder_text=f"R{i+1}")
            name_entry.pack(side="left", padx=5)

            type_combo = ctk.CTkOptionMenu(row, values=[
                "Select Type", "Tank / AFV", "Infantry Squad", 
                "Infantry Platoon", "Artillery Support", "Support Weapon Team"
            ], width=150)
            type_combo.set("Select Type")
            type_combo.pack(side="left", padx=5)

            unit_combo = ctk.CTkOptionMenu(row, values=["Select Unit"], width=200)
            unit_combo.pack(side="left", padx=5)

            class_combo = ctk.CTkOptionMenu(row, values=[
                "Select Class", "A - Elite (+2)", "B - Veteran (+1)", 
                "C - Battle Tested (0)", "D - Recruit (-1)", "E - Civilian (-2)"
            ], width=140)
            class_combo.set("Select Class")
            class_combo.pack(side="left", padx=5)

            self.red_assignments.append({
                "row": row,
                "name_entry": name_entry,
                "type_combo": type_combo,
                "unit_combo": unit_combo,
                "class_combo": class_combo
            })

            type_combo.configure(command=lambda _, entry=self.red_assignments[-1]: self.update_unit_options(entry))

        ctk.CTkButton(frame, text="💾 Save Units", 
                      command=self.save_units,
                      height=50, fg_color="darkgreen", 
                      font=ctk.CTkFont(size=15, weight="bold")).pack(pady=30)

    def update_unit_options(self, assignment):
        """Update unit dropdown when Type changes"""
        type_selected = assignment["type_combo"].get()
        unit_combo = assignment["unit_combo"]
        country = self.app.blue_country if assignment in self.blue_assignments else self.app.red_country

        if not country or country == "Select Country":
            unit_combo.configure(values=["Select Country First"])
            return

        units = []

        if type_selected == "Tank / AFV":
            units = [t.get("MODEL", "Unknown") for t in self.app.data.tanks.get(country, [])]
        elif "Infantry" in type_selected:
            units = [i.get("UNIT_NAME", "Unknown") for i in self.app.data.infantry.get(country, [])]
        elif type_selected == "Artillery Support":
            units = [a.get("UNIT_NAME", "Unknown") for a in self.app.data.artillery.get(country, [])]
        else:
            units = []

        unit_combo.configure(values=["Select Unit"] + units)

    def set_blue_country(self, choice):
        self.app.blue_country = choice if choice != "Select Country" else None
        if self.app.blue_country:
            for assignment in self.blue_assignments:
                self.update_unit_options(assignment)

    def set_red_country(self, choice):
        self.app.red_country = choice if choice != "Select Country" else None
        if self.app.red_country:
            for assignment in self.red_assignments:
                self.update_unit_options(assignment)

    def save_units(self):
        self.app.blue_units.clear()
        self.app.red_units.clear()

        # Blue Units
        for assignment in self.blue_assignments:
            name = assignment["name_entry"].get().strip()
            unit_type = assignment["type_combo"].get()
            unit_name = assignment["unit_combo"].get()
            troop_class = assignment["class_combo"].get()
            
            if name and unit_type != "Select Type" and unit_name != "Select Unit" and troop_class != "Select Class":
                if unit_type == "Tank / AFV":
                    data = self.app.data.get_tank_by_name(self.app.blue_country, unit_name)
                else:
                    data = None

                self.app.blue_units.append({
                    "name": name,
                    "country": self.app.blue_country,
                    "unit_type": unit_type,
                    "unit_name": unit_name,
                    "tank": unit_name,           # Compatibility with Command Phase
                    "data": data,
                    "troop_class": troop_class,
                    "troop_modifier": self.app.get_troop_modifier(troop_class)
                })

        # Red Units
        for assignment in self.red_assignments:
            name = assignment["name_entry"].get().strip()
            unit_type = assignment["type_combo"].get()
            unit_name = assignment["unit_combo"].get()
            troop_class = assignment["class_combo"].get()
            
            if name and unit_type != "Select Type" and unit_name != "Select Unit" and troop_class != "Select Class":
                if unit_type == "Tank / AFV":
                    data = self.app.data.get_tank_by_name(self.app.red_country, unit_name)
                else:
                    data = None

                self.app.red_units.append({
                    "name": name,
                    "country": self.app.red_country,
                    "unit_type": unit_type,
                    "unit_name": unit_name,
                    "tank": unit_name,           # Compatibility with Command Phase
                    "data": data,
                    "troop_class": troop_class,
                    "troop_modifier": self.app.get_troop_modifier(troop_class)
                })

        if len(self.app.blue_units) + len(self.app.red_units) == 0:
            messagebox.showwarning("No Units", "Please assign at least one complete unit.")
            return

        messagebox.showinfo("Units Saved", 
            f"✅ Saved {len(self.app.blue_units)} Blue and {len(self.app.red_units)} Red units.\n"
            f"Go to Command Phase to set orders.")