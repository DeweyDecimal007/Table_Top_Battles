"""
ui/phases/cc_phase.py
"""

import customtkinter as ctk
from tkinter import messagebox


class CommandControlPhase:
    def __init__(self, app):
        self.app = app

    def build(self, parent):
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.pack(padx=30, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(self.frame, text="PHASE 5: COMMAND & CONTROL", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=40)

        ctk.CTkLabel(self.frame, text="Command & Control Phase\n\n"
                     "• Morale checks\n"
                     "• Rally attempts\n"
                     "• Unit status overview\n"
                     "• Issue special orders", 
                     font=ctk.CTkFont(size=16), justify="center").pack(pady=30)

        ctk.CTkButton(self.frame, text="Advance to Recovery Phase →", 
                      command=lambda: self.app.tabview.set("6. Recovery"),
                      height=50, fg_color="darkgreen", 
                      font=ctk.CTkFont(size=16, weight="bold")).pack(pady=40)