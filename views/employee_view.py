"""
views/employee_view.py
Full CRUD for Employee table (admin only).
"""

import tkinter as tk
from views.crud_base import CrudBase
from widgets import AppEntry
from theme import *


class EmployeeView(CrudBase):
    TITLE      = "Employees"
    COLUMNS    = ["ID", "First Name", "Last Name", "Position", "Phone", "Email", "Salary", "Hired"]
    SQL_SELECT = """
        SELECT EmployeeID, FirstName, LastName, Position,
               PhoneNumber, Email, Salary,
               TO_CHAR(HireDate,'DD-Mon-YYYY')
        FROM Employee ORDER BY EmployeeID
    """
    SQL_INSERT = """
        INSERT INTO Employee (FirstName, LastName, Position, PhoneNumber, Email, Salary, HireDate)
        VALUES (:fn, :ln, :pos, :phone, :email, :salary, SYSDATE)
    """
    SQL_UPDATE = """
        UPDATE Employee
        SET FirstName=:fn, LastName=:ln, Position=:pos,
            PhoneNumber=:phone, Email=:email, Salary=:salary
        WHERE EmployeeID=:id
    """
    SQL_DELETE = "DELETE FROM Employee WHERE EmployeeID=:id"
    ID_COLUMN  = 0

    def build_form(self, parent):
        fields = [
            ("First Name", "fn"),
            ("Last Name",  "ln"),
            ("Position",   "pos"),
            ("Phone",      "phone"),
            ("Email",      "email"),
            ("Salary",     "salary"),
        ]
        self._vars = {}
        for label, key in fields:
            tk.Label(parent, text=label, font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", pady=(6, 0))
            var = tk.StringVar()
            AppEntry(parent, textvariable=var, width=28).pack(anchor="w", ipady=4)
            self._vars[key] = var

    def form_values(self):
        d = {k: v.get().strip() for k, v in self._vars.items()}
        try:
            d["salary"] = float(d["salary"]) if d["salary"] else None
        except ValueError:
            d["salary"] = None
        return d

    def populate_form(self, row):
        keys = ["fn", "ln", "pos", "phone", "email", "salary"]
        for i, key in enumerate(keys):
            self._vars[key].set(str(row[i + 1]) if row[i + 1] is not None else "")

    def clear_form(self):
        for v in self._vars.values():
            v.set("")
