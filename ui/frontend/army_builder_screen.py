"""
ui/frontend/army_builder_screen.py
Army Builder: raise formations, recruit units and deploy them to battle.
"""

from tkinter import messagebox

import customtkinter as ctk

from ui.frontend import theme
from ui.frontend.theme import BORDER, GOLD, GOLD_BRIGHT, PANEL, PANEL_HOVER, PANEL_LIGHT, TEXT, TEXT_DIM, TEXT_MUTED
from ui.frontend.widgets import (
    ResourceBar, ScreenHeader, danger_button, primary_button, secondary_button, section_label,
    styled_entry, styled_option_menu,
)

UNIT_TYPES = {
    "Tank / AFV":          {"cost": {"RUs": 60, "CUs": 40, "Fuel": 20, "Manpower": 5},
                            "fallback": ["Light Tank", "Medium Tank", "Heavy Tank", "Armored Car"]},
    "Infantry Squad":      {"cost": {"RUs": 10, "Manpower": 12},
                            "fallback": ["Rifle Squad", "Assault Squad", "Engineer Squad"]},
    "Infantry Platoon":    {"cost": {"RUs": 30, "Manpower": 36},
                            "fallback": ["Rifle Platoon", "Marine Platoon", "Paratroop Platoon"]},
    "Artillery Support":   {"cost": {"RUs": 40, "CUs": 20, "Manpower": 8},
                            "fallback": ["75mm Field Gun", "105mm Howitzer", "81mm Mortar Battery"]},
    "Support Weapon Team": {"cost": {"RUs": 15, "CUs": 5, "Manpower": 4},
                            "fallback": ["HMG Team", "AT Gun Team", "Mortar Team", "Flamethrower Team"]},
}

TROOP_CLASSES = {
    "A - Elite (+2)": 1.6,
    "B - Veteran (+1)": 1.3,
    "C - Battle Tested (0)": 1.0,
    "D - Recruit (-1)": 0.8,
    "E - Civilian (-2)": 0.6,
}

DISMISS_REFUND = 0.5


def unit_cost(unit_type, troop_class):
    multiplier = TROOP_CLASSES.get(troop_class, 1.0)
    return {res: int(round(amount * multiplier)) for res, amount in UNIT_TYPES[unit_type]["cost"].items()}


def format_cost(cost):
    return "  ".join(f"{amount} {res}" for res, amount in cost.items())


class ArmyBuilderScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_DARK, corner_radius=0)
        self.app = app
        self.selected_index = None

        ScreenHeader(self, "card_army.jpg", "Army Builder", "Raise and organize your forces",
                     lambda: app.show_screen("menu"), focus_y=0.45).pack(fill="x")

        top = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=84)
        top.pack(fill="x")
        top.pack_propagate(False)
        self.resource_bar = ResourceBar(top)
        self.resource_bar.pack(side="left", padx=36, pady=18)
        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color=theme.BG_DARK, corner_radius=0)
        body.pack(fill="both", expand=True, padx=36, pady=24)
        body.grid_columnconfigure(0, weight=0, minsize=300)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=0, minsize=360)
        body.grid_rowconfigure(0, weight=1)

        self._build_formations_column(body)
        self._build_roster_column(body)
        self._build_recruit_column(body)

    # ----------------------------------------------------------------- columns

    def _column(self, parent, col, padx):
        frame = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=4, border_width=1, border_color=BORDER)
        frame.grid(row=0, column=col, sticky="nsew", padx=padx)
        return frame

    def _build_formations_column(self, body):
        col = self._column(body, 0, (0, 18))
        section_label(col, "Formations").pack(fill="x", pady=(18, 10))
        self.formation_list = ctk.CTkScrollableFrame(col, fg_color=PANEL, corner_radius=0,
                                                     scrollbar_button_color=BORDER)
        self.formation_list.pack(fill="both", expand=True, padx=8)

        form = ctk.CTkFrame(col, fg_color=PANEL, corner_radius=0)
        form.pack(fill="x", padx=18, pady=(10, 18))
        self.formation_name = styled_entry(form, width=260, placeholder="Formation name")
        self.formation_name.pack(fill="x")
        self.formation_side = ctk.StringVar(value="Blue")
        ctk.CTkSegmentedButton(
            form, values=["Blue", "Red"], variable=self.formation_side, height=34,
            font=theme.font(13, "bold"), fg_color=PANEL_LIGHT, selected_color="#8f6f2e",
            selected_hover_color="#a8843a", unselected_color=PANEL_LIGHT,
            unselected_hover_color=PANEL_HOVER, text_color=TEXT, corner_radius=2,
        ).pack(fill="x", pady=8)
        primary_button(form, "+ New Formation", self._create_formation, width=260, height=40, size=14).pack(fill="x")

    def _build_roster_column(self, body):
        col = self._column(body, 1, (0, 18))
        head = ctk.CTkFrame(col, fg_color=PANEL, corner_radius=0)
        head.pack(fill="x", padx=22, pady=(18, 0))
        self.side_stripe = ctk.CTkFrame(head, width=6, height=44, fg_color=BORDER, corner_radius=0)
        self.side_stripe.pack(side="left", padx=(0, 14))
        title_col = ctk.CTkFrame(head, fg_color=PANEL, corner_radius=0)
        title_col.pack(side="left")
        self.roster_title = ctk.CTkLabel(title_col, text="NO FORMATION SELECTED", font=theme.font(22, "bold"),
                                         text_color=TEXT, fg_color=PANEL, anchor="w", height=26)
        self.roster_title.pack(anchor="w")
        self.roster_sub = ctk.CTkLabel(title_col, text="Create a formation to begin recruiting.",
                                       font=theme.font(13), text_color=TEXT_DIM, fg_color=PANEL,
                                       anchor="w", height=18)
        self.roster_sub.pack(anchor="w")

        actions = ctk.CTkFrame(head, fg_color=PANEL, corner_radius=0)
        actions.pack(side="right")
        self.deploy_btn = primary_button(actions, "Deploy to Battle", self._deploy, width=190, height=40, size=14)
        self.deploy_btn.pack(side="right")
        self.disband_btn = danger_button(actions, "Disband", self._disband, width=110)
        self.disband_btn.pack(side="right", padx=10)

        ctk.CTkFrame(col, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x", padx=22, pady=14)

        header = ctk.CTkFrame(col, fg_color=PANEL, corner_radius=0)
        header.pack(fill="x", padx=30)
        for text, width in (("CALLSIGN", 100), ("TYPE", 170), ("UNIT", 220), ("CLASS", 170)):
            ctk.CTkLabel(header, text=text, width=width, anchor="w", font=theme.font(11, "bold"),
                         text_color=TEXT_MUTED, fg_color=PANEL).pack(side="left")

        self.roster = ctk.CTkScrollableFrame(col, fg_color=PANEL, corner_radius=0, scrollbar_button_color=BORDER)
        self.roster.pack(fill="both", expand=True, padx=16, pady=(4, 16))

    def _build_recruit_column(self, body):
        col = self._column(body, 2, 0)
        section_label(col, "Recruit unit").pack(fill="x", pady=(18, 10))
        inner = ctk.CTkFrame(col, fg_color=PANEL, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=20)

        def label(text):
            ctk.CTkLabel(inner, text=text.upper(), font=theme.font(12, "bold"), text_color=TEXT_MUTED,
                         fg_color=PANEL, anchor="w").pack(fill="x", pady=(10, 2))

        label("Unit type")
        self.type_var = ctk.StringVar(value=list(UNIT_TYPES)[0])
        styled_option_menu(inner, list(UNIT_TYPES), self.type_var, command=self._on_type_change,
                           width=320).pack(fill="x")
        label("Unit")
        self.unit_var = ctk.StringVar(value="")
        self.unit_menu = styled_option_menu(inner, [""], self.unit_var, width=320)
        self.unit_menu.pack(fill="x")
        label("Troop class")
        self.class_var = ctk.StringVar(value="C - Battle Tested (0)")
        styled_option_menu(inner, list(TROOP_CLASSES), self.class_var,
                           command=lambda _v: self._update_cost(), width=320).pack(fill="x")
        label("Callsign")
        self.callsign = styled_entry(inner, width=320)
        self.callsign.pack(fill="x")

        cost_box = ctk.CTkFrame(inner, fg_color=theme.BG_DARK, corner_radius=2, border_width=1, border_color=BORDER)
        cost_box.pack(fill="x", pady=(22, 0))
        ctk.CTkLabel(cost_box, text="RECRUITMENT COST", font=theme.font(11, "bold"), text_color=TEXT_MUTED,
                     fg_color=theme.BG_DARK).pack(anchor="w", padx=14, pady=(10, 0))
        self.cost_label = ctk.CTkLabel(cost_box, text="", font=theme.font(16, "bold"), text_color=TEXT,
                                       fg_color=theme.BG_DARK, anchor="w", justify="left")
        self.cost_label.pack(anchor="w", padx=14, pady=(2, 0))
        self.cost_note = ctk.CTkLabel(cost_box, text="", font=theme.font(12), text_color=TEXT_DIM,
                                      fg_color=theme.BG_DARK, anchor="w", justify="left", wraplength=300)
        self.cost_note.pack(anchor="w", padx=14, pady=(2, 12))

        self.recruit_btn = primary_button(inner, "Recruit", self._recruit, width=320, height=46)
        self.recruit_btn.pack(fill="x", pady=(18, 18), side="bottom")

    # ------------------------------------------------------------------ state

    @property
    def formations(self):
        return self.app.campaign.armies

    @property
    def selected(self):
        if self.selected_index is not None and 0 <= self.selected_index < len(self.formations):
            return self.formations[self.selected_index]
        return None

    def nation_for(self, side):
        campaign = self.app.campaign
        return campaign.blue_nation if side == "Blue" else campaign.red_nation

    def catalog(self, unit_type, nation):
        data = self.app.data
        if unit_type == "Tank / AFV":
            names = [t.get("MODEL") for t in data.tanks.get(nation, [])]
        elif "Infantry" in unit_type:
            names = [i.get("UNIT_NAME") for i in getattr(data, "infantry", {}).get(nation, [])]
        elif unit_type == "Artillery Support":
            names = [a.get("UNIT_NAME") for a in getattr(data, "artillery", {}).get(nation, [])]
        else:
            names = []
        names = [str(n) for n in names if n and str(n) != "nan"]
        return names or UNIT_TYPES[unit_type]["fallback"]

    def on_show(self):
        if self.selected is None and self.formations:
            self.selected_index = 0
        self.refresh()

    def refresh(self):
        campaign = self.app.campaign
        if not campaign:
            return
        self.resource_bar.update_values(campaign.resources)
        self._render_formations()
        self._render_roster()
        self._on_type_change()

    def _render_formations(self):
        for child in self.formation_list.winfo_children():
            child.destroy()
        if not self.formations:
            ctk.CTkLabel(self.formation_list, text="No formations yet.", font=theme.font(14),
                         text_color=TEXT_MUTED, fg_color=PANEL).pack(pady=24)
            return
        for idx, formation in enumerate(self.formations):
            selected = idx == self.selected_index
            bg = PANEL_HOVER if selected else PANEL
            row = ctk.CTkFrame(self.formation_list, fg_color=bg, corner_radius=2, border_width=1,
                               border_color=GOLD if selected else PANEL, height=58)
            row.pack(fill="x", pady=3, padx=2)
            row.pack_propagate(False)
            stripe = ctk.CTkFrame(row, width=4, fg_color=theme.side_color(formation["side"]), corner_radius=0)
            stripe.pack(side="left", fill="y", padx=(1, 10), pady=1)
            text_col = ctk.CTkFrame(row, fg_color=bg, corner_radius=0)
            text_col.pack(side="left", fill="both", expand=True, pady=7)
            name = ctk.CTkLabel(text_col, text=formation["name"], font=theme.font(15, "bold"),
                                text_color=GOLD_BRIGHT if selected else TEXT, fg_color=bg, anchor="w", height=20)
            name.pack(fill="x")
            sub = ctk.CTkLabel(text_col, text=f"{formation['side']} Force  \u2022  {len(formation['units'])} units",
                               font=theme.font(12), text_color=TEXT_DIM, fg_color=bg, anchor="w", height=18)
            sub.pack(fill="x")
            for w in (row, text_col, name, sub):
                w.bind("<Button-1>", lambda _e, i=idx: self._select(i), add="+")

    def _render_roster(self):
        for child in self.roster.winfo_children():
            child.destroy()
        formation = self.selected
        has = formation is not None
        for btn in (self.deploy_btn, self.disband_btn, self.recruit_btn):
            btn.configure(state="normal" if has else "disabled")
        if not has:
            self.side_stripe.configure(fg_color=BORDER)
            self.roster_title.configure(text="NO FORMATION SELECTED")
            self.roster_sub.configure(text="Create a formation to begin recruiting.")
            return

        side = formation["side"]
        self.side_stripe.configure(fg_color=theme.side_color(side))
        self.roster_title.configure(text=formation["name"].upper())
        counts = {}
        for unit in formation["units"]:
            counts[unit["unit_type"]] = counts.get(unit["unit_type"], 0) + 1
        summary = "  \u2022  ".join(f"{n}\u00d7 {t}" for t, n in counts.items()) or "No units recruited"
        self.roster_sub.configure(text=f"{side} Force \u2013 {self.nation_for(side)}   |   {summary}")

        if not formation["units"]:
            ctk.CTkLabel(self.roster, text="Use the recruitment panel to add units to this formation.",
                         font=theme.font(14), text_color=TEXT_MUTED, fg_color=PANEL).pack(pady=40)
            return
        for idx, unit in enumerate(formation["units"]):
            bg = PANEL_LIGHT if idx % 2 == 0 else PANEL
            row = ctk.CTkFrame(self.roster, fg_color=bg, corner_radius=0, height=42)
            row.pack(fill="x")
            row.pack_propagate(False)
            columns = ((unit["callsign"], 100, GOLD), (unit["unit_type"], 170, TEXT_DIM),
                       (unit["unit_name"], 220, TEXT), (unit["troop_class"], 170, TEXT_DIM))
            for col_idx, (text, width, color) in enumerate(columns):
                ctk.CTkLabel(row, text=text, width=width, anchor="w",
                             font=theme.font(14, "bold" if col_idx == 0 else "normal"),
                             text_color=color, fg_color=bg).pack(side="left", padx=(14 if col_idx == 0 else 0, 0))
            ctk.CTkButton(row, text="DISMISS", width=84, height=28, font=theme.font(12, "bold"),
                          fg_color="transparent", hover_color="#3a1616", text_color=theme.DANGER,
                          border_color="#4a2020", border_width=1, corner_radius=2,
                          command=lambda i=idx: self._dismiss(i)).pack(side="right", padx=10)

    def _select(self, index):
        self.selected_index = index
        self._render_formations()
        self._render_roster()
        self._on_type_change()

    def _on_type_change(self, _value=None):
        formation = self.selected
        side = formation["side"] if formation else self.app.campaign.player_side
        units = self.catalog(self.type_var.get(), self.nation_for(side))
        self.unit_menu.configure(values=units)
        if self.unit_var.get() not in units:
            self.unit_var.set(units[0])
        self.callsign.delete(0, "end")
        self.callsign.insert(0, self._next_callsign(side))
        self._update_cost()

    def _next_callsign(self, side):
        prefix = side[0]
        used = {u["callsign"] for f in self.formations for u in f["units"]}
        n = 1
        while f"{prefix}{n}" in used:
            n += 1
        return f"{prefix}{n}"

    def _is_player_side(self, formation):
        return formation is None or formation["side"] == self.app.campaign.player_side

    def _update_cost(self):
        cost = unit_cost(self.type_var.get(), self.class_var.get())
        formation = self.selected
        self.cost_label.configure(text=format_cost(cost))
        if not self._is_player_side(formation):
            self.cost_note.configure(text="Opposing force: not charged to your treasury.", text_color=TEXT_DIM)
            self.cost_label.configure(text_color=TEXT_MUTED)
        elif self.app.campaign.can_afford(cost):
            self.cost_note.configure(text="Funds available.", text_color=theme.SUCCESS)
            self.cost_label.configure(text_color=TEXT)
        else:
            missing = [r for r, a in cost.items() if self.app.campaign.resources.get(r, 0) < a]
            self.cost_note.configure(text=f"Insufficient {', '.join(missing)}.", text_color=theme.DANGER)
            self.cost_label.configure(text_color=theme.DANGER)

    # ---------------------------------------------------------------- actions

    def _create_formation(self):
        name = self.formation_name.get().strip()
        side = self.formation_side.get()
        if not name:
            count = sum(1 for f in self.formations if f["side"] == side) + 1
            name = f"{side} Task Force {count}"
        self.formations.append({"name": name, "side": side, "units": []})
        self.app.campaign.add_log(f"Formation '{name}' raised.")
        self.formation_name.delete(0, "end")
        self.selected_index = len(self.formations) - 1
        self.refresh()

    def _disband(self):
        formation = self.selected
        if not formation:
            return
        if not messagebox.askyesno("Disband Formation",
                                   f"Disband '{formation['name']}'? Player units are refunded "
                                   f"{int(DISMISS_REFUND * 100)}% of their cost."):
            return
        if self._is_player_side(formation):
            for unit in formation["units"]:
                self.app.campaign.refund(unit["cost"], DISMISS_REFUND)
        self.formations.pop(self.selected_index)
        self.app.campaign.add_log(f"Formation '{formation['name']}' disbanded.")
        self.selected_index = 0 if self.formations else None
        self.refresh()

    def _recruit(self):
        formation = self.selected
        if not formation:
            return
        callsign = self.callsign.get().strip()
        if not callsign:
            messagebox.showwarning("Recruit", "Enter a callsign for the unit.")
            return
        if any(u["callsign"] == callsign for f in self.formations for u in f["units"]):
            messagebox.showwarning("Recruit", f"Callsign '{callsign}' is already in use.")
            return
        cost = unit_cost(self.type_var.get(), self.class_var.get())
        if self._is_player_side(formation) and not self.app.campaign.spend(cost):
            messagebox.showwarning("Insufficient Resources", "Your treasury cannot fund this unit.")
            return
        formation["units"].append({
            "callsign": callsign,
            "unit_type": self.type_var.get(),
            "unit_name": self.unit_var.get(),
            "troop_class": self.class_var.get(),
            "cost": cost if self._is_player_side(formation) else {},
        })
        self.app.campaign.dirty = True
        self.refresh()

    def _dismiss(self, index):
        formation = self.selected
        unit = formation["units"].pop(index)
        self.app.campaign.refund(unit.get("cost", {}), DISMISS_REFUND)
        self.refresh()

    def _deploy(self):
        formation = self.selected
        if not formation or not formation["units"]:
            messagebox.showinfo("Deploy", "Recruit at least one unit before deploying.")
            return
        side = formation["side"]
        nation = self.nation_for(side)
        units = []
        for unit in formation["units"]:
            is_tank = unit["unit_type"] == "Tank / AFV"
            units.append({
                "name": unit["callsign"],
                "country": nation,
                "unit_type": unit["unit_type"],
                "unit_name": unit["unit_name"],
                "tank": unit["unit_name"],
                "data": self.app.data.get_tank_by_name(nation, unit["unit_name"]) if is_tank else None,
                "troop_class": unit["troop_class"],
                "troop_modifier": self.app.get_troop_modifier(unit["troop_class"]),
            })
        if side == "Blue":
            self.app.blue_country = nation
            self.app.blue_units[:] = units
        else:
            self.app.red_country = nation
            self.app.red_units[:] = units
        if messagebox.askyesno("Formation Deployed",
                               f"'{formation['name']}' deployed as the {side} force "
                               f"({len(units)} units).\n\nOpen the tactical battle now?"):
            self.app.show_screen("battle")
