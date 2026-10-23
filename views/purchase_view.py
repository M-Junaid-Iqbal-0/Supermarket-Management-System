"""
views/purchase_view.py
Purchase Orders — create and view orders from suppliers.
"""

import tkinter as tk
from tkinter import messagebox
from widgets import AppButton, DataTable, AppEntry, AppCombo, toast
from db.connection import fetch_all, execute, get_connection
from theme import *


class PurchaseView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._all_rows = []
        self._build()
        self.refresh()

    def _build(self):
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=PAD*2, pady=(PAD*2, PAD))
        tk.Label(top, text="Purchase Orders", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")
        AppButton(top, "＋ New Order", command=self._new_order, color=ACCENT).pack(side="right", padx=4)
        AppButton(top, "↻ Refresh",   command=self.refresh,    color=BG_CARD).pack(side="right", padx=4)

        # Status filter
        sbar = tk.Frame(self, bg=BG_DARK)
        sbar.pack(fill="x", padx=PAD*2, pady=(0, PAD))
        tk.Label(sbar, text="Filter Status:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        self.status_var = tk.StringVar(value="All")
        AppCombo(sbar, values=["All", "Pending", "Received", "Cancelled"],
                 textvariable=self.status_var, width=14).pack(side="left", padx=6)
        tk.Button(sbar, text="Apply", font=FONT_SMALL,
                  bg=ACCENT2, fg=TEXT_WHITE, relief="flat",
                  command=self._filter_status, cursor="hand2", padx=8, pady=2).pack(side="left")

        # Update status
        AppButton(sbar, "Update Status", command=self._update_status,
                  color=WARNING).pack(side="right", padx=4)

        cols = ["PO ID", "Supplier", "Employee", "Order Date", "Total Cost", "Status"]
        self.table = DataTable(self, columns=cols)
        self.table.pack(fill="both", expand=True, padx=PAD*2, pady=(0, PAD*2))

    def refresh(self):
        sql = """
            SELECT po.PurchaseOrderID,
                   s.SupplierName,
                   e.FirstName||' '||e.LastName,
                   TO_CHAR(po.OrderDate,'DD-Mon-YYYY'),
                   NVL(po.TotalCost,0),
                   NVL(po.OrderStatus,'Pending')
            FROM Purchase_Order po
            JOIN Supplier s  ON po.SupplierID = s.SupplierID
            JOIN Employee e  ON po.EmployeeID = e.EmployeeID
            ORDER BY po.PurchaseOrderID DESC
        """
        try:
            _, rows = fetch_all(sql)
            self._all_rows = rows
            self.table.load(rows)
            self._color_rows()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _color_rows(self):
        for item in self.table.tree.get_children():
            vals = self.table.tree.item(item)["values"]
            status = str(vals[5]).lower()
            if status == "received":
                self.table.tree.item(item, tags=("received",))
            elif status == "cancelled":
                self.table.tree.item(item, tags=("cancelled",))
            else:
                self.table.tree.item(item, tags=("pending",))
        self.table.tree.tag_configure("received",  foreground=ACCENT)
        self.table.tree.tag_configure("cancelled", foreground=DANGER)
        self.table.tree.tag_configure("pending",   foreground=WARNING)

    def _filter_status(self):
        status = self.status_var.get()
        if status == "All":
            self.table.load(self._all_rows)
        else:
            self.table.load([r for r in self._all_rows
                             if str(r[5]).lower() == status.lower()])
        self._color_rows()

    def _update_status(self):
        row = self.table.selected_values()
        if not row:
            messagebox.showwarning("Select", "Select a purchase order.")
            return
        po_id = row[0]
        dlg = tk.Toplevel(self)
        dlg.title("Update Status")
        dlg.configure(bg=BG_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("280x160")
        tk.Label(dlg, text=f"PO #{po_id} — Set Status",
                 font=FONT_HEAD, bg=BG_PANEL, fg=TEXT_WHITE).pack(padx=PAD*2, pady=PAD)
        status_combo = AppCombo(dlg, values=["Pending", "Received", "Cancelled"], width=22)
        status_combo.set(row[5])
        status_combo.pack(padx=PAD*2)

        def save():
            try:
                execute(
                    "UPDATE Purchase_Order SET OrderStatus=:s WHERE PurchaseOrderID=:id",
                    {"s": status_combo.get(), "id": po_id})
                dlg.destroy()
                self.refresh()
                toast(self.winfo_toplevel(), "Status updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        AppButton(dlg, "Save", command=save, color=ACCENT).pack(padx=PAD*2, pady=12, fill="x")

    def _new_order(self):
        dlg = tk.Toplevel(self)
        dlg.title("New Purchase Order")
        dlg.configure(bg=BG_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("380x300")

        tk.Label(dlg, text="New Purchase Order", font=FONT_HEAD,
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(padx=PAD*2, pady=(PAD*2, 8), anchor="w")

        try:
            _, srows = fetch_all("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
            sup_map = {f"{r[1]} (#{r[0]})": r[0] for r in srows}
        except Exception:
            sup_map = {}
        try:
            _, erows = fetch_all(
                "SELECT EmployeeID, FirstName||' '||LastName FROM Employee ORDER BY FirstName")
            emp_map = {f"{r[1]} (#{r[0]})": r[0] for r in erows}
        except Exception:
            emp_map = {}

        for label, combo_map in [("Supplier", sup_map), ("Employee", emp_map)]:
            tk.Label(dlg, text=label, font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
            cb = AppCombo(dlg, values=list(combo_map.keys()), width=36)
            cb.pack(padx=PAD*2, anchor="w", pady=(2, 8))
            if label == "Supplier":
                sup_combo = cb
            else:
                emp_combo = cb

        tk.Label(dlg, text="Total Cost (PKR)", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
        cost_var = tk.StringVar()
        AppEntry(dlg, textvariable=cost_var, width=20).pack(
            padx=PAD*2, anchor="w", ipady=4, pady=(2, 12))

        err_var = tk.StringVar()
        tk.Label(dlg, textvariable=err_var, font=FONT_SMALL,
                 bg=BG_PANEL, fg=DANGER).pack(padx=PAD*2)

        def confirm():
            sup_id = sup_map.get(sup_combo.get())
            emp_id = emp_map.get(emp_combo.get())
            if not sup_id or not emp_id:
                err_var.set("Select both a supplier and an employee.")
                return
            try:
                cost = float(cost_var.get()) if cost_var.get() else 0
            except ValueError:
                err_var.set("Cost must be a number.")
                return
            try:
                execute("""
                    INSERT INTO Purchase_Order
                        (SupplierID, EmployeeID, OrderDate, TotalCost, OrderStatus)
                    VALUES (:sid, :eid, SYSDATE, :cost, 'Pending')
                """, {"sid": sup_id, "eid": emp_id, "cost": cost})
                dlg.destroy()
                self.refresh()
                toast(self.winfo_toplevel(), "Purchase order created.")
            except Exception as e:
                err_var.set(str(e))

        AppButton(dlg, "Create Order", command=confirm, color=ACCENT).pack(
            padx=PAD*2, fill="x", pady=8)
