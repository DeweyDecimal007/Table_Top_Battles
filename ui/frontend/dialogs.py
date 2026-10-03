"""
ui/frontend/dialogs.py
Overlay panels for the main menu: new campaign, load, save and settings.
"""

import random
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from game_engine.campaign_state import CampaignState, DIFFICULTIES, GAME_MODES
from ui.frontend import theme
from ui.frontend.theme import BORDER, GOLD, PANEL, PANEL_HOVER, PANEL_LIGHT, TEXT, TEXT_DIM, TEXT_MUTED
from ui.frontend.widgets import (
    ModalPanel, danger_button, primary_button, secondary_button, styled_entry, styled_option_menu,
)

CODENAMES = [
    "Iron Tide", "Coral Hammer", "Blue Horizon", "Storm Petrel", "Jade Anchor", "Crimson Reef",
    "Silent Trident", "Pacific Fury", "Black Lagoon", "Steel Monsoon", "Typhoon Gate", "Atoll Strike",
]


def field_label(master, text):
    return ctk.CTkLabel(master, text=text.upper(), font=theme.font(12, "bold"),
                        text_color=TEXT_MUTED, fg_color=PANEL, anchor="w")


def segmented(master, values, variable, command=None):
    return ctk.CTkSegmentedButton(
        master, values=values, variable=variable, command=command, height=38,
        font=theme.font(14, "bold"), fg_color=PANEL_LIGHT, selected_color="#8f6f2e",
        selected_hover_color="#a8843a", unselected_color=PANEL_LIGHT,
        unselected_hover_color=PANEL_HOVER, text_color=TEXT, corner_radius=2,
    )


def format_timestamp(iso_text):
    try:
        return datetime.fromisoformat(iso_text).strftime("%b %d, %Y  %H:%M")
    except (TypeError, ValueError):
        return "Unknown date"


class NewGamePanel(ModalPanel):
    def __init__(self, master, app, on_close=None):
        super().__init__(master, "New Campaign", width=720, height=640, on_close=on_close)
        self.app = app
        nations = app.data.get_countries() or ["Blue Nation", "Red Nation"]

        body = self.body
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        field_label(body, "Operation name").grid(row=0, column=0, columnspan=2, sticky="w")
        self.name_entry = styled_entry(body, width=640)
        self.name_entry.insert(0, f"Operation {random.choice(CODENAMES)}")
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky="we", pady=(4, 16))

        field_label(body, "Game mode").grid(row=2, column=0, columnspan=2, sticky="w")
        self.mode_var = ctk.StringVar(value="Grand Campaign")
        segmented(body, list(GAME_MODES), self.mode_var, self._update_mode).grid(
            row=3, column=0, columnspan=2, sticky="we", pady=(4, 6))
        self.mode_desc = ctk.CTkLabel(body, text="", font=theme.font(13), text_color=TEXT_DIM,
                                      fg_color=PANEL, anchor="w", justify="left", wraplength=640)
        self.mode_desc.grid(row=4, column=0, columnspan=2, sticky="we", pady=(0, 16))

        field_label(body, "Command side").grid(row=5, column=0, sticky="w")
        field_label(body, "Difficulty").grid(row=5, column=1, sticky="w", padx=(16, 0))
        self.side_var = ctk.StringVar(value="Blue")
        segmented(body, ["Blue", "Red"], self.side_var).grid(row=6, column=0, sticky="we", pady=(4, 16))
        self.diff_var = ctk.StringVar(value="Veteran")
        segmented(body, list(DIFFICULTIES), self.diff_var).grid(
            row=6, column=1, sticky="we", padx=(16, 0), pady=(4, 16))

        field_label(body, "Blue nation").grid(row=7, column=0, sticky="w")
        field_label(body, "Red nation").grid(row=7, column=1, sticky="w", padx=(16, 0))
        self.blue_var = ctk.StringVar(value=nations[0])
        self.red_var = ctk.StringVar(value=nations[1] if len(nations) > 1 else nations[0])
        styled_option_menu(body, nations, self.blue_var, width=300).grid(row=8, column=0, sticky="we", pady=(4, 0))
        styled_option_menu(body, nations, self.red_var, width=300).grid(
            row=8, column=1, sticky="we", padx=(16, 0), pady=(4, 0))

        primary_button(self.footer, "Begin Campaign", self._begin, width=220).pack(side="right")
        secondary_button(self.footer, "Cancel", self.close).pack(side="right", padx=12)

        self._update_mode()

    def _update_mode(self, _value=None):
        self.mode_desc.configure(text=GAME_MODES[self.mode_var.get()]["description"])

    def _begin(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Operation Name", "Give your campaign a name.")
            return
        state = CampaignState.new(
            name=name,
            mode=self.mode_var.get(),
            player_side=self.side_var.get(),
            blue_nation=self.blue_var.get(),
            red_nation=self.red_var.get(),
            difficulty=self.diff_var.get(),
        )
        self.close()
        self.app.start_campaign(state)


class SaveListMixin:
    """Scrollable list of save slots with single selection."""

    def build_save_list(self, parent, on_select, on_double=None):
        self.selected_save = None
        self._rows = []
        self._on_select = on_select
        self._on_double = on_double
        self.list_frame = ctk.CTkScrollableFrame(parent, fg_color=theme.BG_DARK, corner_radius=2,
                                                 border_width=1, border_color=BORDER,
                                                 scrollbar_button_color=BORDER)
        self.list_frame.pack(fill="both", expand=True)
        self.populate()

    def populate(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        self._rows = []
        self.selected_save = None
        saves = self.app.saves.list_saves()
        if not saves:
            ctk.CTkLabel(self.list_frame, text="No saved campaigns yet.", font=theme.font(15),
                         text_color=TEXT_MUTED).pack(pady=40)
            return
        for save in saves:
            self._add_row(save)

    def _add_row(self, save):
        row = ctk.CTkFrame(self.list_frame, fg_color=PANEL, corner_radius=2, border_width=1,
                           border_color=PANEL, height=68)
        row.pack(fill="x", padx=6, pady=4)
        row.pack_propagate(False)

        stripe = ctk.CTkFrame(row, width=4, fg_color=theme.side_color(save["side"]), corner_radius=0)
        stripe.pack(side="left", fill="y", padx=(1, 12), pady=1)

        text_col = ctk.CTkFrame(row, fg_color=PANEL, corner_radius=0)
        text_col.pack(side="left", fill="both", expand=True, pady=8)
        title = ctk.CTkLabel(text_col, text=save["slot_name"], font=theme.font(16, "bold"),
                             text_color=TEXT, fg_color=PANEL, anchor="w", height=22)
        title.pack(fill="x")
        details = f"{save['name']}  \u2022  {save['mode']}  \u2022  {save['side']} \u2013 {save['nation']}"
        sub = ctk.CTkLabel(text_col, text=details, font=theme.font(12), text_color=TEXT_DIM,
                           fg_color=PANEL, anchor="w", height=18)
        sub.pack(fill="x")

        right = ctk.CTkFrame(row, fg_color=PANEL, corner_radius=0)
        right.pack(side="right", padx=14, pady=8)
        turn = ctk.CTkLabel(right, text=f"TURN {save['turn']}", font=theme.font(15, "bold"),
                            text_color=GOLD, fg_color=PANEL, anchor="e", height=22)
        turn.pack(anchor="e")
        date = ctk.CTkLabel(right, text=format_timestamp(save["last_saved"]), font=theme.font(12),
                            text_color=TEXT_MUTED, fg_color=PANEL, anchor="e", height=18)
        date.pack(anchor="e")

        widgets = [row, text_col, title, sub, right, turn, date]
        entry = {"save": save, "row": row, "widgets": widgets}
        self._rows.append(entry)
        for w in widgets:
            w.bind("<Button-1>", lambda _e, en=entry: self._select(en), add="+")
            if self._on_double:
                w.bind("<Double-Button-1>", lambda _e, en=entry: self._double(en), add="+")

    def _select(self, entry):
        for other in self._rows:
            other["row"].configure(border_color=PANEL)
            for w in other["widgets"]:
                w.configure(fg_color=PANEL)
        entry["row"].configure(border_color=GOLD)
        for w in entry["widgets"]:
            w.configure(fg_color=PANEL_HOVER)
        self.selected_save = entry["save"]
        self._on_select(entry["save"])

    def _double(self, entry):
        self._select(entry)
        self._on_double(entry["save"])


class LoadGamePanel(SaveListMixin, ModalPanel):
    def __init__(self, master, app, on_close=None):
        ModalPanel.__init__(self, master, "Load Campaign", width=780, height=620, on_close=on_close)
        self.app = app
        self.build_save_list(self.body, on_select=lambda _s: None, on_double=lambda _s: self._load())

        primary_button(self.footer, "Load", self._load, width=180).pack(side="right")
        secondary_button(self.footer, "Cancel", self.close).pack(side="right", padx=12)
        danger_button(self.footer, "Delete", self._delete).pack(side="left")

    def _load(self):
        if not self.selected_save:
            messagebox.showinfo("Load Campaign", "Select a saved campaign first.")
            return
        path = self.selected_save["path"]
        if not self.app.confirm_discard_changes():
            return
        self.close()
        self.app.load_campaign(path)

    def _delete(self):
        if not self.selected_save:
            return
        if messagebox.askyesno("Delete Save", f"Permanently delete '{self.selected_save['slot_name']}'?"):
            self.app.saves.delete(self.selected_save["path"])
            self.populate()


class SaveGamePanel(SaveListMixin, ModalPanel):
    def __init__(self, master, app, on_close=None):
        ModalPanel.__init__(self, master, "Save Campaign", width=780, height=640, on_close=on_close)
        self.app = app
        campaign = app.campaign

        field_label(self.body, "Save name").pack(anchor="w")
        self.slot_entry = styled_entry(self.body, width=700)
        self.slot_entry.insert(0, campaign.save_slot or f"{campaign.name} - Turn {campaign.turn}")
        self.slot_entry.pack(fill="x", pady=(4, 14))
        field_label(self.body, "Existing saves (click to overwrite)").pack(anchor="w", pady=(0, 4))
        self.build_save_list(self.body, on_select=self._fill_name, on_double=lambda _s: self._save())

        primary_button(self.footer, "Save", self._save, width=180).pack(side="right")
        secondary_button(self.footer, "Cancel", self.close).pack(side="right", padx=12)

    def _fill_name(self, save):
        self.slot_entry.delete(0, "end")
        self.slot_entry.insert(0, save["slot_name"])

    def _save(self):
        slot = self.slot_entry.get().strip()
        if not slot:
            messagebox.showwarning("Save Campaign", "Enter a name for this save.")
            return
        if self.app.saves.exists(slot) and slot != self.app.campaign.save_slot:
            if not messagebox.askyesno("Overwrite Save", f"'{slot}' already exists. Overwrite it?"):
                return
        app = self.app
        self.close()
        app.save_campaign(slot)


class SettingsPanel(ModalPanel):
    SCALES = ["90%", "100%", "110%", "125%", "150%"]

    def __init__(self, master, app, on_close=None):
        super().__init__(master, "Settings", width=600, height=480, on_close=on_close)
        self.app = app
        settings = app.settings

        self.fullscreen_var = ctk.BooleanVar(value=settings.get("fullscreen", False))
        self.autosave_var = ctk.BooleanVar(value=settings.get("autosave", True))
        self.scale_var = ctk.StringVar(value=settings.get("ui_scale", "100%"))

        self._row("Fullscreen", "Toggle anytime with F11",
                  self._switch(self.fullscreen_var))
        self._row("Autosave", "Save automatically at the end of each strategic turn",
                  self._switch(self.autosave_var))
        self._row("Interface scale", "Size of menus, text and buttons",
                  styled_option_menu(self.body, self.SCALES, self.scale_var, width=140))

        primary_button(self.footer, "Apply", self._apply, width=160).pack(side="right")
        secondary_button(self.footer, "Cancel", self.close).pack(side="right", padx=12)

    def _switch(self, variable):
        return ctk.CTkSwitch(self.body, text="", variable=variable, progress_color=GOLD,
                             button_color=TEXT, button_hover_color=theme.GOLD_BRIGHT,
                             fg_color=BORDER, width=60)

    def _row(self, title, subtitle, control):
        row = ctk.CTkFrame(self.body, fg_color=PANEL, corner_radius=0)
        row.pack(fill="x", pady=10)
        text_col = ctk.CTkFrame(row, fg_color=PANEL, corner_radius=0)
        text_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_col, text=title, font=theme.font(17, "bold"), text_color=TEXT,
                     fg_color=PANEL, anchor="w").pack(fill="x")
        ctk.CTkLabel(text_col, text=subtitle, font=theme.font(13), text_color=TEXT_DIM,
                     fg_color=PANEL, anchor="w").pack(fill="x")
        control.lift(row)
        control.pack(in_=row, side="right")

    def _apply(self):
        self.app.apply_settings({
            "fullscreen": self.fullscreen_var.get(),
            "autosave": self.autosave_var.get(),
            "ui_scale": self.scale_var.get(),
        })
        self.close()
