"""
ui/frontend/industry_screen.py
Resources & Industry: stockpiles, per-turn production and industry upgrades.
"""

import customtkinter as ctk

from game_engine.campaign_state import INDUSTRY, RESOURCES, upgrade_cost
from ui.frontend import theme
from ui.frontend.theme import BORDER, GOLD, GOLD_BRIGHT, PANEL, PANEL_LIGHT, TEXT, TEXT_DIM, TEXT_MUTED
from ui.frontend.widgets import ResourceBar, ScreenHeader, primary_button, section_label

MAX_LEVEL = 10


class IndustryScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK, corner_radius=0)
        self.app = app

        ScreenHeader(self, "card_industry.jpg", "Resources & Industry",
                     "Fuel the war machine", lambda: app.show_screen("menu"), focus_y=0.55).pack(fill="x")

        top = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=84)
        top.pack(fill="x")
        top.pack_propagate(False)
        self.resource_bar = ResourceBar(top)
        self.resource_bar.pack(side="left", padx=36, pady=18)
        primary_button(top, "End Turn  \u25B8", self._end_turn, width=170, height=44).pack(side="right", padx=36)
        self.turn_label = ctk.CTkLabel(top, text="", font=theme.font(22, "bold"), text_color=GOLD_BRIGHT,
                                       fg_color=PANEL)
        self.turn_label.pack(side="right", padx=12)
        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color=theme.BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True, padx=36, pady=24)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=1, minsize=320)
        body.grid_rowconfigure(0, weight=1)

        self.sectors = ctk.CTkScrollableFrame(body, fg_color=theme.BG_DARK, corner_radius=0,
                                              scrollbar_button_color=BORDER)
        self.sectors.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        self.sectors.grid_columnconfigure((0, 1), weight=1, uniform="sector")

        side = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=4, border_width=1, border_color=BORDER)
        side.grid(row=0, column=1, sticky="nsew")
        section_label(side, "Per-turn output").pack(fill="x", pady=(18, 8))
        self.output_frame = ctk.CTkFrame(side, fg_color=PANEL, corner_radius=0)
        self.output_frame.pack(fill="x", padx=18)
        section_label(side, "Campaign log").pack(fill="x", pady=(22, 8))
        self.log_box = ctk.CTkTextbox(side, fg_color=PANEL, text_color=TEXT_DIM, font=theme.font(13),
                                      wrap="word", border_width=0, activate_scrollbars=True)
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 14))

    def on_show(self):
        self.refresh()

    def refresh(self):
        campaign = self.app.campaign
        if not campaign:
            return
        production = campaign.production()
        self.resource_bar.update_values(campaign.resources, production)
        self.turn_label.configure(text=f"TURN {campaign.turn}")

        for child in self.sectors.winfo_children():
            child.destroy()
        for i, key in enumerate(INDUSTRY):
            self._sector_card(key, campaign).grid(row=i // 2, column=i % 2, sticky="nsew", padx=8, pady=8)

        for child in self.output_frame.winfo_children():
            child.destroy()
        for res, meta in RESOURCES.items():
            row = ctk.CTkFrame(self.output_frame, fg_color=PANEL, corner_radius=0)
            row.pack(fill="x", pady=3)
            ctk.CTkFrame(row, width=4, height=22, fg_color=meta["color"], corner_radius=0).pack(side="left")
            ctk.CTkLabel(row, text=meta["label"], font=theme.font(14), text_color=TEXT,
                         fg_color=PANEL).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"+{production.get(res, 0)}", font=theme.font(15, "bold"),
                         text_color=meta["color"], fg_color=PANEL).pack(side="right")

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("1.0", "\n".join(campaign.log) or "No events yet.")
        self.log_box.configure(state="disabled")

    def _sector_card(self, key, campaign):
        info = INDUSTRY[key]
        level = campaign.industry.get(key, 0)
        cost = upgrade_cost(key, level)
        affordable = campaign.can_afford(cost) and level < MAX_LEVEL

        card = ctk.CTkFrame(self.sectors, fg_color=PANEL, corner_radius=4, border_width=1, border_color=BORDER)

        head = ctk.CTkFrame(card, fg_color=PANEL, corner_radius=0)
        head.pack(fill="x", padx=20, pady=(18, 0))
        ctk.CTkLabel(head, text=info["name"].upper(), font=theme.font(19, "bold"), text_color=TEXT,
                     fg_color=PANEL).pack(side="left")
        ctk.CTkLabel(head, text=f"LVL {level}", font=theme.font(15, "bold"), text_color=GOLD,
                     fg_color=PANEL).pack(side="right")

        pips = ctk.CTkFrame(card, fg_color=PANEL, corner_radius=0)
        pips.pack(fill="x", padx=20, pady=(8, 0))
        for i in range(MAX_LEVEL):
            ctk.CTkFrame(pips, width=22, height=6, corner_radius=0,
                         fg_color=GOLD if i < level else PANEL_LIGHT).pack(side="left", padx=(0, 4))

        ctk.CTkLabel(card, text=info["description"], font=theme.font(13), text_color=TEXT_DIM,
                     fg_color=PANEL, anchor="w", justify="left", wraplength=380).pack(fill="x", padx=20, pady=(10, 0))

        output = "   ".join(f"+{amt * level} {res}" for res, amt in info["produces"].items())
        per_level = ", ".join(f"+{amt} {res}" for res, amt in info["produces"].items())
        ctk.CTkLabel(card, text=f"OUTPUT  {output}   ({per_level} per level)", font=theme.font(13, "bold"),
                     text_color=theme.SUCCESS, fg_color=PANEL, anchor="w").pack(fill="x", padx=20, pady=(8, 0))

        foot = ctk.CTkFrame(card, fg_color=PANEL, corner_radius=0)
        foot.pack(fill="x", padx=20, pady=(14, 18))
        if level >= MAX_LEVEL:
            ctk.CTkLabel(foot, text="FULLY EXPANDED", font=theme.font(13, "bold"), text_color=TEXT_MUTED,
                         fg_color=PANEL).pack(side="left")
        else:
            ctk.CTkLabel(foot, text="COST", font=theme.font(12, "bold"), text_color=TEXT_MUTED,
                         fg_color=PANEL).pack(side="left", padx=(0, 8))
            for res, amount in cost.items():
                enough = campaign.resources.get(res, 0) >= amount
                ctk.CTkLabel(foot, text=f"{amount} {res}", font=theme.font(14, "bold"), fg_color=PANEL,
                             text_color=TEXT if enough else theme.DANGER).pack(side="left", padx=(0, 12))
        ctk.CTkButton(
            foot, text="EXPAND", width=110, height=36, font=theme.font(14, "bold"),
            fg_color=GOLD if affordable else PANEL_LIGHT, hover_color=GOLD_BRIGHT,
            text_color="#111111" if affordable else TEXT_MUTED, corner_radius=2,
            state="normal" if affordable else "disabled",
            command=lambda k=key: self._upgrade(k),
        ).pack(side="right")
        return card

    def _upgrade(self, key):
        if self.app.campaign.upgrade_building(key):
            self.refresh()

    def _end_turn(self):
        self.app.end_turn()
        self.refresh()
