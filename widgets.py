"""
widgets.py
Reusable tkinter widgets used across all views.
"""

import tkinter as tk
from tkinter import ttk
from theme import *


# ── Styled Button ─────────────────────────────────────────
class AppButton(tk.Button):
    def __init__(self, parent, text, command=None, color=ACCENT, **kw):
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=TEXT_WHITE,
            font=FONT_BTN,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            activebackground=color,
            activeforeground=TEXT_WHITE,
            **kw,
        )
        self.bind("<Enter>", lambda e: self.config(bg=self._lighten(color)))
        self.bind("<Leave>", lambda e: self.config(bg=color))

    @staticmethod
    def _lighten(hex_color):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        r, g, b = min(r+30, 255), min(g+30, 255), min(b+30, 255)
        return f"#{r:02x}{g:02x}{b:02x}"


# ── Styled Label ──────────────────────────────────────────
class Label(tk.Label):
    def __init__(self, parent, text, font=FONT_BODY, color=TEXT_MAIN, **kw):
        super().__init__(parent, text=text, font=font, fg=color, bg=BG_PANEL, **kw)


# ── Styled Entry ──────────────────────────────────────────
class AppEntry(tk.Entry):
    def __init__(self, parent, width=24, show=None, **kw):
        super().__init__(
            parent,
            width=width,
            font=FONT_BODY,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT2,
            show=show or "",
            **kw,
        )


# ── Styled Combobox ───────────────────────────────────────
class AppCombo(ttk.Combobox):
    def __init__(self, parent, values=(), width=22, **kw):
        super().__init__(parent, values=values, width=width,
                         font=FONT_BODY, state="readonly", **kw)


# ── Data Table (Treeview) ─────────────────────────────────
class DataTable(tk.Frame):
    """Scrollable treeview with styled headers."""

    def __init__(self, parent, columns: list, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.columns = columns
        self._build(columns)

    def _build(self, columns):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_MAIN,
                        fieldbackground=BG_CARD,
                        rowheight=ROW_H,
                        font=FONT_BODY,
                        borderwidth=0)
        style.configure("App.Treeview.Heading",
                        background=BG_PANEL,
                        foreground=ACCENT2,
                        font=FONT_BTN,
                        relief="flat")
        style.map("App.Treeview",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", TEXT_WHITE)])

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            style="App.Treeview",
            selectmode="browse",
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", minwidth=60,
                             width=max(80, len(col)*10))

        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def load(self, rows):
        """Clear and reload all rows."""
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def selected_values(self):
        """Return tuple of selected row values, or None."""
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"]


# ── Toast Notification ────────────────────────────────────
def toast(root, message: str, success: bool = True):
    """Temporary notification bubble."""
    color = ACCENT if success else DANGER
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.configure(bg=color)
    tk.Label(win, text=message, bg=color, fg=TEXT_WHITE,
             font=FONT_BTN, padx=16, pady=8).pack()
    # position bottom-right of root
    root.update_idletasks()
    rx, ry = root.winfo_x(), root.winfo_y()
    rw, rh = root.winfo_width(), root.winfo_height()
    win.geometry(f"+{rx+rw-260}+{ry+rh-80}")
    win.after(2500, win.destroy)


# ── Modal Dialog base ─────────────────────────────────────
class ModalDialog(tk.Toplevel):
    def __init__(self, parent, title: str, width=420, height=480):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_PANEL)
        self.resizable(False, False)
        self.grab_set()
        # center over parent
        parent.update_idletasks()
        px = parent.winfo_x() + parent.winfo_width()  // 2 - width  // 2
        py = parent.winfo_y() + parent.winfo_height() // 2 - height // 2
        self.geometry(f"{width}x{height}+{px}+{py}")

    def form_row(self, label: str, widget):
        """Add a label + widget row to this dialog."""
        row = tk.Frame(self, bg=BG_PANEL)
        row.pack(fill="x", padx=PAD*2, pady=4)
        tk.Label(row, text=label, font=FONT_BODY, fg=TEXT_DIM,
                 bg=BG_PANEL, width=16, anchor="w").pack(side="left")
        widget.configure(bg=BG_CARD if isinstance(widget, tk.Entry) else widget.cget("bg"))
        widget.pack(side="left", fill="x", expand=True)
        return widget
