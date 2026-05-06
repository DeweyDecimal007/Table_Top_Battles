"""
ui/phases/recovery_phase.py
"""

import customtkinter as ctk
from tkinter import messagebox


class RecoveryPhase:
    def __init__(self, app):
        self.app = app

    def build(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(self.frame, text="PHASE 6: RECOVERY PHASE", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=40)

        ctk.CTkLabel(self.frame, text="End of Turn Actions\n\n"
                     "• Rally routed units\n"
                     "• Repair attempts\n"
                     "• Morale recovery\n"
                     "• Remove smoke / wrecks", 
                     font=ctk.CTkFont(size=16), justify="center").pack(pady=30)

        ctk.CTkButton(self.frame, text="🏁 End Turn & Start Next Turn", 
                      command=self.end_turn,
                      fg_color="darkgreen", height=60, 
                      font=ctk.CTkFont(size=18, weight="bold")).pack(pady=40)

    def end_turn(self):
        # Reset Command Phase for next turn
        if hasattr(self.app, 'command_phase'):
            self.app.command_phase.roll_used_this_turn = False
            self.app.command_phase.orders_saved = False

        # Reset Fire Phase index
        self.app.current_fire_index = 0

        # Increment turn
        self.app.game.turn_number += 1

        messagebox.showinfo("Turn Complete", 
            f"Turn {self.app.game.turn_number - 1} finished!\n\n"
            f"Turn {self.app.game.turn_number} started.\n\n"
            "Go to Command Phase to roll new activation order.")

        # Return to Command Phase
        self.app.tabview.set("1. Command Phase")