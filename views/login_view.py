"""
views/login_view.py
Login screen — shown at startup.
"""

import tkinter as tk
from tkinter import messagebox
from widgets import AppButton, AppEntry
from theme import *
from db.connection import login


class LoginView(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=BG_DARK)
        self.on_login_success = on_login_success
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        # ── Left brand panel ─────────────────────────────
        left = tk.Frame(self, bg=BG_PANEL, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(left, bg=BG_PANEL).pack(expand=True)  # spacer
        tk.Label(left, text="🛒", font=("Segoe UI", 52),
                 bg=BG_PANEL, fg=ACCENT).pack(pady=(0, 10))
        tk.Label(left, text="FreshMart", font=(FONT_FAMILY, 26, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack()
        tk.Label(left, text="POS & Management System",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_DIM).pack(pady=(4, 0))
        tk.Frame(left, bg=BG_PANEL).pack(expand=True)  # spacer

        # version tag at bottom
        tk.Label(left, text="v1.0 · Student Project",
                 font=FONT_SMALL, bg=BG_PANEL, fg=BORDER).pack(pady=12)

        # ── Right login form ──────────────────────────────
        right = tk.Frame(self, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        center = tk.Frame(right, bg=BG_DARK)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Sign In", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 4))
        tk.Label(center, text="Enter your credentials to continue",
                 font=FONT_BODY, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0, 24))

        # Username
        tk.Label(center, text="Username", font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w")
        self.username_var = tk.StringVar()
        AppEntry(center, textvariable=self.username_var, width=30).pack(
            anchor="w", pady=(2, 12), ipady=6)

        # Password
        tk.Label(center, text="Password", font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w")
        self.password_var = tk.StringVar()
        AppEntry(center, textvariable=self.password_var, width=30,
                 show="•").pack(anchor="w", pady=(2, 24), ipady=6)

        # Error label
        self.error_var = tk.StringVar()
        tk.Label(center, textvariable=self.error_var, font=FONT_SMALL,
                 bg=BG_DARK, fg=DANGER).pack(anchor="w", pady=(0, 8))

        # Login button
        btn = AppButton(center, "Sign In →", command=self._attempt_login, color=ACCENT)
        btn.pack(fill="x", ipady=4)

        # Bind Enter key
        center.bind_all("<Return>", lambda e: self._attempt_login())

        # Hint
        tk.Label(center, text="Default admin: admin / admin123",
                 font=FONT_SMALL, bg=BG_DARK, fg=BORDER).pack(pady=(16, 0))

    def _attempt_login(self):
        u = self.username_var.get().strip()
        p = self.password_var.get().strip()
        if not u or not p:
            self.error_var.set("Please fill in both fields.")
            return
        try:
            user = login(u, p)
            if user:
                self.error_var.set("")
                self.destroy()
                self.on_login_success(user)
            else:
                self.error_var.set("Invalid username or password.")
        except RuntimeError as e:
            messagebox.showerror("DB Error", str(e))
