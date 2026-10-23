# FreshMart POS — Student Project
Supermarket management GUI built with Python + Tkinter connected to Oracle DB 21c XE.

---

## Setup (do this once)

### 1. Install Python dependency
```
pip install oracledb
```

### 2. Run the SQL setup script in SQL Developer
Open `setup.sql` and run it against your schema.
This creates the `AppUser` and `Sale_History` tables and seeds the default admin login.

### 3. Edit config.py
Fill in your Oracle credentials:
```python
DB_CONFIG = {
    "user":     "your_username",
    "password": "your_password",
    "dsn":      "localhost/XEPDB1",   # default for 21c XE
}
```
> If you used a different PDB name, change `XEPDB1` accordingly.
> You can check in SQL Developer: View → DBA → Container Database.

---

## Run the app
```
python app.py
```

---

## Default Login
| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | Admin |

Create more users inside the app under **Users** tab.

---

## What each role can do

| Feature            | Admin | Employee | Customer |
|--------------------|-------|----------|----------|
| Dashboard          | ✅    | ✅       | ❌       |
| Customers (CRUD)   | ✅    | ❌       | ❌       |
| Employees (CRUD)   | ✅    | ❌       | ❌       |
| Products (CRUD)    | ✅    | ✅ view  | ✅ view  |
| Categories (CRUD)  | ✅    | ❌       | ❌       |
| Suppliers (CRUD)   | ✅    | ❌       | ❌       |
| Inventory          | ✅    | ✅       | ❌       |
| Sales              | ✅    | ✅       | ❌       |
| Sale History       | ✅    | ✅ view  | ✅ own   |
| Purchase Orders    | ✅    | ❌       | ❌       |
| User Accounts      | ✅    | ❌       | ❌       |

---

## Project Structure
```
supermarket_gui/
├── app.py              ← entry point
├── config.py           ← DB credentials (edit this)
├── theme.py            ← colors & fonts
├── widgets.py          ← reusable UI components
├── requirements.txt
├── setup.sql           ← run once in SQL Developer
├── db/
│   └── connection.py   ← Oracle connection helpers
└── views/
    ├── login_view.py
    ├── main_view.py
    ├── dashboard_view.py
    ├── customer_view.py
    ├── employee_view.py
    ├── product_view.py
    ├── category_view.py
    ├── supplier_view.py
    ├── inventory_view.py
    ├── sales_view.py
    ├── sale_history_view.py
    ├── purchase_view.py
    └── user_mgmt_view.py
```
