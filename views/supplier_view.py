"""
views/supplier_view.py
Full CRUD for Supplier table.
"""

import tkinter as tk
from views.crud_base import CrudBase
from widgets import AppEntry
from theme import *


class SupplierView(CrudBase):
    TITLE      = "Suppliers"
    COLUMNS    = ["ID", "Supplier Name", "Contact Person", "Phone", "Email", "Address"]
    SQL_SELECT = """
        SELECT SupplierID, SupplierName, ContactPerson,
               PhoneNumber, Email, Address
        FROM Supplier ORDER BY SupplierID
    """
    SQL_INSERT = """
        INSERT INTO Supplier (SupplierName, ContactPerson, PhoneNumber, Email, Address)
        VALUES (:name, :contact, :phone, :email, :addr)
    """
    SQL_UPDATE = """
        UPDATE Supplier
        SET SupplierName=:name, ContactPerson=:contact,
            PhoneNumber=:phone, Email=:email, Address=:addr
        WHERE SupplierID=:id
    """
    SQL_DELETE = "DELETE FROM Supplier WHERE SupplierID=:id"
    ID_COLUMN  = 0

    def build_form(self, parent):
        fields = [
            ("Supplier Name",   "name"),
            ("Contact Person",  "contact"),
            ("Phone",           "phone"),
            ("Email",           "email"),
            ("Address",         "addr"),
        ]
        self._vars = {}
        for label, key in fields:
            tk.Label(parent, text=label, font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", pady=(6, 0))
            var = tk.StringVar()
            AppEntry(parent, textvariable=var, width=28).pack(anchor="w", ipady=4)
            self._vars[key] = var

    def form_values(self):
        return {k: v.get().strip() for k, v in self._vars.items()}

    def populate_form(self, row):
        keys = ["name", "contact", "phone", "email", "addr"]
        for i, key in enumerate(keys):
            self._vars[key].set(row[i + 1] if row[i + 1] else "")

    def clear_form(self):
        for v in self._vars.values():
            v.set("")
