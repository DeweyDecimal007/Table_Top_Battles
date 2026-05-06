"""
ui/phases/movement_phase.py
"""

import customtkinter as ctk
from tkinter import messagebox


class MovementPhase:
    def __init__(self, app):
        self.app = app
        self.moved_vars = {}
        self.terrain_vars = {}
        self.advance_btn = None
        self.list_frame = None

    def build(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(self.frame, text="PHASE 2: MOVEMENT PHASE", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=15)

        # Refresh Button
        ctk.CTkButton(self.frame, text="🔄 Refresh Movement List", 
                      command=self.populate_movement_list,
                      fg_color="#1f6aa5").pack(pady=8)

        # Header
        header = ctk.CTkFrame(self.frame, fg_color="#2b2b2b")
        header.pack(fill="x", padx=40, pady=8)
        cols = ["#", "Side", "Country", "Unit Name", "Tank", "Orders", "Terrain", "MOVED"]
        widths = [40, 80, 100, 120, 160, 160, 140, 90]
        for text, w in zip(cols, widths):
            ctk.CTkLabel(header, text=text, width=w, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=4)

        # Units List
        self.list_frame = ctk.CTkFrame(self.frame)
        self.list_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Advance Button
        self.advance_btn = ctk.CTkButton(self.frame, text="Advance to Melee Phase →", 
                                         command=lambda: self.app.tabview.set("3. Melee"),
                                         height=50, fg_color="darkgreen", 
                                         font=ctk.CTkFont(size=16, weight="bold"))
        self.advance_btn.pack(pady=25)
        self.advance_btn.configure(state="disabled")

        # Initial population
        self.populate_movement_list()

    def populate_movement_list(self):
        if not self.list_frame:
            return

        # Clear old rows
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.app.activation_order:
            ctk.CTkLabel(self.list_frame, text="No activation order yet.\n\nGo to Command Phase first and generate order.", 
                         font=ctk.CTkFont(size=16), text_color="orange").pack(pady=80)
            return

        self.moved_vars.clear()
        self.terrain_vars.clear()

        for idx, (unit_name, number) in enumerate(self.app.activation_order):
            unit = next((u for u in self.app.blue_units + self.app.red_units if u["name"] == unit_name), None)
            if not unit:
                continue

            row = ctk.CTkFrame(self.list_frame, fg_color="#1f1f1f")
            row.pack(fill="x", pady=4, padx=5)

            ctk.CTkLabel(row, text=f"{number}", width=40).pack(side="left", padx=8)
            
            side_color = "cyan" if unit["country"] == self.app.blue_country else "red"
            side_text = "BLUE" if unit["country"] == self.app.blue_country else "RED"
            ctk.CTkLabel(row, text=side_text, text_color=side_color, width=80).pack(side="left", padx=8)

            ctk.CTkLabel(row, text=unit["country"], width=100).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=unit["name"], width=120).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=unit.get("tank", "—"), width=160).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=unit.get("order", "—"), width=160).pack(side="left", padx=8)

            # Terrain
            terrain_var = ctk.StringVar(value="Select Terrain")
            terrain_combo = ctk.CTkOptionMenu(row, values=[
                "Select Terrain", "Open Ground", "Woods", "Urban", "Hills", 
                "Rough Terrain", "River", "Entrenched", "Hull Down"
            ], variable=terrain_var, width=135)
            terrain_combo.pack(side="left", padx=8)
            self.terrain_vars[unit_name] = terrain_var

            # MOVED Checkbox
            moved_var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(row, text="MOVED", variable=moved_var, 
                                  command=self.check_all_moved)
            chk.pack(side="left", padx=12)
            self.moved_vars[unit_name] = moved_var

        self.check_all_moved()

    def check_all_moved(self):
        if not self.moved_vars:
            return
        all_moved = all(var.get() for var in self.moved_vars.values())
        if self.advance_btn:
            self.advance_btn.configure(state="normal" if all_moved else "disabled")