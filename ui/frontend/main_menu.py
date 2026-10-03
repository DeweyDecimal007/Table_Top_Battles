"""
ui/frontend/main_menu.py
Title screen / command center. Shows the title menu until a campaign is
started or loaded, then switches to the campaign command menu with
feature cards for the strategic map, industry and army builder.
"""

import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from ui.frontend import theme
from ui.frontend.dialogs import LoadGamePanel, NewGamePanel, SaveGamePanel, SettingsPanel, format_timestamp
from ui.frontend.theme import BORDER, GOLD, GOLD_BRIGHT, PANEL, TEXT, TEXT_DIM, TEXT_MUTED
from ui.frontend.widgets import FeatureCard, MenuButton, ResourceBar, primary_button, section_label

GAME_VERSION = "v0.3  \u2022  Early Access"

INTEL_TICKER = [
    "INTEL \u25B8  Right-click an island on the strategic map to open its tactical battlefield.",
    "INTEL \u25B8  Steel Mills and Factories fund every tank, gun and landing craft you build.",
    "INTEL \u25B8  Elite troops cost more to raise but add +2 to their combat rolls.",
    "INTEL \u25B8  The Industrial Hub at the center of the theater is the key to the war.",
    "INTEL \u25B8  Press F11 at any time to toggle fullscreen.",
    "INTEL \u25B8  Deploy a formation from the Army Builder straight into a tactical battle.",
]


class MainMenuScreen(ctk.CTkFrame):
    PANEL_WIDTH = 430

    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK, corner_radius=0)
        self.app = app
        self.active_modal = None
        self._bg_photo = None
        self._bg_job = None
        self._last_bg_size = None
        self._card_width = None
        self._ticker_index = 0

        self.bg_label = tk.Label(self, bg=theme.BG_DARK, bd=0, highlightthickness=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self._build_panel()
        self._build_ticker()

        self.campaign_area = None
        self.title_area = None
        self.cards_row = None

        self.bind("<Configure>", self._schedule_background, add="+")
        self.refresh()
        self._rotate_ticker()

    # ------------------------------------------------------------------ layout

    def _build_panel(self):
        self.panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, width=self.PANEL_WIDTH)
        self.panel.place(x=0, y=0, relheight=1)
        self.panel.pack_propagate(False)
        ctk.CTkFrame(self.panel, width=2, fg_color=GOLD, corner_radius=0).place(relx=1.0, x=-2, y=0, relheight=1)

        title = Image.new("RGBA", (820, 300), (0, 0, 0, 0))
        top = theme.glow_text("TABLE TOP", 64, color=theme.TEXT, glow="#3a4a5c", glow_radius=8, tracking=14)
        bottom = theme.glow_text("BATTLES", 150, glow_radius=14, tracking=10)
        title.alpha_composite(top, (12, 0))
        title.alpha_composite(bottom, (0, 70))
        title = title.crop(title.getbbox())
        w, h = title.size
        display_w = self.PANEL_WIDTH - 70
        self._title_image = ctk.CTkImage(light_image=title, dark_image=title,
                                         size=(display_w, int(h * display_w / w)))
        ctk.CTkLabel(self.panel, text="", image=self._title_image, fg_color=PANEL).pack(
            anchor="w", padx=(28, 0), pady=(46, 0))
        ctk.CTkLabel(self.panel, text="PACIFIC THEATER  \u2022  CAMPAIGN COMMAND",
                     font=theme.font(13, "bold"), text_color=TEXT_DIM, fg_color=PANEL).pack(
            anchor="w", padx=(40, 0), pady=(6, 0))

        self.menu_frame = ctk.CTkFrame(self.panel, fg_color=PANEL, corner_radius=0)
        self.menu_frame.pack(fill="x", pady=(30, 0), padx=(0, 2))

        ctk.CTkLabel(self.panel, text=GAME_VERSION, font=theme.font(12), text_color=TEXT_MUTED,
                     fg_color=PANEL).pack(side="bottom", anchor="w", padx=40, pady=22)

    def _build_ticker(self):
        self.ticker = ctk.CTkFrame(self, fg_color=theme.BG_DARK, corner_radius=0, height=40)
        self.ticker.place(x=self.PANEL_WIDTH, rely=1.0, anchor="sw", relwidth=1.0)
        ctk.CTkFrame(self.ticker, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x", side="top")
        self.ticker_label = ctk.CTkLabel(self.ticker, text="", font=theme.font(13),
                                         text_color=TEXT_DIM, fg_color=theme.BG_DARK, anchor="w")
        self.ticker_label.pack(side="left", padx=28)

    def _rotate_ticker(self):
        self.ticker_label.configure(text=INTEL_TICKER[self._ticker_index % len(INTEL_TICKER)])
        self._ticker_index += 1
        self.after(7000, self._rotate_ticker)

    # -------------------------------------------------------------- background

    def _schedule_background(self, _event=None):
        if self._bg_job:
            self.after_cancel(self._bg_job)
        self._bg_job = self.after(80, self._render_background)

    def _render_background(self):
        self._bg_job = None
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50 or h < 50:
            return
        panel_px = self.panel.winfo_width()
        if (w, h, panel_px) != self._last_bg_size:
            self._last_bg_size = (w, h, panel_px)
            art = theme.cover_crop(theme.load_art("menu_background.jpg"), w, h, focus_x=0.7).convert("RGBA")
            fade_w = min(420, max(1, w - panel_px))
            art.alpha_composite(theme.horizontal_fade((fade_w, h), PANEL, 235, 0), (panel_px, 0))
            art.alpha_composite(theme.vertical_fade((w, 140), theme.BG_DARK, 150, 0), (0, 0))
            bottom_h = int(h * 0.45)
            art.alpha_composite(theme.vertical_fade((w, bottom_h), theme.BG_DARK, 0, 235), (0, h - bottom_h))
            self._bg_photo = ImageTk.PhotoImage(art.convert("RGB"))
            self.bg_label.configure(image=self._bg_photo)
        self._layout_cards()

    # ------------------------------------------------------------------- state

    def refresh(self):
        """Rebuild the menu and right-hand area for the current campaign state."""
        self.close_modal()
        for child in self.menu_frame.winfo_children():
            child.destroy()
        for area in (self.campaign_area, self.title_area, self.cards_row):
            if area is not None:
                area.destroy()
        self.campaign_area = self.title_area = self.cards_row = None
        self._card_width = None

        if self.app.campaign:
            self._build_campaign_menu()
            self._build_campaign_area()
        else:
            self._build_title_menu()
            self._build_title_area()
        self.ticker.lift()
        self._schedule_background()

    def _add_button(self, text, command, subtitle=None, height=48, size=20, enabled=True):
        btn = MenuButton(self.menu_frame, text, lambda: self._menu_action(command),
                         subtitle=subtitle, height=height, size=size)
        btn.pack(fill="x")
        btn.set_enabled(enabled)
        return btn

    def _menu_action(self, command):
        self.close_modal()
        command()

    def _build_title_menu(self):
        latest = self.app.saves.latest()
        subtitle = f"{latest['slot_name'][:22]}  \u2022  T{latest['turn']}" if latest else None
        self._add_button("Continue", self._continue_latest, subtitle=subtitle, enabled=latest is not None)
        self._add_button("New Campaign", self.open_new_game)
        self._add_button("Load Campaign", self.open_load_game, enabled=latest is not None)
        self._add_button("Settings", self.open_settings)
        self._add_button("Quit to Desktop", self.app.quit_game)

    def _build_campaign_menu(self):
        section_label(self.menu_frame, "Command", indent=40).pack(fill="x", pady=(0, 6))
        self._add_button("Strategic Map", self.app.open_strategic_map, height=44, size=18)
        self._add_button("Resources & Industry", lambda: self.app.show_screen("industry"), height=44, size=18)
        self._add_button("Army Builder", lambda: self.app.show_screen("army"), height=44, size=18)
        self._add_button("Tactical Battle", lambda: self.app.show_screen("battle"), height=44, size=18)
        section_label(self.menu_frame, "Campaign", indent=40).pack(fill="x", pady=(16, 6))
        self._add_button("Save Campaign", self.open_save_game, height=40, size=16)
        self._add_button("Load Campaign", self.open_load_game, height=40, size=16)
        self._add_button("New Campaign", self.open_new_game, height=40, size=16)
        self._add_button("Settings", self.open_settings, height=40, size=16)
        self._add_button("Exit to Title", self.app.exit_to_title, height=40, size=16)
        self._add_button("Quit to Desktop", self.app.quit_game, height=40, size=16)

    def _build_title_area(self):
        latest = self.app.saves.latest()
        area = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=4, border_width=1, border_color=BORDER)
        area.place(relx=1.0, rely=1.0, x=-48, y=-72, anchor="se")
        self.title_area = area

        ctk.CTkLabel(area, text="WAR BULLETIN", font=theme.font(13, "bold"), text_color=GOLD,
                     fg_color=PANEL).pack(anchor="w", padx=24, pady=(18, 4))
        ctk.CTkLabel(area, text="The Pacific is ablaze. Command awaits your orders.",
                     font=theme.font(20, "bold"), text_color=TEXT, fg_color=PANEL).pack(anchor="w", padx=24)
        if latest:
            info = (f"Last campaign: {latest['name']}  \u2022  {latest['mode']}  \u2022  Turn {latest['turn']}"
                    f"\nSaved {format_timestamp(latest['last_saved'])}")
        else:
            info = "Begin a New Campaign to build your industry, raise your armies\nand seize the islands."
        ctk.CTkLabel(area, text=info, font=theme.font(14), text_color=TEXT_DIM, fg_color=PANEL,
                     justify="left").pack(anchor="w", padx=24, pady=(6, 0))
        row = ctk.CTkFrame(area, fg_color=PANEL, corner_radius=0)
        row.pack(anchor="w", padx=24, pady=(16, 20))
        if latest:
            primary_button(row, "Continue", self._continue_latest, width=170).pack(side="left", padx=(0, 12))
        primary_button(row, "New Campaign", self.open_new_game, width=200).pack(side="left")

    def _build_campaign_area(self):
        campaign = self.app.campaign
        banner = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=4, border_width=1, border_color=BORDER)
        banner.place(relx=1.0, x=-48, y=40, anchor="ne")
        self.campaign_area = banner
        top = ctk.CTkFrame(banner, fg_color=PANEL, corner_radius=0)
        top.pack(fill="x", padx=22, pady=(16, 0))
        ctk.CTkFrame(top, width=6, height=46, fg_color=theme.side_color(campaign.player_side),
                     corner_radius=0).pack(side="left", padx=(0, 14))
        name_col = ctk.CTkFrame(top, fg_color=PANEL, corner_radius=0)
        name_col.pack(side="left")
        ctk.CTkLabel(name_col, text=campaign.name.upper(), font=theme.font(24, "bold"),
                     text_color=TEXT, fg_color=PANEL, anchor="w", height=28).pack(anchor="w")
        details = (f"{campaign.mode}  \u2022  {campaign.difficulty}  \u2022  "
                   f"{campaign.player_side} Force \u2013 {campaign.player_nation}")
        ctk.CTkLabel(name_col, text=details, font=theme.font(13), text_color=TEXT_DIM,
                     fg_color=PANEL, anchor="w", height=18).pack(anchor="w")

        turn_text = f"TURN {campaign.turn}"
        if campaign.turn_limit:
            turn_text += f" / {campaign.turn_limit}"
        turn_col = ctk.CTkFrame(top, fg_color=PANEL, corner_radius=0)
        turn_col.pack(side="right", padx=(40, 0))
        ctk.CTkLabel(turn_col, text=turn_text, font=theme.font(26, "bold"), text_color=GOLD_BRIGHT,
                     fg_color=PANEL, height=30).pack(anchor="e")
        saved = "Unsaved changes" if campaign.dirty else "All changes saved"
        ctk.CTkLabel(turn_col, text=saved, font=theme.font(12), fg_color=PANEL, height=16,
                     text_color=theme.DANGER if campaign.dirty else TEXT_MUTED).pack(anchor="e")

        ctk.CTkFrame(banner, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x", padx=22, pady=14)
        bottom = ctk.CTkFrame(banner, fg_color=PANEL, corner_radius=0)
        bottom.pack(fill="x", padx=22, pady=(0, 16))
        resources = ResourceBar(bottom, compact=True)
        resources.pack(side="left")
        resources.update_values(campaign.resources, campaign.production())
        primary_button(bottom, "End Turn  \u25B8", self.app.end_turn, width=150, height=42).pack(
            side="right", padx=(24, 0))

        self.cards_row = ctk.CTkFrame(self, fg_color=theme.BG_DARK, corner_radius=0)
        self.cards_row.place(relx=1.0, rely=1.0, x=-48, y=-72, anchor="se")

    def _layout_cards(self):
        if not self.app.campaign or self.cards_row is None:
            return
        scale = self._get_widget_scaling()
        avail = self.winfo_width() / scale - self.PANEL_WIDTH - 96
        avail_h = self.winfo_height() / scale
        width = int(max(220, min(360, (avail - 40) / 3)))
        img_h = int(width * (0.56 if avail_h > 820 else 0.42))
        if self._card_width == (width, img_h):
            return
        self._card_width = (width, img_h)
        for child in self.cards_row.winfo_children():
            child.destroy()
        cards = [
            ("card_strategic.jpg", "Strategic Map",
             "Command the theater. Move fleets and launch invasions across the island chain.",
             self.app.open_strategic_map),
            ("card_industry.jpg", "Resources & Industry",
             "Expand steel mills, refineries and shipyards to fuel the war machine.",
             lambda: self.app.show_screen("industry")),
            ("card_army.jpg", "Army Builder",
             "Raise formations of infantry, armor and artillery and assign their veterancy.",
             lambda: self.app.show_screen("army")),
        ]
        for i, (art, title, desc, command) in enumerate(cards):
            card = FeatureCard(self.cards_row, art, title, desc,
                               lambda c=command: self._menu_action(c), width=width, img_height=img_h)
            card.pack(side="left", padx=(0 if i == 0 else 20, 0))

    # ------------------------------------------------------------------ modals

    def open_modal(self, panel_cls):
        self.close_modal()
        self.active_modal = panel_cls(self, self.app, on_close=self._modal_closed)
        self.active_modal.show()

    def _modal_closed(self):
        self.active_modal = None

    def close_modal(self):
        if self.active_modal is not None and self.active_modal.winfo_exists():
            modal, self.active_modal = self.active_modal, None
            modal.place_forget()
            modal.destroy()
        self.active_modal = None

    def open_new_game(self):
        if self.app.confirm_discard_changes():
            self.open_modal(NewGamePanel)

    def open_load_game(self):
        self.open_modal(LoadGamePanel)

    def open_save_game(self):
        if self.app.campaign:
            self.open_modal(SaveGamePanel)

    def open_settings(self):
        self.open_modal(SettingsPanel)

    def _continue_latest(self):
        latest = self.app.saves.latest()
        if latest:
            self.app.load_campaign(latest["path"])
