"""
views/inventory_view.py
Inventory table — view + update stock levels.
"""

import tkinter as tk
from tkinter import messagebox
from widgets import AppButton, DataTable, AppEntry, toast
from db.connection import fetch_all, execute
from theme import *


class InventoryView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._all_rows = []
        self._build()
        self.refresh()

    def _build(self):
        # Header
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=PAD*2, pady=(PAD*2, 0))
        tk.Label(top, text="Inventory", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")

        AppButton(top, "↻ Refresh", command=self.refresh, color=BG_CARD).pack(side="right", padx=4)

        # Low stock filter
        self.low_var = tk.BooleanVar()
        tk.Checkbutton(top, text="Show Low Stock Only",
                       variable=self.low_var, command=self._filter,
                       bg=BG_DARK, fg=TEXT_DIM, selectcolor=BG_CARD,
                       activebackground=BG_DARK, font=FONT_BODY).pack(side="right", padx=8)

        # Search
        sbar = tk.Frame(self, bg=BG_DARK)
        sbar.pack(fill="x", padx=PAD*2, pady=(8, 0))
        tk.Label(sbar, text="Search:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        tk.Entry(sbar, textvariable=self.search_var, font=FONT_BODY,
                 bg=BG_CARD, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                 relief="flat", highlightthickness=1,
                 highlightbackground=BORDER, width=30).pack(
                     side="left", padx=8, ipady=4)

        # Main split
        split = tk.Frame(self, bg=BG_DARK)
        split.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)

        cols = ["Inv ID", "Product", "Category", "In Stock", "Reorder Level", "Status", "Last Updated"]
        self.table = DataTable(split, columns=cols)
        self.table.pack(side="left", fill="both", expand=True)
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Update panel
        panel = tk.Frame(split, bg=BG_PANEL, width=240, padx=PAD, pady=PAD)
        panel.pack(side="left", fill="y", padx=(PAD, 0))
        panel.pack_propagate(False)

        tk.Label(panel, text="Update Stock", font=FONT_HEAD,
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 12))

        tk.Label(panel, text="Selected Product",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.prod_label = tk.Label(panel, text="—", font=FONT_BODY,
                                   bg=BG_PANEL, fg=ACCENT2, wraplength=200)
        self.prod_label.pack(anchor="w", pady=(2, 12))

        tk.Label(panel, text="New Quantity", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.qty_var = tk.StringVar()
        AppEntry(panel, textvariable=self.qty_var, width=16).pack(anchor="w", ipady=4, pady=(2, 8))

        tk.Label(panel, text="Reorder Level", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.reorder_var = tk.StringVar()
        AppEntry(panel, textvariable=self.reorder_var, width=16).pack(anchor="w", ipady=4, pady=(2, 12))

        AppButton(panel, "Save Changes", command=self._update_stock, color=ACCENT).pack(fill="x")

        self._selected_inv_id = None

    def refresh(self):
        sql = """
            SELECT
                NVL(i.InventoryID, 0) AS InventoryID,
                p.ProductName,
                NVL(c.CategoryName, '—') AS CategoryName,
                NVL(i.QuantityInStock, 0) AS QuantityInStock,
                NVL(i.ReorderLevel, 0) AS ReorderLevel,
                CASE
                    WHEN NVL(i.QuantityInStock, 0) <= NVL(i.ReorderLevel, 0)
                    THEN 'LOW STOCK'
                    ELSE 'OK'
                END AS Status,
                CASE
                    WHEN i.LastUpdated IS NULL
                    THEN '—'
                    ELSE TO_CHAR(i.LastUpdated, 'DD-Mon-YYYY HH24:MI')
                END AS LastUpdated
            FROM Product p
            LEFT JOIN Inventory i
                ON p.ProductID = i.ProductID
            LEFT JOIN Category c
                ON p.CategoryID = c.CategoryID
            ORDER BY p.ProductID
        """

        try:
            _, rows = fetch_all(sql)

            self._all_rows = rows
            self.table.load(rows)

            for item in self.table.tree.get_children():
                vals = self.table.tree.item(item)["values"]

                if len(vals) > 5 and vals[5] == "LOW STOCK":
                    self.table.tree.item(item, tags=("low",))

            self.table.tree.tag_configure("low", foreground=DANGER)

        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _filter(self):
        q = self.search_var.get().lower()
        low_only = self.low_var.get()
        rows = self._all_rows
        if low_only:
            rows = [r for r in rows if r[5] == "LOW STOCK"]
        if q:
            rows = [r for r in rows if any(q in str(v).lower() for v in r)]
        self.table.load(rows)

    def _on_select(self, _=None):
        row = self.table.selected_values()
        if row:
            self._selected_inv_id = row[0]
            self.prod_label.config(text=row[1])
            self.qty_var.set(str(row[3]))
            self.reorder_var.set(str(row[4]))

    def _update_stock(self):
        if not self._selected_inv_id:
            messagebox.showwarning("Select", "Select an inventory row first.")
            return
        try:
            qty     = int(self.qty_var.get())
            reorder = int(self.reorder_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Quantity and Reorder Level must be whole numbers.")
            return
        sql = """
            UPDATE Inventory
            SET QuantityInStock=:qty, ReorderLevel=:reorder,
                LastUpdated=SYSTIMESTAMP
            WHERE InventoryID=:id
        """
        try:
            execute(sql, {"qty": qty, "reorder": reorder, "id": self._selected_inv_id})
            self.refresh()
            toast(self.winfo_toplevel(), "Stock updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
