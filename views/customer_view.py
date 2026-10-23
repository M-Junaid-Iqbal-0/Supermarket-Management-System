"""
views/customer_view.py
Full CRUD for Customer table.
"""

import tkinter as tk
from views.crud_base import CrudBase
from widgets import AppEntry, Label
from theme import *


class CustomerView(CrudBase):
    TITLE      = "Customers"
    COLUMNS    = ["ID", "First Name", "Last Name", "Phone", "Email", "Address", "Registered"]
    SQL_SELECT = """
        SELECT CustomerID, FirstName, LastName, PhoneNumber,
               Email, Address, TO_CHAR(RegistrationDate,'DD-Mon-YYYY')
        FROM Customer ORDER BY CustomerID
    """
    SQL_INSERT = """
        INSERT INTO Customer (FirstName, LastName, PhoneNumber, Email, Address, RegistrationDate)
        VALUES (:fn, :ln, :phone, :email, :addr, SYSDATE)
    """
    SQL_UPDATE = """
        UPDATE Customer
        SET FirstName=:fn, LastName=:ln, PhoneNumber=:phone,
            Email=:email, Address=:addr
        WHERE CustomerID=:id
    """
    SQL_DELETE = "DELETE FROM Customer WHERE CustomerID=:id"
    ID_COLUMN  = 0

    def build_form(self, parent):
        fields = [
            ("First Name",  "fn"),
            ("Last Name",   "ln"),
            ("Phone",       "phone"),
            ("Email",       "email"),
            ("Address",     "addr"),
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
        keys = ["fn", "ln", "phone", "email", "addr"]
        for i, key in enumerate(keys):
            self._vars[key].set(row[i + 1] if row[i + 1] else "")

    def clear_form(self):
        for v in self._vars.values():
            v.set("")
