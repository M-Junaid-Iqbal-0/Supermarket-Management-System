"""
views/product_view.py
Full CRUD for Product table.
"""

import tkinter as tk
from views.crud_base import CrudBase
from widgets import AppEntry, AppCombo
from db.connection import fetch_all
from theme import *


class ProductView(CrudBase):
    TITLE = "Products"
    COLUMNS = ["ID", "Product Name", "Brand", "Price", "Category", "Expiry", "Description"]

    SQL_SELECT = """
        SELECT p.ProductID, p.ProductName, p.Brand, p.UnitPrice,
               NVL(c.CategoryName,'—'),
               NVL(TO_CHAR(p.ExpiryDate,'DD-Mon-YYYY'),'—'),
               NVL(p.Description,'—')
        FROM Product p
        LEFT JOIN Category c ON p.CategoryID = c.CategoryID
        ORDER BY p.ProductID
    """

    SQL_INSERT = """
        INSERT INTO Product (
            ProductName, Brand, UnitPrice,
            CategoryID, ExpiryDate, Description
        )
        VALUES (
            :name, :brand, :price,
            :cat_id,
            TO_DATE(:expiry,'YYYY-MM-DD'),
            :description
        )
    """

    SQL_UPDATE = """
        UPDATE Product
        SET ProductName=:name,
            Brand=:brand,
            UnitPrice=:price,
            CategoryID=:cat_id,
            ExpiryDate=TO_DATE(:expiry,'YYYY-MM-DD'),
            Description=:description
        WHERE ProductID=:id
    """

    SQL_DELETE = "DELETE FROM Product WHERE ProductID=:id"
    ID_COLUMN = 0

    def _load_categories(self):
        try:
            _, rows = fetch_all(
                "SELECT CategoryID, CategoryName FROM Category ORDER BY CategoryName"
            )
            self._cat_map = {name: cid for cid, name in rows}
            return list(self._cat_map.keys())
        except:
            self._cat_map = {}
            return []

    def build_form(self, parent):
        cats = self._load_categories()
        self._vars = {}

        fields = [
            ("Product Name", "name"),
            ("Brand", "brand"),
            ("Unit Price", "price"),
            ("Expiry (YYYY-MM-DD)", "expiry"),
            ("Description", "description"),
        ]

        for label, key in fields:
            tk.Label(parent, text=label, font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", pady=(6, 0))

            var = tk.StringVar()
            AppEntry(parent, textvariable=var, width=28).pack(anchor="w", ipady=4)
            self._vars[key] = var

        tk.Label(parent, text="Category", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", pady=(6, 0))

        self.cat_combo = AppCombo(parent, values=cats, width=26)
        self.cat_combo.pack(anchor="w")

    def form_values(self):
        d = {k: v.get().strip() for k, v in self._vars.items()}

        cat_name = self.cat_combo.get()
        d["cat_id"] = self._cat_map.get(cat_name, None)

        try:
            d["price"] = float(d["price"])
        except:
            d["price"] = None

        if not d["expiry"]:
            d["expiry"] = None

        return d

    def populate_form(self, row):
        self._vars["name"].set(row[1] or "")
        self._vars["brand"].set(row[2] or "")
        self._vars["price"].set(str(row[3]) if row[3] else "")
        self._vars["expiry"].set("")
        self._vars["description"].set(row[6] if row[6] != "—" else "")
        self.cat_combo.set(row[4] if row[4] != "—" else "")

    def clear_form(self):
        for v in self._vars.values():
            v.set("")
        self.cat_combo.set("")