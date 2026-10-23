"""
views/sale_history_view.py
Archived/completed sales. Admin can delete. Customers see only their own.
"""

import tkinter as tk
from tkinter import messagebox
from widgets import AppButton, DataTable, toast
from db.connection import fetch_all, execute
from theme import *


class SaleHistoryView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._all_rows = []
        self._build()
        self.refresh()

    def _build(self):
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=PAD*2, pady=(PAD*2, PAD))
        tk.Label(top, text="Sale History", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")
        AppButton(top, "↻ Refresh", command=self.refresh, color=BG_CARD).pack(side="right", padx=4)
        if self.user["role"] == "admin":
            AppButton(top, "🗑 Delete Record", command=self._delete,
                      color=DANGER).pack(side="right", padx=4)

        # Search
        sbar = tk.Frame(self, bg=BG_DARK)
        sbar.pack(fill="x", padx=PAD*2, pady=(0, PAD))
        tk.Label(sbar, text="Search:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        tk.Entry(sbar, textvariable=self.search_var, font=FONT_BODY,
                 bg=BG_CARD, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
                 relief="flat", highlightthickness=1,
                 highlightbackground=BORDER, width=30).pack(
                     side="left", padx=8, ipady=4)

        cols = ["History ID", "Orig Sale ID", "Customer", "Employee",
                "Sale Date", "Total (PKR)", "Payment", "Amount Paid", "Archived At"]
        self.table = DataTable(self, columns=cols)
        self.table.pack(fill="both", expand=True, padx=PAD*2, pady=(0, PAD*2))

        self.table.tree.bind("<Double-1>", self._show_sale_details)

    def refresh(self):
        sql = """
            SELECT h.HistoryID, h.OrigSaleID,
                   NVL(c.FirstName||' '||c.LastName,'Walk-in'),
                   NVL(e.FirstName||' '||e.LastName,'—'),
                   TO_CHAR(h.SaleDate,'DD-Mon-YYYY HH24:MI'),
                   h.TotalAmount, NVL(h.PaymentMethod,'—'),
                   h.AmountPaid,
                   TO_CHAR(h.ArchivedAt,'DD-Mon-YYYY HH24:MI')
            FROM Sale_History h
            LEFT JOIN Customer c ON h.CustomerID = c.CustomerID
            LEFT JOIN Employee e ON h.EmployeeID = e.EmployeeID
        """
        # Customers only see their own history
        if self.user["role"] == "customer" and self.user.get("customer_id"):
            sql += " WHERE h.CustomerID = :cid ORDER BY h.ArchivedAt DESC"
            params = {"cid": self.user["customer_id"]}
        else:
            sql += " ORDER BY h.ArchivedAt DESC"
            params = {}
        try:
            _, rows = fetch_all(sql, params)
            self._all_rows = rows
            self.table.load(rows)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _filter(self):
        q = self.search_var.get().lower()
        if not q:
            self.table.load(self._all_rows)
            return
        self.table.load([r for r in self._all_rows
                         if any(q in str(v).lower() for v in r)])


    def _delete(self):
        row = self.table.selected_values()

        if not row:
            messagebox.showwarning(
                "Select",
                "Select a record to delete."
            )
            return

        if not messagebox.askyesno(
            "Delete",
            f"Permanently delete history record #{row[0]}?"
        ):
            return

        try:
            # delete items first
            execute(
                """
                DELETE FROM Sale_History_Item
                WHERE HISTORYID=:id
                """,
                {"id": row[0]}
            )

            # delete header
            execute(
                """
                DELETE FROM Sale_History
                WHERE HISTORYID=:id
                """,
                {"id": row[0]}
            )

            self.refresh()

            toast(
                self.winfo_toplevel(),
                "Record deleted.",
                success=False
            )

        except Exception as e:
            import traceback
            traceback.print_exc()

            messagebox.showerror(
                "Error",
                str(e)
            )


    def _show_sale_details(self, event=None):

        row = self.table.selected_values()


        if not row:
    
            return

    
    
        history_id = row[0]
    
        orig_sale_id = row[1]

        dlg = tk.Toplevel(self)
        dlg.title(f"Sale #{orig_sale_id} Details")
        dlg.geometry("850x550")
        dlg.configure(bg=BG_PANEL)

        # Header
        tk.Label(
            dlg,
            text=f"Sale #{orig_sale_id}",
            font=FONT_HEAD,
            bg=BG_PANEL,
            fg=TEXT_WHITE
        ).pack(anchor="w", padx=15, pady=(15, 5))

        info_frame = tk.Frame(dlg, bg=BG_PANEL)
        info_frame.pack(fill="x", padx=15)

        details = (
            f"Customer: {row[2]}\n"
            f"Employee: {row[3]}\n"
            f"Sale Date: {row[4]}\n"
            f"Total Amount: PKR {row[5]}\n"
            f"Payment Method: {row[6]}\n"
            f"Amount Paid: PKR {row[7]}\n"
            f"Archived At: {row[8]}"
        )
    
        tk.Label(
            info_frame,
            text=details,
            justify="left",
            bg=BG_PANEL,
            fg=TEXT_DIM,
            font=FONT_BODY
        ).pack(anchor="w")

        tk.Frame(dlg, bg=BORDER, height=1).pack(fill="x", padx=15, pady=10)

        tk.Label(
            dlg,
            text="Products Purchased",
            font=FONT_SMALL,
            bg=BG_PANEL,
            fg=ACCENT2
        ).pack(anchor="w", padx=15)

        item_cols = ["Product", "Quantity", "Unit Price", "Subtotal"]

        item_table = DataTable(dlg, columns=item_cols)
        item_table.pack(fill="both", expand=True, padx=15, pady=10)

        try:
            _, rows = fetch_all("""
                SELECT
                    p.ProductName,
                    shi.Quantity,
                    shi.UnitPrice,
                    shi.Subtotal
                FROM Sale_History_Item shi
                JOIN Product p
                    ON p.ProductID = shi.ProductID
                WHERE shi.HISTORYID = :hid
            """, {"hid": history_id})

            item_table.load(rows)

        except Exception as e:
            import traceback
            traceback.print_exc()

            messagebox.showerror(
                "Error",
                str(e)
            )