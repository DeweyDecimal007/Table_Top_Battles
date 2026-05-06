"""
ui/phases/command_phase.py
"""

import customtkinter as ctk
from tkinter import messagebox
import random


class CommandPhase:
    def __init__(self, app):
        self.app = app
        self.order_vars = {}
        self.roll_used_this_turn = False
        self.orders_saved = False
        self.save_btn = None
        self.advance_btn = None
        self.roll_btn = None

    def build(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(self.frame, text="PHASE 1: COMMAND PHASE", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=15)

        summary_frame = ctk.CTkFrame(self.frame)
        summary_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Blue Side
        self.blue_frame = ctk.CTkFrame(summary_frame)
        self.blue_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        ctk.CTkLabel(self.blue_frame, text="BLUE FORCE", text_color="cyan", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)
        self.blue_list = ctk.CTkFrame(self.blue_frame)
        self.blue_list.pack(fill="both", expand=True)

        # Red Side
        self.red_frame = ctk.CTkFrame(summary_frame)
        self.red_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))
        ctk.CTkLabel(self.red_frame, text="RED FORCE", text_color="red", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)
        self.red_list = ctk.CTkFrame(self.red_frame)
        self.red_list.pack(fill="both", expand=True)

        # Activation Order
        ctk.CTkLabel(self.frame, text="🎲 ACTIVATION ORDER", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(25,5))

        self.order_text = ctk.CTkTextbox(self.frame, height=180, width=720, font=ctk.CTkFont(size=14))
        self.order_text.pack(pady=10, padx=40)

        # Buttons
        btn_frame = ctk.CTkFrame(self.frame)
        btn_frame.pack(pady=25)

        self.roll_btn = ctk.CTkButton(btn_frame, text="🎲 Roll Activation Order", 
                                      command=self.generate_and_display_order,
                                      fg_color="#1f6aa5", height=48, width=240)
        self.roll_btn.pack(side="left", padx=12)

        self.save_btn = ctk.CTkButton(btn_frame, text="💾 Save Current Orders", 
                                      command=self.save_orders_to_units,
                                      fg_color="darkgreen", height=48, width=240, state="disabled")
        self.save_btn.pack(side="left", padx=12)

        self.advance_btn = ctk.CTkButton(btn_frame, text="Advance to Movement Phase →", 
                                         command=lambda: self.app.tabview.set("2. Movement"),
                                         height=48, width=240, state="disabled")
        self.advance_btn.pack(side="left", padx=12)

        self.generate_and_display_order()   # Auto-roll on first visit

    def generate_and_display_order(self):
        if len(self.app.blue_units) + len(self.app.red_units) == 0:
            self.order_text.delete("1.0", "end")
            self.order_text.insert("end", "No units assigned yet.\nGo to Unit Name Assignments first.")
            return

        if self.roll_used_this_turn:
            messagebox.showinfo("Once Per Turn", "You can only roll the activation order once per turn.")
            return

        all_units = self.app.blue_units + self.app.red_units
        random.shuffle(all_units)
        self.app.activation_order = [(u["name"], i+1) for i, u in enumerate(all_units)]
        self.app.current_fire_index = 0
        self.roll_used_this_turn = True

        self.populate_unit_lists()
        self.update_button_states()

    def populate_unit_lists(self):
        """Populate Blue and Red unit lists with safe key handling"""
        # Clear old widgets
        for widget in self.blue_list.winfo_children():
            widget.destroy()
        for widget in self.red_list.winfo_children():
            widget.destroy()

        if not self.app.blue_units and not self.app.red_units:
            ctk.CTkLabel(self.blue_list, text="No units assigned yet.\nGo to Unit Name Assignments first.").pack(pady=40)
            return

        # Blue Side
        for unit in self.app.blue_units:
            self.create_unit_row(self.blue_list, unit)

        # Red Side
        for unit in self.app.red_units:
            self.create_unit_row(self.red_list, unit)

    def create_unit_row(self, parent, unit):
        """Create a row for a unit with order dropdown"""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", pady=4, padx=10)

        # Display name safely
        display_name = unit.get("tank") or unit.get("unit_name") or unit.get("name") or "Unknown"
        
        ctk.CTkLabel(row, text=unit.get("name", "—"), width=100, anchor="w").pack(side="left", padx=8)
        ctk.CTkLabel(row, text=display_name, text_color="lightgray", width=180).pack(side="left", padx=8)

        # Order dropdown
        var = ctk.StringVar(value="Select Order")
        combo = ctk.CTkOptionMenu(row, values=[
            "Select Order",
            "Hold Position (0)",
            "Move Cautious (-1)",
            "Move Full Speed (-2)",
            "Overwatch (+1)",
            "Fire on Last Target (+3)"
        ], variable=var, width=200)
        combo.pack(side="right", padx=8)
        self.order_vars[unit["name"]] = var

        var.trace_add("write", lambda *args: self.update_button_states())

    def update_button_states(self):
        all_have_orders = all(
            self.order_vars.get(u["name"], ctk.StringVar(value="Select Order")).get() != "Select Order"
            for u in self.app.blue_units + self.app.red_units
        )
        self.save_btn.configure(state="normal" if all_have_orders else "disabled")
        self.advance_btn.configure(state="normal" if self.orders_saved else "disabled")

    def save_orders_to_units(self):
        for unit in self.app.blue_units + self.app.red_units:
            if unit["name"] in self.order_vars:
                order = self.order_vars[unit["name"]].get()
                unit["order"] = order if order != "Select Order" else "—"

        self.orders_saved = True
        messagebox.showinfo("Saved", "Orders have been saved to all units.")
        self.update_button_states()