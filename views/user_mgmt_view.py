"""
views/user_mgmt_view.py
Admin-only: manage AppUser accounts (create, deactivate, reset password).
"""

import tkinter as tk
from tkinter import messagebox
from widgets import AppButton, DataTable, AppEntry, AppCombo, toast
from db.connection import fetch_all, execute, hash_password
from theme import *


class UserMgmtView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self._all_rows = []
        self._build()
        self.refresh()

    def _build(self):
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=PAD*2, pady=(PAD*2, PAD))
        tk.Label(top, text="User Accounts", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(side="left")
        AppButton(top, "＋ Add User",       command=self._add_user,      color=ACCENT).pack(side="right", padx=4)
        AppButton(top, "🔑 Reset Password", command=self._reset_password, color=ACCENT2).pack(side="right", padx=4)
        AppButton(top, "⏸ Toggle Active",   command=self._toggle_active,  color=WARNING).pack(side="right", padx=4)
        AppButton(top, "↻ Refresh",         command=self.refresh,         color=BG_CARD).pack(side="right", padx=4)

        cols = ["User ID", "Username", "Role", "Employee ID", "Customer ID", "Active"]
        self.table = DataTable(self, columns=cols)
        self.table.pack(fill="both", expand=True, padx=PAD*2, pady=(0, PAD*2))

    def refresh(self):
        sql = """
            SELECT UserID, Username, Role,
                   NVL(TO_CHAR(EmployeeID),'—'),
                   NVL(TO_CHAR(CustomerID),'—'),
                   CASE IsActive WHEN 1 THEN 'Yes' ELSE 'No' END
            FROM AppUser ORDER BY UserID
        """
        try:
            _, rows = fetch_all(sql)
            self._all_rows = rows
            self.table.load(rows)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _add_user(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add User")
        dlg.configure(bg=BG_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("380x550")

        tk.Label(dlg, text="New User Account", font=FONT_HEAD,
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(padx=PAD*2, pady=(PAD*2, 8), anchor="w")

        fields = {}
        for label, key, show in [
            ("Username",        "uname", ""),
            ("Password",        "pw",    "•"),
            ("Employee ID (optional)", "eid", ""),
            ("Customer ID (optional)", "cid", ""),
        ]:
            tk.Label(dlg, text=label, font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
            var = tk.StringVar()
            AppEntry(dlg, textvariable=var, width=32, show=show if show else "").pack(
                padx=PAD*2, anchor="w", ipady=4, pady=(2, 8))
            fields[key] = var

        tk.Label(dlg, text="Role", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
        role_combo = AppCombo(dlg, values=["admin", "employee", "customer"], width=30)
        role_combo.set("employee")
        role_combo.pack(padx=PAD*2, anchor="w", pady=(2, 12))

        err_var = tk.StringVar()
        tk.Label(dlg, textvariable=err_var, font=FONT_SMALL,
                 bg=BG_PANEL, fg=DANGER).pack(padx=PAD*2)

        def confirm():
            u = fields["uname"].get().strip()
            p = fields["pw"].get().strip()
            if not u or not p:
                err_var.set("Username and password required.")
                return
            eid = fields["eid"].get().strip() or None
            cid = fields["cid"].get().strip() or None
            try:
                eid = int(eid) if eid else None
                cid = int(cid) if cid else None
            except ValueError:
                err_var.set("Employee/Customer ID must be a number.")
                return
            hashed = hash_password(p)
            try:
                execute("""
                    INSERT INTO AppUser (Username, PasswordHash, Role, EmployeeID, CustomerID)
                    VALUES (:u, :pw, :role, :eid, :cid)
                """, {"u": u, "pw": hashed, "role": role_combo.get(), "eid": eid, "cid": cid})
                dlg.destroy()
                self.refresh()
                toast(self.winfo_toplevel(), f"User '{u}' created.")
            except Exception as e:
                err_var.set(str(e))

        AppButton(dlg, "Create User", command=confirm, color=ACCENT).pack(
            padx=PAD*2, fill="x", pady=8)

    def _reset_password(self):
        row = self.table.selected_values()
        if not row:
            messagebox.showwarning("Select", "Select a user.")
            return
        uid, uname = row[0], row[1]
        dlg = tk.Toplevel(self)
        dlg.title("Reset Password")
        dlg.configure(bg=BG_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("320x200")
        tk.Label(dlg, text=f"Reset password for: {uname}",
                 font=FONT_HEAD, bg=BG_PANEL, fg=TEXT_WHITE).pack(padx=PAD*2, pady=PAD)
        tk.Label(dlg, text="New Password", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=PAD*2, anchor="w")
        pw_var = tk.StringVar()
        AppEntry(dlg, textvariable=pw_var, show="•", width=28).pack(
            padx=PAD*2, anchor="w", ipady=4, pady=(2, 12))

        err_var = tk.StringVar()
        tk.Label(dlg, textvariable=err_var, font=FONT_SMALL,
                 bg=BG_PANEL, fg=DANGER).pack(padx=PAD*2)

        def save():
            p = pw_var.get().strip()
            if not p:
                err_var.set("Enter a new password.")
                return
            try:
                execute("UPDATE AppUser SET PasswordHash=:pw WHERE UserID=:id",
                        {"pw": hash_password(p), "id": uid})
                dlg.destroy()
                toast(self.winfo_toplevel(), "Password reset.")
            except Exception as e:
                err_var.set(str(e))

        AppButton(dlg, "Save", command=save, color=ACCENT).pack(padx=PAD*2, fill="x")

    def _toggle_active(self):
        row = self.table.selected_values()
        if not row:
            messagebox.showwarning("Select", "Select a user.")
            return
        uid   = row[0]
        uname = row[1]
        if uname == self.user["username"]:
            messagebox.showwarning("Cannot", "You cannot deactivate your own account.")
            return
        current = 1 if row[5] == "Yes" else 0
        new_val = 0 if current else 1
        label   = "deactivate" if current else "activate"
        if not messagebox.askyesno("Confirm", f"{label.capitalize()} user '{uname}'?"):
            return
        try:
            execute("UPDATE AppUser SET IsActive=:v WHERE UserID=:id",
                    {"v": new_val, "id": uid})
            self.refresh()
            toast(self.winfo_toplevel(), f"User {label}d.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
