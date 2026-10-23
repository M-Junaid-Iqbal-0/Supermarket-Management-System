"""
db/connection.py
Oracle DB connection pool and query helpers.
"""

import oracledb
import hashlib
from config import DB_CONFIG


# ── Connection ────────────────────────────────────────────
def get_connection():
    """Return a new Oracle connection."""
    return oracledb.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        dsn=DB_CONFIG["dsn"],
    )


def test_connection():
    """Returns True if DB is reachable, else False + error string."""
    try:
        con = get_connection()
        con.close()
        return True, None
    except Exception as e:
        return False, str(e)


# ── Auth helpers ──────────────────────────────────────────
def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def login(username: str, password: str):
    """
    Returns user dict on success, None on failure.
    dict keys: user_id, username, role, employee_id, customer_id
    """
    hashed = hash_password(password)
    sql = """
        SELECT UserID, Username, Role, EmployeeID, CustomerID
        FROM AppUser
        WHERE Username = :u AND PasswordHash = :p AND IsActive = 1
    """
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute(sql, u=username, p=hashed)
        row = cur.fetchone()
        cur.close()
        con.close()
        if row:
            return {
                "user_id": row[0],
                "username": row[1],
                "role": row[2],
                "employee_id": row[3],
                "customer_id": row[4],
            }
        return None
    except Exception as e:
        raise RuntimeError(f"Login error: {e}")


# ── Generic helpers ───────────────────────────────────────
def fetch_all(sql: str, params: dict = None):
    """Run a SELECT and return list of rows (tuples)."""
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql, params or {})
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    cur.close()
    con.close()
    return cols, rows


def execute(sql: str, params: dict = None):
    """Run INSERT/UPDATE/DELETE and commit."""
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql, params or {})
    con.commit()
    cur.close()
    con.close()


def execute_many(sql: str, data: list):
    """Bulk execute with a list of param dicts."""
    con = get_connection()
    cur = con.cursor()
    cur.executemany(sql, data)
    con.commit()
    cur.close()
    con.close()
