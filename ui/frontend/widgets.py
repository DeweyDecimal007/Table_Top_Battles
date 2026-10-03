"""
ui/frontend/widgets.py
Styled building blocks for the front-end: menu buttons, feature cards,
resource bars, screen headers and modal panels.
"""

import customtkinter as ctk

from game_engine.campaign_state import RESOURCES
from ui.frontend import theme
from ui.frontend.theme import (
    BORDER, GOLD, GOLD_BRIGHT, PANEL, PANEL_HOVER, PANEL_LIGHT, TEXT, TEXT_DIM, TEXT_MUTED,
)


class MenuButton(ctk.CTkFrame):
    """Full-width menu entry with a gold accent bar that lights up on hover."""

    def __init__(self, master, text, command, subtitle=None, height=50, size=20, bg=PANEL):
        super().__init__(master, fg_color=bg, corner_radius=0, height=height)
        self.pack_propagate(False)
        self._command = command
        self._enabled = True
        self._bg = bg

        self.accent = ctk.CTkFrame(self, width=4, height=height, fg_color=bg, corner_radius=0)
        self.accent.pack(side="left", fill="y")
        self.spacer = ctk.CTkFrame(self, width=32, height=height, fg_color=bg, corner_radius=0)
        self.spacer.pack(side="left", fill="y")

        self.button = ctk.CTkButton(
            self, text=text.upper(), command=self._invoke, anchor="w",
            font=theme.font(size, "bold"), fg_color=bg, hover_color=PANEL_HOVER,
            text_color=TEXT, text_color_disabled=TEXT_MUTED,
            corner_radius=0, height=height, border_spacing=4,
        )
        self.button.pack(side="left", fill="both", expand=True)

        self.subtitle = None
        if subtitle:
            self.subtitle = ctk.CTkLabel(self, text=subtitle, font=theme.font(12),
                                         text_color=TEXT_MUTED, fg_color=bg)
            self.subtitle.place(relx=1.0, rely=0.5, x=-18, anchor="e")

        for widget in (self.accent, self.spacer, self.button, self.subtitle):
            if widget is None:
                continue
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            if widget is not self.button:
                widget.bind("<Button-1>", lambda _e: self._invoke(), add="+")

    def _invoke(self):
        if self._enabled and self._command:
            self._command()

    def _set_hover(self, hovered):
        bg = PANEL_HOVER if hovered else self._bg
        self.accent.configure(fg_color=GOLD_BRIGHT if hovered else self._bg)
        self.spacer.configure(fg_color=bg)
        self.button.configure(fg_color=bg, text_color=GOLD_BRIGHT if hovered else TEXT)
        if self.subtitle:
            self.subtitle.configure(fg_color=bg)

    def _on_enter(self, _event=None):
        if self._enabled:
            self._set_hover(True)

    def _on_leave(self, _event=None):
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        while widget is not None:
            if widget is self:
                return
            widget = widget.master
        self._set_hover(False)

    def set_enabled(self, enabled):
        self._enabled = enabled
        self.button.configure(state="normal" if enabled else "disabled")
        if not enabled:
            self._set_hover(False)


def section_label(master, text, bg=PANEL, indent=18):
    frame = ctk.CTkFrame(master, fg_color=bg, corner_radius=0)
    ctk.CTkLabel(frame, text=text.upper(), font=theme.font(12, "bold"),
                 text_color=GOLD, fg_color=bg).pack(side="left", padx=(indent, 8))
    ctk.CTkFrame(frame, height=1, fg_color=BORDER, corner_radius=0).pack(
        side="left", fill="x", expand=True, padx=(0, 18), pady=(2, 0))
    return frame


def primary_button(master, text, command, width=180, height=44, size=16):
    return ctk.CTkButton(
        master, text=text.upper(), command=command, width=width, height=height,
        font=theme.font(size, "bold"), fg_color=GOLD, hover_color=GOLD_BRIGHT,
        text_color="#111111", corner_radius=2,
    )


def secondary_button(master, text, command, width=160, height=40, size=14):
    return ctk.CTkButton(
        master, text=text.upper(), command=command, width=width, height=height,
        font=theme.font(size, "bold"), fg_color="transparent", hover_color=PANEL_HOVER,
        text_color=TEXT, border_color=BORDER, border_width=1, corner_radius=2,
    )


def danger_button(master, text, command, width=120, height=40, size=14):
    return ctk.CTkButton(
        master, text=text.upper(), command=command, width=width, height=height,
        font=theme.font(size, "bold"), fg_color="transparent", hover_color="#3a1616",
        text_color=theme.DANGER, border_color="#4a2020", border_width=1, corner_radius=2,
    )


def styled_option_menu(master, values, variable=None, command=None, width=260):
    return ctk.CTkOptionMenu(
        master, values=values, variable=variable, command=command, width=width, height=38,
        font=theme.font(15), dropdown_font=theme.font(14),
        fg_color=PANEL_LIGHT, button_color=BORDER, button_hover_color=PANEL_HOVER,
        dropdown_fg_color=PANEL_LIGHT, dropdown_hover_color=PANEL_HOVER,
        text_color=TEXT, corner_radius=2,
    )


def styled_entry(master, width=260, placeholder=""):
    return ctk.CTkEntry(
        master, width=width, height=38, font=theme.font(15), placeholder_text=placeholder,
        fg_color=PANEL_LIGHT, border_color=BORDER, text_color=TEXT, corner_radius=2,
    )


class FeatureCard(ctk.CTkFrame):
    """Large clickable card with artwork, title and description."""

    def __init__(self, master, art_name, title, description, command, width=330, img_height=180):
        super().__init__(master, fg_color=PANEL, corner_radius=4, border_width=2,
                         border_color=BORDER, width=width)
        self._command = command
        art = theme.cover_crop(theme.load_art(art_name), width * 2, img_height * 2)
        self._image = ctk.CTkImage(light_image=art, dark_image=art, size=(width - 8, img_height))

        self.image_label = ctk.CTkLabel(self, text="", image=self._image, fg_color=PANEL)
        self.image_label.pack(padx=4, pady=(4, 0))

        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=theme.font(20, "bold"),
                                        text_color=TEXT, anchor="w", fg_color=PANEL)
        self.title_label.pack(fill="x", padx=16, pady=(12, 0))

        self.desc_label = ctk.CTkLabel(self, text=description, font=theme.font(13), text_color=TEXT_DIM,
                                       anchor="w", justify="left", wraplength=width - 36, fg_color=PANEL)
        self.desc_label.pack(fill="x", padx=16, pady=(4, 0))

        self.cta = ctk.CTkLabel(self, text="ENTER  \u25B8", font=theme.font(13, "bold"),
                                text_color=GOLD, anchor="w", fg_color=PANEL)
        self.cta.pack(fill="x", padx=16, pady=(8, 14))

        for widget in (self, self.image_label, self.title_label, self.desc_label, self.cta):
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            widget.bind("<Button-1>", lambda _e: self._command(), add="+")
            try:
                widget.configure(cursor="hand2")
            except (ValueError, TypeError):
                pass

    def _on_enter(self, _event=None):
        self.configure(border_color=GOLD_BRIGHT)
        self.title_label.configure(text_color=GOLD_BRIGHT)
        self.cta.configure(text_color=GOLD_BRIGHT)

    def _on_leave(self, event=None):
        if event is not None:
            x, y = self.winfo_pointerxy()
            widget = self.winfo_containing(x, y)
            while widget is not None:
                if widget is self:
                    return
                widget = widget.master
        self.configure(border_color=BORDER)
        self.title_label.configure(text_color=TEXT)
        self.cta.configure(text_color=GOLD)


class ResourceBar(ctk.CTkFrame):
    """Horizontal strip of resource chips: amount plus optional per-turn delta."""

    def __init__(self, master, bg=PANEL, compact=False):
        super().__init__(master, fg_color=bg, corner_radius=0)
        self._bg = bg
        self.chips = {}
        for key, meta in RESOURCES.items():
            chip = ctk.CTkFrame(self, fg_color=bg, corner_radius=0)
            chip.pack(side="left", padx=(0, 18 if compact else 26))
            ctk.CTkFrame(chip, width=4, height=34, fg_color=meta["color"], corner_radius=0).pack(
                side="left", padx=(0, 8))
            text_col = ctk.CTkFrame(chip, fg_color=bg, corner_radius=0)
            text_col.pack(side="left")
            ctk.CTkLabel(text_col, text=key.upper(), font=theme.font(11, "bold"),
                         text_color=TEXT_MUTED, fg_color=bg, height=14, anchor="w").pack(anchor="w")
            value = ctk.CTkLabel(text_col, text="0", font=theme.font(17 if compact else 19, "bold"),
                                 text_color=TEXT, fg_color=bg, height=22, anchor="w")
            value.pack(anchor="w")
            self.chips[key] = value

    def update_values(self, resources, production=None):
        for key, label in self.chips.items():
            text = f"{resources.get(key, 0):,}"
            if production and production.get(key):
                text += f"  +{production[key]}"
            label.configure(text=text)


class ScreenHeader(ctk.CTkFrame):
    """Art banner across the top of a sub-screen, with a back button."""

    HEIGHT = 150

    def __init__(self, master, art_name, title, subtitle, on_back, focus_y=0.5):
        super().__init__(master, fg_color=theme.BG_DARK, corner_radius=0, height=self.HEIGHT)
        self.pack_propagate(False)
        banner = theme.banner_image(art_name, 2560 * 2, self.HEIGHT * 2, title, subtitle, focus_y=focus_y)
        self._image = ctk.CTkImage(light_image=banner, dark_image=banner, size=(2560, self.HEIGHT))
        ctk.CTkLabel(self, text="", image=self._image).place(x=0, y=0)

        ctk.CTkButton(
            self, text="\u25C2  COMMAND CENTER", command=on_back, width=190, height=36,
            font=theme.font(14, "bold"), fg_color=PANEL, hover_color=PANEL_HOVER,
            text_color=TEXT, border_color=GOLD, border_width=1, corner_radius=2,
        ).place(relx=1.0, x=-24, y=22, anchor="ne")


class ModalPanel(ctk.CTkFrame):
    """Centered overlay panel with a gold frame and a title strip."""

    def __init__(self, master, title, width=640, height=560, on_close=None):
        super().__init__(master, fg_color=PANEL, corner_radius=4, border_width=2,
                         border_color=GOLD, width=width, height=height)
        self.pack_propagate(False)
        self._on_close = on_close

        title_bar = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=64)
        title_bar.pack(fill="x", padx=2, pady=(2, 0))
        title_bar.pack_propagate(False)
        ctk.CTkLabel(title_bar, text=title.upper(), font=theme.font(24, "bold"),
                     text_color=GOLD_BRIGHT, fg_color=PANEL).pack(side="left", padx=28)
        ctk.CTkButton(title_bar, text="\u2715", width=36, height=36, command=self.close,
                      font=theme.font(16, "bold"), fg_color=PANEL, hover_color=PANEL_HOVER,
                      text_color=TEXT_DIM, corner_radius=2).pack(side="right", padx=16)
        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x", padx=24)

        self.footer = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=76)
        self.footer.pack(fill="x", side="bottom", padx=28, pady=(0, 14))

        self.body = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        self.body.pack(fill="both", expand=True, padx=28, pady=(18, 0))

    def show(self):
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.lift()

    def close(self):
        if not self.winfo_exists():
            return
        self.place_forget()
        self.destroy()
        if self._on_close:
            self._on_close()
