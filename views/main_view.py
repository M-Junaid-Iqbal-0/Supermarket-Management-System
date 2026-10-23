"""
views/main_view.py
Main application window: sidebar + content area.
Loaded after successful login.
"""

import tkinter as tk
from theme import *
from widgets import AppButton


# Nav items per role: (label, view_key, icon)
NAV_ADMIN = [
    ("Dashboard",       "dashboard",    "📊"),
    ("Customers",       "customers",    "👤"),
    ("Employees",       "employees",    "👷"),
    ("Products",        "products",     "📦"),
    ("Categories",      "categories",   "🏷️"),
    ("Suppliers",       "suppliers",    "🚚"),
    ("Inventory",       "inventory",    "🗄️"),
    ("Sales",           "sales",        "🧾"),
    ("Sale History",    "sale_history", "📜"),
    ("Purchase Orders", "purchases",    "🛒"),
    ("Users",           "users",        "🔑"),
]

NAV_EMPLOYEE = [
    ("Dashboard",       "dashboard",    "📊"),
    ("Products",        "products",     "📦"),
    ("Inventory",       "inventory",    "🗄️"),
    ("Sales",           "sales",        "🧾"),
    ("Sale History",    "sale_history", "📜"),
]

NAV_CUSTOMER = [
    ("Products",        "products",     "📦"),
    ("My Purchases",    "sale_history", "📜"),
]


class MainView(tk.Frame):
    def __init__(self, parent, user: dict, on_logout):
        super().__init__(parent, bg=BG_DARK)
        self.user = user
        self.on_logout = on_logout
        self.content_frame = None
        self.current_view = None
        self._nav_buttons = {}
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        # ── Sidebar ───────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=BG_PANEL, width=SIDEBAR_W)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo = tk.Frame(self.sidebar, bg=BG_PANEL)
        logo.pack(fill="x", pady=(20, 8), padx=PAD)
        tk.Label(logo, text="🛒 FreshMart", font=FONT_HEAD,
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w")
        tk.Label(logo, text="Management System", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=PAD, pady=8)

        # Role badge
        role_colors = {"admin": ACCENT, "employee": ACCENT2, "customer": WARNING}
        role_color = role_colors.get(self.user["role"], TEXT_DIM)
        badge = tk.Frame(self.sidebar, bg=BG_PANEL)
        badge.pack(fill="x", padx=PAD, pady=(0, 12))
        tk.Label(badge, text=self.user["username"], font=FONT_BTN,
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(badge, text=self.user["role"].upper(), font=FONT_SMALL,
                 bg=BG_PANEL, fg=role_color).pack(anchor="w")

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=PAD, pady=(0, 8))

        # Nav items
        nav_items = {
            "admin": NAV_ADMIN,
            "employee": NAV_EMPLOYEE,
            "customer": NAV_CUSTOMER,
        }.get(self.user["role"], NAV_CUSTOMER)

        self.nav_frame = tk.Frame(self.sidebar, bg=BG_PANEL)
        self.nav_frame.pack(fill="x")

        for label, key, icon in nav_items:
            btn = tk.Button(
                self.nav_frame,
                text=f"  {icon}  {label}",
                font=FONT_BODY,
                bg=BG_PANEL,
                fg=TEXT_DIM,
                activebackground=BG_CARD,
                activeforeground=TEXT_WHITE,
                relief="flat",
                anchor="w",
                cursor="hand2",
                padx=8,
                pady=7,
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x", padx=6, pady=1)
            self._nav_buttons[key] = btn

        # Logout at bottom
        tk.Frame(self.sidebar, bg=BG_PANEL).pack(expand=True)
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=PAD, pady=8)
        AppButton(self.sidebar, "⬅  Logout", command=self._logout,
                  color=DANGER).pack(fill="x", padx=PAD, pady=(0, 14))

        # ── Content area ──────────────────────────────────
        self.content_frame = tk.Frame(self, bg=BG_DARK)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # Load first nav item by default
        first_key = nav_items[0][1]
        self.navigate(first_key)

    def navigate(self, key: str):
        """Load a view into the content area."""
        # Highlight active nav button
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.config(bg=BG_CARD, fg=TEXT_WHITE)
            else:
                btn.config(bg=BG_PANEL, fg=TEXT_DIM)

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Load view
        view = self._load_view(key)
        if view:
            view.pack(fill="both", expand=True)
        self.current_view = key

    def _load_view(self, key: str):
        role = self.user["role"]
        user = self.user

        if key == "dashboard":
            from views.dashboard_view import DashboardView
            return DashboardView(self.content_frame, user)
        elif key == "customers":
            from views.customer_view import CustomerView
            return CustomerView(self.content_frame, user)
        elif key == "employees":
            from views.employee_view import EmployeeView
            return EmployeeView(self.content_frame, user)
        elif key == "products":
            from views.product_view import ProductView

            if user["role"] == "customer":
                return ProductView(self.content_frame, user, readonly=True)

            return ProductView(self.content_frame, user)
        elif key == "categories":
            from views.category_view import CategoryView
            return CategoryView(self.content_frame, user)
        elif key == "suppliers":
            from views.supplier_view import SupplierView
            return SupplierView(self.content_frame, user)
        elif key == "inventory":
            from views.inventory_view import InventoryView
            return InventoryView(self.content_frame, user)
        elif key == "sales":
            from views.sales_view import SalesView
            return SalesView(self.content_frame, user)
        elif key == "sale_history":
            from views.sale_history_view import SaleHistoryView
            return SaleHistoryView(self.content_frame, user)
        elif key == "purchases":
            from views.purchase_view import PurchaseView
            return PurchaseView(self.content_frame, user)
        elif key == "users":
            from views.user_mgmt_view import UserMgmtView
            return UserMgmtView(self.content_frame, user)
        return None

    def _logout(self):
        self.destroy()
        self.on_logout()
