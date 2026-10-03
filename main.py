"""
main.py - Interactive Wargame Rules Assistant
"""

import customtkinter as ctk
import os
import re
import subprocess
import sys
from tkinter import messagebox

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
from game_engine.campaign_state import SaveManager

# Front End
from ui.frontend import theme
from ui.frontend.main_menu import MainMenuScreen
from ui.frontend.industry_screen import IndustryScreen
from ui.frontend.army_builder_screen import ArmyBuilderScreen

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DEFAULT_SETTINGS = {"fullscreen": False, "autosave": True, "ui_scale": "100%"}


class BattleScreen(ctk.CTkFrame):
    """Hosts the original tabbed sequence-of-play UI."""

    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK, corner_radius=0)
        self.app = app

        bar = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=0, height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkLabel(bar, text="TACTICAL BATTLE", font=theme.font(24, "bold"),
                     text_color=theme.GOLD_BRIGHT, fg_color=theme.PANEL).pack(side="left", padx=32)
        self.forces_label = ctk.CTkLabel(bar, text="", font=theme.font(14), text_color=theme.TEXT_DIM,
                                         fg_color=theme.PANEL)
        self.forces_label.pack(side="left", padx=12)
        ctk.CTkButton(
            bar, text="\u25C2  COMMAND CENTER", command=lambda: app.show_screen("menu"), width=190, height=36,
            font=theme.font(14, "bold"), fg_color=theme.PANEL, hover_color=theme.PANEL_HOVER,
            text_color=theme.TEXT, border_color=theme.GOLD, border_width=1, corner_radius=2,
        ).pack(side="right", padx=24)
        ctk.CTkFrame(self, height=2, fg_color=theme.GOLD, corner_radius=0).pack(fill="x")

        app.tabview = ctk.CTkTabview(self, width=1000, height=620)
        app.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        app.create_battle_tabs()

    def on_show(self):
        blue, red = len(self.app.blue_units), len(self.app.red_units)
        self.forces_label.configure(
            text=f"Turn {self.app.game.turn_number}   |   Blue: {blue} units   \u2022   Red: {red} units")


class WargameApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Table Top Battles - Pacific Theater")
        self.geometry("1600x900")
        self.minsize(1280, 760)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.configure(fg_color=theme.BG_DARK)

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
        self.strategic_process = None
        self.tabview = None

        self.saves = SaveManager(os.path.join(PROJECT_ROOT, "saves"))
        self.settings = {**DEFAULT_SETTINGS, **self.saves.load_settings()}
        self.campaign = None

        self.screens = {}
        self.screen_factories = {
            "menu": MainMenuScreen,
            "industry": IndustryScreen,
            "army": ArmyBuilderScreen,
            "battle": BattleScreen,
        }
        self.current_screen = None
        self._toast = None
        self._toast_job = None

        self.apply_settings(self.settings, persist=False)
        self.show_screen("menu")

        self.bind("<F11>", lambda _e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda _e: self._on_escape())
        self.protocol("WM_DELETE_WINDOW", self.quit_game)
        self._fade_in()

    # ------------------------------------------------------------ screens

    def show_screen(self, name):
        if name in ("industry", "army", "battle") and not self.campaign:
            name = "menu"
        if name not in self.screens:
            self.screens[name] = self.screen_factories[name](self, self)
        if self.current_screen and self.current_screen != name:
            self.screens[self.current_screen].place_forget()
        screen = self.screens[name]
        screen.place(x=0, y=0, relwidth=1, relheight=1)
        screen.lift()
        self.current_screen = name
        if name == "menu":
            screen.refresh()
        elif hasattr(screen, "on_show"):
            screen.on_show()
        if self._toast is not None:
            self._toast.lift()

    def _on_escape(self):
        if self.current_screen == "menu":
            self.screens["menu"].close_modal()
        else:
            self.show_screen("menu")

    def create_battle_tabs(self):
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

        self.build_strategic_tab()

    def build_strategic_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_strategic)
        frame.pack(padx=40, pady=40, fill="both", expand=True)

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

    def open_strategic_map(self):
        if self.strategic_process is not None and self.strategic_process.poll() is None:
            self.toast("The strategic map is already open.")
            return
        try:
            print("🌍 Launching Strategic Theater Map...")
            self.strategic_process = subprocess.Popen(
                [sys.executable, "-m", "strategic.strategic_map"], cwd=PROJECT_ROOT)
            self.toast("Strategic map launching in a new window...")
        except Exception as e:
            messagebox.showerror("Map Error", f"Could not launch map:\n{e}")

    def get_troop_modifier(self, troop_class):
        match = re.search(r"\(([+-]?\d+)\)", str(troop_class))
        return int(match.group(1)) if match else 0

    # ----------------------------------------------------------- campaign

    def start_campaign(self, state):
        self.campaign = state
        self.blue_units.clear()
        self.red_units.clear()
        self.blue_country = state.blue_nation
        self.red_country = state.red_nation
        self.show_screen("menu")
        self.toast(f"{state.name} has begun. Good luck, Commander.")

    def load_campaign(self, path):
        try:
            state = self.saves.load(path)
        except Exception as e:
            messagebox.showerror("Load Failed", f"Could not load save:\n{e}")
            return
        self.campaign = state
        self.blue_country = state.blue_nation
        self.red_country = state.red_nation
        self.show_screen("menu")
        self.toast(f"Loaded {state.save_slot}  \u2022  Turn {state.turn}")

    def save_campaign(self, slot_name):
        try:
            self.saves.save(self.campaign, slot_name)
        except OSError as e:
            messagebox.showerror("Save Failed", f"Could not save campaign:\n{e}")
            return False
        self.toast(f"Campaign saved: {slot_name}")
        if self.current_screen == "menu":
            self.screens["menu"].refresh()
        return True

    def end_turn(self):
        campaign = self.campaign
        if not campaign:
            return
        produced = campaign.end_turn()
        summary = "  ".join(f"+{v} {k}" for k, v in produced.items() if v)
        if self.settings.get("autosave", True):
            manual_slot = campaign.save_slot
            try:
                self.saves.save(campaign, f"Autosave - {campaign.name}")
            except OSError:
                pass
            campaign.save_slot = manual_slot
        self.toast(f"Turn {campaign.turn} begins.   {summary}")
        if campaign.turn_limit and campaign.turn > campaign.turn_limit:
            messagebox.showinfo("Campaign Complete",
                                f"{campaign.name} has reached its turn limit of {campaign.turn_limit}.")
        if self.current_screen == "menu":
            self.screens["menu"].refresh()

    def confirm_discard_changes(self):
        """Offer to save unsaved progress. Returns False if the user cancels."""
        if not self.campaign or not self.campaign.dirty:
            return True
        answer = messagebox.askyesnocancel(
            "Unsaved Changes", f"Save '{self.campaign.name}' before continuing?")
        if answer is None:
            return False
        if answer:
            return self.save_campaign(self.campaign.save_slot or self.campaign.name)
        return True

    def exit_to_title(self):
        if not self.confirm_discard_changes():
            return
        self.campaign = None
        self.show_screen("menu")

    def quit_game(self):
        if not self.confirm_discard_changes():
            return
        if self.strategic_process is not None and self.strategic_process.poll() is None:
            self.strategic_process.terminate()
        self.destroy()

    # ----------------------------------------------------------- settings

    def apply_settings(self, settings, persist=True):
        self.settings.update(settings)
        try:
            scale = int(str(self.settings.get("ui_scale", "100%")).rstrip("%")) / 100
        except ValueError:
            scale = 1.0
        ctk.set_widget_scaling(scale)
        self.attributes("-fullscreen", bool(self.settings.get("fullscreen")))
        if persist:
            self.saves.save_settings(self.settings)

    def toggle_fullscreen(self):
        self.apply_settings({"fullscreen": not self.settings.get("fullscreen")})

    # ----------------------------------------------------------- effects

    def toast(self, message, duration=3200):
        if self._toast is None:
            self._toast = ctk.CTkLabel(self, text="", font=theme.font(15, "bold"), text_color=theme.TEXT,
                                       fg_color=theme.PANEL_LIGHT, corner_radius=4, height=44)
        self._toast.configure(text=f"   {message}   ")
        self._toast.place(relx=0.5, rely=1.0, y=-64, anchor="s")
        self._toast.lift()
        if self._toast_job:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(duration, self._toast.place_forget)

    def _fade_in(self, alpha=0.0):
        try:
            self.attributes("-alpha", alpha)
        except Exception:
            return
        if alpha < 1.0:
            self.after(16, lambda: self._fade_in(min(1.0, alpha + 0.06)))


if __name__ == "__main__":
    print("✅ Sequence of Play engine loaded and ready for battle!")
    app = WargameApp()
    app.mainloop()
