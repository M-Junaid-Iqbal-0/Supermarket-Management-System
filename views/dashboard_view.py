"""
views/dashboard_view.py
Summary dashboard — stat cards + recent sales table.
"""

import tkinter as tk
from theme import *
from widgets import DataTable
from db.connection import fetch_all


class DashboardView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", padx=PAD*2, pady=(PAD*2, PAD))
        tk.Label(hdr, text="Dashboard", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")

        # Stat cards
        stats_row = tk.Frame(self, bg=BG_DARK)
        stats_row.pack(fill="x", padx=PAD*2, pady=(0, PAD))

        stats = self._load_stats()
        card_defs = [
            ("Total Customers",  stats.get("customers", "—"),  ACCENT2),
            ("Total Products",   stats.get("products",  "—"),  ACCENT),
            ("Active Sales",     stats.get("sales",     "—"),  WARNING),
            ("Low Stock Items",  stats.get("lowstock",  "—"),  DANGER),
        ]
        for label, value, color in card_defs:
            self._stat_card(stats_row, label, value, color).pack(
                side="left", fill="both", expand=True, padx=6)

        # Recent sales
        tk.Label(self, text="Recent Sales", font=FONT_HEAD,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w", padx=PAD*2, pady=(PAD, 4))

        cols = ["Sale ID", "Customer", "Employee", "Date", "Total (PKR)", "Paid Via"]
        self.table = DataTable(self, columns=cols)
        self.table.pack(fill="both", expand=True, padx=PAD*2, pady=(0, PAD*2))
        self._load_recent_sales()

    def _stat_card(self, parent, label, value, color):
        card = tk.Frame(parent, bg=BG_PANEL, padx=18, pady=14)
        tk.Label(card, text=str(value), font=(FONT_FAMILY, 28, "bold"),
                 bg=BG_PANEL, fg=color).pack(anchor="w")
        tk.Label(card, text=label, font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        return card

    def _load_stats(self):
        stats = {}
        queries = {
            "customers": "SELECT COUNT(*) FROM Customer",
            "products":  "SELECT COUNT(*) FROM Product",
            "sales":     "SELECT COUNT(*) FROM Sale",
            "lowstock":  "SELECT COUNT(*) FROM Inventory WHERE QuantityInStock <= ReorderLevel",
        }
        for key, sql in queries.items():
            try:
                _, rows = fetch_all(sql)
                stats[key] = rows[0][0] if rows else 0
            except Exception:
                stats[key] = "err"
        return stats

    def _load_recent_sales(self):
        sql = """
            SELECT s.SaleID,
                   NVL(c.FirstName||' '||c.LastName, 'Walk-in') AS Customer,
                   NVL(e.FirstName||' '||e.LastName, '—')       AS Employee,
                   TO_CHAR(s.SaleDate,'DD-Mon-YYYY HH24:MI')    AS SaleDate,
                   s.TotalAmount,
                   NVL(p.PaymentMethod, '—')                    AS PayMethod
            FROM Sale s
            LEFT JOIN Customer c  ON s.CustomerID  = c.CustomerID
            LEFT JOIN Employee e  ON s.EmployeeID  = e.EmployeeID
            LEFT JOIN Payment  p  ON s.SaleID      = p.SaleID
            ORDER BY s.SaleDate DESC
            FETCH FIRST 20 ROWS ONLY
        """
        try:
            _, rows = fetch_all(sql)
            self.table.load(rows)
        except Exception as ex:
            tk.Label(self, text=f"Could not load sales: {ex}",
                     bg=BG_DARK, fg=DANGER, font=FONT_SMALL).pack()
