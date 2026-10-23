"""
views/category_view.py
Full CRUD for Category table.
"""

import tkinter as tk
from views.crud_base import CrudBase
from widgets import AppEntry
from theme import *


class CategoryView(CrudBase):
    TITLE = "Categories"

    COLUMNS = ["ID", "Category Name", "Description"]

    SQL_SELECT = """
        SELECT CategoryID,
               CategoryName,
               NVL(Description, '—')
        FROM Category
        ORDER BY CategoryID
    """

    SQL_INSERT = """
        INSERT INTO Category (
            CategoryName,
            Description
        )
        VALUES (
            :name,
            :description
        )
    """

    SQL_UPDATE = """
        UPDATE Category
        SET CategoryName = :name,
            Description  = :description
        WHERE CategoryID = :id
    """

    SQL_DELETE = """
        DELETE FROM Category
        WHERE CategoryID = :id
    """

    ID_COLUMN = 0

    def build_form(self, parent):
        self._vars = {}

        fields = [
            ("Category Name", "name"),
            ("Description", "description")
        ]

        for label, key in fields:
            tk.Label(
                parent,
                text=label,
                font=FONT_SMALL,
                bg=BG_PANEL,
                fg=TEXT_DIM
            ).pack(anchor="w", pady=(6, 0))

            var = tk.StringVar()

            AppEntry(
                parent,
                textvariable=var,
                width=28
            ).pack(anchor="w", ipady=4)

            self._vars[key] = var

    def form_values(self):
        return {
            key: var.get().strip()
            for key, var in self._vars.items()
        }

    def populate_form(self, row):
        self._vars["name"].set(row[1] or "")
        self._vars["description"].set(
            row[2] if row[2] != "—" else ""
        )

    def clear_form(self):
        for var in self._vars.values():
            var.set("")