"""
main.py - Interactive Wargame Rules Assistant
"""

import customtkinter as ctk
import os
import random
from tkinter import messagebox
from PIL import Image, ImageTk

# Phase Classes
from ui.phases.unit_assignment_phase import UnitAssignmentPhase
from ui.phases.command_phase import CommandPhase
from ui.phases.movement_phase import MovementPhase
from ui.phases.melee_phase import MeleePhase
from ui.phases.fire_phase import FirePhase
from ui.phases.cc_phase import CommandControlPhase
from ui.phases.recovery_phase import RecoveryPhase

# Game Engine
from game_engine.sequence_of_play import SequenceOfPlay
from game_engine.combat_resolver import CombatResolver
from game_engine.data_loader import DataLoader
from strategic.strategic_map import StrategicMap

class WargameApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🚀 Interactive Wargame Rules Assistant")
        self.geometry("1050x760")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = r"C:\Interactive War Game Rules\data"

        self.game = SequenceOfPlay()
        self.resolver = CombatResolver()
        self.data = DataLoader(self.data_path)

        self.blue_country = None
        self.red_country = None
        self.blue_units = []
        self.red_units = []
        self.activation_order = []
        self.current_fire_index = 0
        self.selected_facing = ctk.StringVar(value="FRONT")

        self.strategic_map = None

        self.create_widgets()

    def create_widgets(self):
        title = ctk.CTkLabel(self, text="INTERACTIVE WARGAME RULES ASSISTANT", 
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=15)

        self.tabview = ctk.CTkTabview(self, width=1000, height=620)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        # Create Tabs
        self.tab_unit_assign = self.tabview.add("Unit Name Assignments")
        self.tab_command     = self.tabview.add("1. Command Phase")
        self.tab_movement    = self.tabview.add("2. Movement")
        self.tab_melee       = self.tabview.add("3. Melee")
        self.tab_fire        = self.tabview.add("4. Fire Phase")
        self.tab_cc          = self.tabview.add("5. Command & Control")
        self.tab_recovery    = self.tabview.add("6. Recovery")
        self.tab_strategic   = self.tabview.add("Strategic Command")

        self.build_all_tabs()

    def build_all_tabs(self):
        self.unit_assignment_phase = UnitAssignmentPhase(self)
        self.unit_assignment_phase.build(self.tab_unit_assign)

        self.command_phase = CommandPhase(self)
        self.command_phase.build(self.tab_command)

        self.movement_phase = MovementPhase(self)
        self.movement_phase.build(self.tab_movement)

        self.melee_phase = MeleePhase(self)
        self.melee_phase.build(self.tab_melee)

        self.fire_phase = FirePhase(self)
        self.fire_phase.build(self.tab_fire)

        self.cc_phase = CommandControlPhase(self)
        self.cc_phase.build(self.tab_cc)

        self.recovery_phase = RecoveryPhase(self)
        self.recovery_phase.build(self.tab_recovery)

        # ====================== STRATEGIC COMMAND TAB - FORCE BUILD EVERY TIME ======================
        if "Strategic Command" not in self.tabview._tab_dict:
            self.tab_strategic = self.tabview.add("Strategic Command")
            print("✅ Strategic Command tab created for the first time")
        else:
            self.tab_strategic = self.tabview.tab("Strategic Command")
            print("✅ Strategic Command tab already exists - forcing rebuild")

        self.build_strategic_tab()   # <-- This line now runs EVERY time

    def build_strategic_tab(self):
        """Strategic Command tab - now impossible to miss"""
        print("🔥 build_strategic_tab() STARTED")

        frame = ctk.CTkScrollableFrame(self.tab_strategic)
        frame.pack(padx=40, pady=40, fill="both", expand=True)
        print("✅ ScrollableFrame packed")

        ctk.CTkLabel(frame, 
                     text="🌍 STRATEGIC COMMAND\nBLUE HORIZON THEATER",
                     font=ctk.CTkFont(size=36, weight="bold"),
                     text_color="#00FF00").pack(pady=60)

        ctk.CTkButton(frame,
                      text="🚀 OPEN FULL STRATEGIC MAP",
                      font=ctk.CTkFont(size=24, weight="bold"),
                      height=100,
                      width=600,
                      fg_color="#00CC00",
                      hover_color="#00FF00",
                      command=self.open_strategic_map).pack(pady=60)

        print("✅ build_strategic_tab() FINISHED - content should now be visible!")
    def open_strategic_map(self):
        try:
            print("🌍 Launching Strategic Theater Map...")
            StrategicMap().run()
        except Exception as e:
            messagebox.showerror("Map Error", f"Could not launch map:\n{e}")
            
if __name__ == "__main__":
    print("✅ Sequence of Play engine loaded and ready for battle!")
    app = WargameApp()
    app.mainloop()