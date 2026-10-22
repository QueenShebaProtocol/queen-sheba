import os
import sqlite3
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "queen_sheba.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return hashed, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    hashed, _ = hash_password(password, salt)
    return secrets.compare_digest(hashed, password_hash)


def init_db():
    """Initialize database tables and seed default fictional demo accounts and data."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        product_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Processing',
        carrier TEXT,
        tracking_number TEXT,
        order_date TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        orders_count INTEGER DEFAULT 1,
        total_spent REAL DEFAULT 0.0,
        registered_date TEXT NOT NULL
    )
    """)

    # Seed Admin User if not present
    cursor.execute("SELECT id FROM users WHERE email = 'admin@queensheba.demo'")
    admin_row = cursor.fetchone()
    if not admin_row:
        p_hash, salt = hash_password("DemoAdmin123!")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, salt, role) VALUES (?, ?, ?, ?, ?)",
            ("Admin User", "admin@queensheba.demo", p_hash, salt, "admin")
        )

    # Seed Demo Customer One
    cursor.execute("SELECT id FROM users WHERE email = 'demo1@example.com'")
    c1_row = cursor.fetchone()
    if not c1_row:
        p_hash, salt = hash_password("DemoCustomer123!")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, salt, role) VALUES (?, ?, ?, ?, ?)",
            ("Demo Customer One", "demo1@example.com", p_hash, salt, "user")
        )
        c1_id = cursor.lastrowid
    else:
        c1_id = c1_row["id"]

    # Seed Demo Customer Two
    cursor.execute("SELECT id FROM users WHERE email = 'demo2@example.com'")
    c2_row = cursor.fetchone()
    if not c2_row:
        p_hash, salt = hash_password("DemoCustomer123!")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, salt, role) VALUES (?, ?, ?, ?, ?)",
            ("Demo Customer Two", "demo2@example.com", p_hash, salt, "user")
        )
        c2_id = cursor.lastrowid
    else:
        c2_id = c2_row["id"]

    # Seed Demo Customers List (Total 12)
    demo_customers_data = [
        ("C001", "Demo Customer One", "demo1@example.com", 2, 978.00, "May 01, 2025"),
        ("C002", "Demo Customer Two", "demo2@example.com", 1, 79.00, "May 03, 2025"),
        ("C003", "Demo Customer Three", "demo3@example.com", 1, 129.00, "May 05, 2025"),
        ("C004", "Demo Customer Four", "demo4@example.com", 1, 29.00, "May 07, 2025"),
        ("C005", "Demo Customer Five", "demo5@example.com", 1, 49.00, "May 09, 2025"),
        ("C006", "Sara Bekele", "sara.b@example.com", 1, 899.00, "May 10, 2025"),
        ("C007", "Dawit Haile", "dawit.h@example.com", 0, 0.00, "May 11, 2025"),
        ("C008", "Marta Tadesse", "marta.t@example.com", 0, 0.00, "May 12, 2025"),
        ("C009", "Yohannes Girma", "yohannes.g@example.com", 1, 79.00, "May 12, 2025"),
        ("C010", "Bethlehem Alemu", "bethlehem.a@example.com", 0, 0.00, "May 13, 2025"),
        ("C011", "Kassahun Desta", "kassahun.d@example.com", 0, 0.00, "May 14, 2025"),
        ("C012", "Hanna Solomon", "hanna.s@example.com", 0, 0.00, "May 14, 2025"),
    ]

    cursor.execute("SELECT COUNT(*) as cnt FROM customers")
    if cursor.fetchone()["cnt"] == 0:
        cursor.executemany(
            "INSERT INTO customers (id, name, email, orders_count, total_spent, registered_date) VALUES (?, ?, ?, ?, ?, ?)",
            demo_customers_data
        )

    # Seed Demo Orders (Total 8, matches Admin_panal.png Recent Orders)
    demo_orders_data = [
        ("QS-1008", c1_id, "Demo Customer One", "demo1@example.com", "P001", "ShebaBook Pro", 899.00, 1, 899.00, "Shipped", "Sheba Express Courier", "SHB-EXP-9821734", "May 16, 2025"),
        ("QS-1007", c2_id, "Demo Customer Two", "demo2@example.com", "P002", "Royal Headset", 79.00, 1, 79.00, "Processing", "Sheba Express Courier", "SHB-EXP-4419203", "May 16, 2025"),
        ("QS-1006", None, "Demo Customer Three", "demo3@example.com", "P003", "Sheba Smart Watch", 129.00, 1, 129.00, "Delivered", "Sheba Express Courier", "SHB-EXP-8817291", "May 15, 2025"),
        ("QS-1005", None, "Demo Customer Four", "demo4@example.com", "P005", "Wireless Mouse", 29.00, 1, 29.00, "Processing", "Sheba Express Courier", "SHB-EXP-1123984", "May 15, 2025"),
        ("QS-1004", None, "Demo Customer Five", "demo5@example.com", "P004", "Royal Keyboard", 49.00, 1, 49.00, "Shipped", "Sheba Express Courier", "SHB-EXP-6629184", "May 14, 2025"),
        ("QS-1003", None, "Sara Bekele", "sara.b@example.com", "P001", "ShebaBook Pro", 899.00, 1, 899.00, "Delivered", "Sheba Express Courier", "SHB-EXP-3329181", "May 13, 2025"),
        ("QS-1002", c2_id, "Demo Customer Two", "demo2@example.com", "P002", "Royal Headset", 79.00, 1, 79.00, "Delivered", "Sheba Express Courier", "SHB-EXP-4419202", "May 11, 2025"),
        ("QS-1001", c1_id, "Demo Customer One", "demo1@example.com", "P002", "Royal Headset", 79.00, 1, 79.00, "Delivered", "Sheba Express Courier", "SHB-EXP-9821733", "May 10, 2025"),
    ]

    cursor.execute("SELECT COUNT(*) as cnt FROM orders")
    if cursor.fetchone()["cnt"] == 0:
        cursor.executemany(
            """INSERT INTO orders (
                order_id, user_id, customer_name, customer_email, product_id, product_name,
                price, quantity, total_amount, status, carrier, tracking_number, order_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            demo_orders_data
        )

    conn.commit()
    conn.close()
