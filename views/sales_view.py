"""
views/sales_view.py
Active sales management.
- Create new sale
- Add items to sale
- Close sale → archives to Sale_History, removes from Sale
"""

import tkinter as tk
from tkinter import messagebox, ttk
from widgets import AppButton, DataTable, AppEntry, AppCombo, toast
from db.connection import fetch_all, execute, get_connection
from theme import *


class SalesView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._build()
        self._load_sales()

    def _build(self):
        print("BUILD CALLED", id(self))
        # Header
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=PAD*2, pady=(PAD*2, PAD))
        tk.Label(top, text="Active Sales", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")
        AppButton(top, "＋ New Sale",   command=self._new_sale,   color=ACCENT).pack(side="right", padx=4)
        AppButton(top, "✔ Close Sale",  command=self._close_sale, color=WARNING).pack(side="right", padx=4)
        AppButton(top, "↻ Refresh",     command=self._load_sales, color=BG_CARD).pack(side="right", padx=4)

        # Pane: left = sale list, right = sale detail
        pane = tk.Frame(self, bg=BG_DARK)
        pane.pack(fill="both", expand=True, padx=PAD*2, pady=(0, PAD))

        # ── Sale list ────────────────────────────────────
        left = tk.Frame(pane, bg=BG_DARK)
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="Current Sales", font=FONT_HEAD,
                 bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0, 4))

        sale_cols = ["Sale ID", "Customer", "Employee", "Date", "Total (PKR)"]
        self.sale_table = DataTable(left, columns=sale_cols)
        self.sale_table.pack(fill="both", expand=True)
        self.sale_table.tree.bind("<<TreeviewSelect>>", self._on_sale_select)

        # ── Sale detail ───────────────────────────────────
        right = tk.Frame(pane, bg=BG_PANEL, width=380, padx=PAD, pady=PAD)
        right.pack(side="left", fill="y", padx=(PAD, 0))
        right.pack_propagate(False)

        tk.Label(right, text="Sale Detail", font=FONT_HEAD,
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 8))

        # Sale info
        info = tk.Frame(right, bg=BG_PANEL)
        info.pack(fill="x", pady=(0, 8))
        self.sale_info_var = tk.StringVar(value="No sale selected.")
        tk.Label(info, textvariable=self.sale_info_var, font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM, justify="left").pack(anchor="w")

        # Items table
        tk.Label(right, text="Items", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        item_cols = ["Item ID", "Product", "Qty", "Unit Price", "Subtotal"]
        self.item_table = DataTable(right, columns=item_cols)
        self.item_table.pack(fill="both", expand=True, pady=(4, 8))

        # Add item section
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=4)
        tk.Label(right, text="Add Item to Sale", font=FONT_SMALL,
                 bg=BG_PANEL, fg=ACCENT2).pack(anchor="w", pady=(4, 4))

        self._selected_sale_id = None
        self._product_map = {}   # display_name -> (product_id, unit_price)

        # Product dropdown
        tk.Label(right, text="Product", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.prod_var = tk.StringVar()
        self.prod_combo = AppCombo(right, values=[], width=30)
        self.prod_combo.pack(anchor="w", pady=(2, 6))
        self.prod_combo.bind("<<ComboboxSelected>>", self._on_product_select)
        self._load_products()

        row_qty = tk.Frame(right, bg=BG_PANEL)
        row_qty.pack(fill="x")
        tk.Label(row_qty, text="Qty", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side="left")
        self.add_qty_var = tk.StringVar(value="1")
        AppEntry(row_qty, textvariable=self.add_qty_var, width=6).pack(
            side="left", padx=(4, 12), ipady=3)
        tk.Label(row_qty, text="Price", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(side="left")
        self.add_price_var = tk.StringVar()
        AppEntry(row_qty, textvariable=self.add_price_var, width=8).pack(
            side="left", padx=4, ipady=3)

        AppButton(right, "Add Item", command=self._add_item, color=ACCENT2).pack(
            fill="x", pady=(8, 4))
        AppButton(right, "Remove Selected Item", command=self._remove_item, color=DANGER).pack(fill="x")



    # ── Products ──────────────────────────────────────────

    def _load_products(self):
        print("LOAD PRODUCTS", id(self))
        try:
            print("Loading products...")

            _, rows = fetch_all("""
                SELECT ProductID,
                       ProductName,
                       UnitPrice
                FROM Product
                ORDER BY ProductName
            """)

            print("ROWS:", rows)

            self._product_map = {
                f"{r[1]} (#{r[0]})": (r[0], r[2])
                for r in rows
            }

            print("PRODUCT MAP:", self._product_map)

            self.prod_combo["values"] = list(self._product_map.keys())

            print("COMBO VALUES SET")

        except Exception as e:
            import traceback
            traceback.print_exc()

            print("LOAD PRODUCTS ERROR:", e)

            messagebox.showerror(
                "Product Load Error",
                str(e)
            )
        print("LOAD SELF ID:", id(self))
        print("LOAD MAP ID:", id(self._product_map))



    def _on_product_select(self, _=None):
        key = self.prod_combo.get()

        print("SELECTED:", repr(key))

        if key in self._product_map:
            self.add_price_var.set(
                str(self._product_map[key][1])
            )
    # ── Sales list ────────────────────────────────────────
    def _load_sales(self):
        sql = """
            SELECT s.SaleID,
                   NVL(c.FirstName||' '||c.LastName,'Walk-in'),
                   NVL(e.FirstName||' '||e.LastName,'—'),
                   TO_CHAR(s.SaleDate,'DD-Mon-YYYY HH24:MI'),
                   s.TotalAmount
            FROM Sale s
            LEFT JOIN Customer c ON s.CustomerID = c.CustomerID
            LEFT JOIN Employee e ON s.EmployeeID = e.EmployeeID
            ORDER BY s.SaleDate DESC
        """
        try:
            _, rows = fetch_all(sql)
            self.sale_table.load(rows)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _on_sale_select(self, _=None):
        row = self.sale_table.selected_values()
        if not row:
            return
        self._selected_sale_id = row[0]
        self.sale_info_var.set(
            f"Sale #{row[0]}  |  {row[1]}  |  Total: PKR {row[4]}")
        self._load_sale_items(row[0])

    def _load_sale_items(self, sale_id):
        sql = """
            SELECT si.SaleItemID, p.ProductName, si.Quantity,
                   si.UnitPrice, si.Subtotal
            FROM Sale_Item si
            JOIN Product p ON si.ProductID = p.ProductID
            WHERE si.SaleID = :sid
        """
        try:
            _, rows = fetch_all(sql, {"sid": sale_id})
            self.item_table.load(rows)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ── New sale dialog ───────────────────────────────────
    def _new_sale(self):
        dlg = tk.Toplevel(self)
        dlg.title("New Sale")
        dlg.configure(bg=BG_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("380x340")

        tk.Label(dlg, text="New Sale", font=FONT_HEAD,
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(padx=PAD*2, pady=(PAD*2, 8), anchor="w")

        # Customer
        try:
            _, crows = fetch_all(
                "SELECT CustomerID, FirstName||' '||LastName FROM Customer ORDER BY FirstName")
            cust_map = {f"{r[1]} (#{r[0]})": r[0] for r in crows}
            cust_map["Walk-in (no account)"] = None
        except Exception:
            cust_map = {"Walk-in (no account)": None}

        tk.Label(dlg, text="Customer", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
        cust_combo = AppCombo(dlg, values=list(cust_map.keys()), width=36)
        cust_combo.set("Walk-in (no account)")
        cust_combo.pack(padx=PAD*2, anchor="w", pady=(2, 10))

        # Employee
        try:
            _, erows = fetch_all(
                "SELECT EmployeeID, FirstName||' '||LastName FROM Employee ORDER BY FirstName")
            emp_map = {f"{r[1]} (#{r[0]})": r[0] for r in erows}
        except Exception:
            emp_map = {}

        tk.Label(dlg, text="Employee (cashier)", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
        emp_combo = AppCombo(dlg, values=list(emp_map.keys()), width=36)
        emp_combo.pack(padx=PAD*2, anchor="w", pady=(2, 10))

        # Payment method
        tk.Label(dlg, text="Payment Method", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
        pay_combo = AppCombo(dlg, values=["Cash", "Card", "Online Transfer", "Other"], width=36)
        pay_combo.set("Cash")
        pay_combo.pack(padx=PAD*2, anchor="w", pady=(2, 16))

        err_var = tk.StringVar()
        tk.Label(dlg, textvariable=err_var, font=FONT_SMALL,
                 bg=BG_PANEL, fg=DANGER).pack(padx=PAD*2)

        def confirm():
            cust_id = cust_map.get(cust_combo.get())
            emp_id  = emp_map.get(emp_combo.get())
            paymethod = pay_combo.get()

            con = get_connection()
            cur = con.cursor()
            try:
                # Insert Sale
                out_id = cur.var(int)
                cur.execute("""
                    INSERT INTO Sale (CustomerID, EmployeeID, SaleDate, TotalAmount)
                    VALUES (:cid, :eid, SYSTIMESTAMP, 0)
                    RETURNING SaleID INTO :sid
                """, cid=cust_id, eid=emp_id, sid=out_id)
                new_sale_id = out_id.getvalue()[0]

                # Insert Payment placeholder
                cur.execute("""
                    INSERT INTO Payment (SaleID, PaymentMethod, AmountPaid, PaymentDate)
                    VALUES (:sid, :pm, 0, SYSTIMESTAMP)
                """, sid=new_sale_id, pm=paymethod)

                con.commit()
                dlg.destroy()
                self._load_sales()
                toast(self.winfo_toplevel(), f"Sale #{new_sale_id} created.")
            except Exception as e:
                con.rollback()
                err_var.set(str(e))
            finally:
                cur.close()
                con.close()

        AppButton(dlg, "Create Sale", command=confirm, color=ACCENT).pack(
            padx=PAD*2, fill="x", pady=8)

    # ── Add item ──────────────────────────────────────────


    def _add_item(self):
        if not self._selected_sale_id:
            messagebox.showwarning("Select", "Select a sale first.")
            return

        # Use StringVar instead of combo.get()
        prod_key = self.prod_combo.get()

        print("PRODUCT SELECTED:", repr(prod_key))
        print("PRODUCT MAP:", self._product_map)

        if not prod_key:
            messagebox.showwarning(
                "Select",
                "No product selected from dropdown."
            )
            return

        if prod_key not in self._product_map:
            messagebox.showwarning(
                "Select",
                f"Product not found:\n{repr(prod_key)}"
            )
            return

        try:
            qty = int(self.add_qty_var.get())
            price = float(self.add_price_var.get())
        except ValueError:
            messagebox.showerror(
                "Input",
                "Quantity and price must be numbers."
            )
            return

        prod_id, _ = self._product_map[prod_key]
        subtotal = qty * price
        sid = self._selected_sale_id

        print("SALE ID:", sid)
        print("PRODUCT ID:", prod_id)
        print("QTY:", qty)
        print("PRICE:", price)
        print("SUBTOTAL:", subtotal)

        con = get_connection()
        cur = con.cursor()

        try:
            cur.execute("""
                INSERT INTO Sale_Item
                (SaleID, ProductID, Quantity, UnitPrice, Subtotal)
                VALUES
                (:sid, :pid, :qty, :price, :sub)
            """,
            sid=sid,
            pid=prod_id,
            qty=qty,
            price=price,
            sub=subtotal)

            print("INSERT SUCCESS")

            cur.execute("""
                UPDATE Sale
                SET TotalAmount = (
                    SELECT NVL(SUM(Subtotal), 0)
                    FROM Sale_Item
                    WHERE SaleID = :sid
                )
                WHERE SaleID = :sid
            """, sid=sid)

            cur.execute("""
                UPDATE Payment
                SET AmountPaid = (
                    SELECT NVL(SUM(Subtotal), 0)
                    FROM Sale_Item
                    WHERE SaleID = :sid
                )
                WHERE SaleID = :sid
            """, sid=sid)

            con.commit()

            self._load_sale_items(sid)
            self._load_sales()

            toast(self.winfo_toplevel(), "Item added.")

        except Exception as e:
            import traceback
            traceback.print_exc()

            con.rollback()

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            cur.close()
            con.close()

    def _remove_item(self):
        row = self.item_table.selected_values()
        if not row:
            messagebox.showwarning("Select", "Select an item to remove.")
            return
        item_id = row[0]
        sid     = self._selected_sale_id
        qty     = row[2]
        con = get_connection()
        cur = con.cursor()
        try:
            # Restore inventory
            cur.execute("""
                UPDATE Inventory SET QuantityInStock = QuantityInStock + :qty,
                       LastUpdated = SYSTIMESTAMP
                WHERE ProductID = (SELECT ProductID FROM Sale_Item WHERE SaleItemID=:iid)
            """, qty=qty, iid=item_id)
            cur.execute("DELETE FROM Sale_Item WHERE SaleItemID=:iid", iid=item_id)
            cur.execute("""
                UPDATE Sale SET TotalAmount=(
                    SELECT NVL(SUM(Subtotal),0) FROM Sale_Item WHERE SaleID=:sid
                ) WHERE SaleID=:sid2
            """, sid=sid, sid2=sid)
            cur.execute("""
                UPDATE Payment SET AmountPaid=(
                    SELECT NVL(SUM(Subtotal),0) FROM Sale_Item WHERE SaleID=:sid
                ) WHERE SaleID=:sid2
            """, sid=sid, sid2=sid)
            con.commit()
            self._load_sale_items(sid)
            self._load_sales()
            toast(self.winfo_toplevel(), "Item removed.", success=False)
        except Exception as e:
            con.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            con.close()

    # ── Close / archive sale ──────────────────────────────
    def _close_sale(self):
        if not self._selected_sale_id:
            messagebox.showwarning("Select", "Select a sale to close.")
            return
        sid = self._selected_sale_id
        if not messagebox.askyesno("Close Sale",
                f"Archive Sale #{sid} and remove from active sales?"):
            return
        con = get_connection()
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO Sale_History
                    (OrigSaleID, CustomerID, EmployeeID, SaleDate,
                     TotalAmount, PaymentMethod, AmountPaid)
                SELECT s.SaleID, s.CustomerID, s.EmployeeID, s.SaleDate,
                       s.TotalAmount, p.PaymentMethod, p.AmountPaid
                FROM Sale s
                LEFT JOIN Payment p ON s.SaleID = p.SaleID
                WHERE s.SaleID = :sid
            """, sid=sid)

            # Get generated history ID
            cur.execute("""
                SELECT HISTORYID
                FROM Sale_History
                WHERE ORIGSALEID = :sid
            """, sid=sid)

            row = cur.fetchone()

            if row is None:
                raise Exception("History record not found")

            history_id = row[0]

            # Copy sale items into history
            cur.execute("""
                INSERT INTO Sale_History_Item
                (
                    HISTORYID,
                    ORIGSALEID,
                    PRODUCTID,
                    QUANTITY,
                    UNITPRICE,
                    SUBTOTAL
                )
                SELECT
                    :hid,
                    SaleID,
                    ProductID,
                    Quantity,
                    UnitPrice,
                    Subtotal
                FROM Sale_Item
                WHERE SaleID = :sid
            """,
            hid=history_id,
            sid=sid)

            print("SALE ITEMS COPIED TO HISTORY SUCCESSFULLY")

            # Delete sale items first
            cur.execute("""
                DELETE FROM Sale_Item
                WHERE SaleID = :sid
            """, {"sid": sid})

            print("SALE ITEMS DELETED")

            # Delete payment record
            cur.execute("""
                DELETE FROM Payment
                WHERE SaleID = :sid
            """, {"sid": sid})

            print("PAYMENT DELETED")

            # Delete active sale
            cur.execute("""
                DELETE FROM Sale
                WHERE SaleID = :sid
            """, {"sid": sid})

            print("ACTIVE SALE DELETED")

            con.commit()

            print("ARCHIVE COMPLETE")

        except Exception as e:
            import traceback
            traceback.print_exc()

            print("DELETE SALE ERROR:", e)

            try:
                con.rollback()
            except Exception:
                pass

            messagebox.showerror(
                "Delete Error",
                str(e)
            )
        except Exception as e:
            import traceback
            traceback.print_exc()

            print("COPY SALE ITEMS TO HISTORY ERROR:", e)

            messagebox.showerror(
                "History Save Error",
                str(e)
            )
        
            cur.execute("DELETE FROM Sale WHERE SaleID=:sid", sid=sid)
            cur.execute("SELECT COUNT(*) FROM Sale WHERE SaleID = :sid", {"sid": sid},); print("SALE STILL EXISTS:", cur.fetchone()[0])
            con.commit()
            print("ARCHIVED SALE ID:", sid)

            cur.execute("""
    SELECT *
    FROM Sale_History
    WHERE OrigSaleID = :sid
            """, {"sid": sid})

            print("HISTORY CHECK:", cur.fetchall())
            self._selected_sale_id = None
            self.sale_info_var.set("No sale selected.")
            self.item_table.load([])
            self._load_sales()
            toast(self.winfo_toplevel(), f"Sale #{sid} archived.")
        except Exception as e:
            con.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            con.close()
