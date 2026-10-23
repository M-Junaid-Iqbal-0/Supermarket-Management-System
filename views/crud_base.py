"""
views/crud_base.py
Base class for simple CRUD views.
Subclass and implement: TABLE, COLUMNS, SQL_SELECT, SQL_INSERT,
SQL_UPDATE, SQL_DELETE, build_form(), form_values(), populate_form().
"""

import tkinter as tk
from tkinter import messagebox
from widgets import AppButton, DataTable, toast
from theme import *
from db.connection import fetch_all, execute


class CrudBase(tk.Frame):
    # ── Override in subclass ──────────────────────────────
    TITLE       = "Records"
    TABLE       = ""
    COLUMNS     = []          # display column names
    SQL_SELECT  = ""
    SQL_INSERT  = ""
    SQL_UPDATE  = ""
    SQL_DELETE  = ""
    ID_COLUMN   = 0           # index of PK in selected row

    def __init__(self, parent, user, readonly=False):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self.readonly = readonly
        self.selected_row = None
        self._build_shell()
        self.build_form(self.form_frame)
        self.refresh()

    def _build_shell(self):
        # Top bar
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=PAD*2, pady=(PAD*2, 0))
        tk.Label(top, text=self.TITLE, font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")

        if not self.readonly:
            AppButton(top, "＋ Add",    command=self._add,    color=ACCENT).pack(side="right", padx=4)
            AppButton(top, "✏ Update",  command=self._update, color=ACCENT2).pack(side="right", padx=4)
            AppButton(top, "🗑 Delete",  command=self._delete, color=DANGER).pack(side="right", padx=4)

        AppButton(top, "↻ Refresh", command=self.refresh, color=BG_CARD).pack(side="right", padx=4)

        # Search bar
        search_bar = tk.Frame(self, bg=BG_DARK)
        search_bar.pack(fill="x", padx=PAD*2, pady=(8, 0))
        tk.Label(search_bar, text="Search:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        tk.Entry(search_bar, textvariable=self.search_var,
                 font=FONT_BODY, bg=BG_CARD, fg=TEXT_MAIN,
                 insertbackground=TEXT_MAIN, relief="flat",
                 highlightthickness=1, highlightbackground=BORDER,
                 width=30).pack(side="left", padx=8, ipady=4)

        # Main split
        split = tk.Frame(self, bg=BG_DARK)
        split.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)

        # Table (left/top)
        self.table = DataTable(split, columns=self.COLUMNS)
        self.table.pack(side="left", fill="both", expand=True)
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Form (right panel)
        if not self.readonly:
            self.form_frame = tk.Frame(split, bg=BG_PANEL, width=280, padx=PAD, pady=PAD)
            self.form_frame.pack(side="left", fill="y", padx=(PAD, 0))
            self.form_frame.pack_propagate(False)
            tk.Label(self.form_frame, text="Details", font=FONT_HEAD,
                     bg=BG_PANEL, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 8))
        else:
            self.form_frame = tk.Frame(self, bg=BG_DARK)  # dummy

        self._all_rows = []

    def build_form(self, parent):
        """Override: build input fields into parent frame."""
        pass

    def form_values(self) -> dict:
        """Override: return dict of field_name -> value."""
        return {}

    def populate_form(self, row):
        """Override: fill form fields from selected row tuple."""
        pass

    def clear_form(self):
        """Override if needed."""
        pass

    # ── Data ─────────────────────────────────────────────
    def refresh(self):
        try:
            _, rows = fetch_all(self.SQL_SELECT)
            self._all_rows = rows
            self.table.load(rows)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _filter(self):
        q = self.search_var.get().lower()
        if not q:
            self.table.load(self._all_rows)
            return
        filtered = [r for r in self._all_rows
                    if any(q in str(v).lower() for v in r)]
        self.table.load(filtered)

    def _on_select(self, _event=None):
        row = self.table.selected_values()
        if row:
            self.selected_row = row
            self.populate_form(row)

    # ── CRUD actions ──────────────────────────────────────
    def _add(self):
        vals = self.form_values()
        if not vals:
            return
        try:
            execute(self.SQL_INSERT, vals)
            self.refresh()
            self.clear_form()
            toast(self.winfo_toplevel(), f"Record added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update(self):
        if not self.selected_row:
            messagebox.showwarning("Select", "Select a row first.")
            return
        vals = self.form_values()
        if not vals:
            return
        vals["id"] = self.selected_row[self.ID_COLUMN]
        try:
            execute(self.SQL_UPDATE, vals)
            self.refresh()
            toast(self.winfo_toplevel(), "Record updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        if not self.selected_row:
            messagebox.showwarning("Select", "Select a row first.")
            return
        rid = self.selected_row[self.ID_COLUMN]
        if not messagebox.askyesno("Confirm", f"Delete record #{rid}?"):
            return
        try:
            execute(self.SQL_DELETE, {"id": rid})
            self.refresh()
            self.clear_form()
            toast(self.winfo_toplevel(), "Record deleted.", success=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
