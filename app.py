"""
app.py
Application entry point.
Run with: python app.py
"""

import tkinter as tk
from tkinter import messagebox
from config import APP_TITLE, APP_VERSION
from theme import BG_DARK, FONT_FAMILY
from db.connection import test_connection


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.configure(bg=BG_DARK)
        self.geometry("1200x720")
        self.minsize(900, 600)

        # Center on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 1200) // 2
        y = (sh - 720)  // 2
        self.geometry(f"1200x720+{x}+{y}")

        # Check DB before showing UI
        ok, err = test_connection()
        if not ok:
            messagebox.showerror(
                "Database Connection Failed",
                f"Could not connect to Oracle DB.\n\n{err}\n\n"
                "Check your credentials in config.py and make sure Oracle is running."
            )
            self.destroy()
            return

        self._show_login()

    def _show_login(self):
        from views.login_view import LoginView
        LoginView(self, on_login_success=self._show_main)

    def _show_main(self, user: dict):
        from views.main_view import MainView
        MainView(self, user=user, on_logout=self._show_login)


if __name__ == "__main__":
    app = App()
    app.mainloop()
