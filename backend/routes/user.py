from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from backend.services.auth import get_current_user
from backend.services.db import get_db_connection

router = APIRouter(prefix="/api/user", tags=["User Account"])


@router.get("/profile", summary="Get User Profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user": current_user
    }


@router.get("/orders", summary="Get User Fictional Orders")
def get_user_orders(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, customer_name, customer_email, product_id, product_name,
               price, quantity, total_amount, status, carrier, tracking_number, order_date
        FROM orders
        WHERE user_id = ? OR customer_email = ? COLLATE NOCASE
        ORDER BY order_date DESC
    """, (current_user["id"], current_user["email"]))
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]
