import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from backend.services.auth import require_admin
from backend.services.db import get_db_connection

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"], dependencies=[Depends(require_admin)])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PRODUCTS_FILE = DATA_DIR / "products.json"
INTERNAL_DATA_FILE = DATA_DIR / "internal_demo_data.json"


def load_products_json() -> List[Dict[str, Any]]:
    if not PRODUCTS_FILE.exists():
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products_json(products: List[Dict[str, Any]]):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)


class ProductModel(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    category: str
    stock: int
    image: Optional[str] = "/images/product_laptop.jpg"
    badge: Optional[str] = ""
    badge_type: Optional[str] = ""
    rating: Optional[int] = 5
    reviews_count: Optional[int] = 10
    specs: Optional[str] = ""


class OrderStatusUpdate(BaseModel):
    status: str


@router.get("/dashboard", summary="Admin Dashboard Stats and Summaries")
def get_dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total customers
    cursor.execute("SELECT COUNT(*) as cnt FROM customers")
    customers_cnt = cursor.fetchone()["cnt"]

    # Total orders
    cursor.execute("SELECT COUNT(*) as cnt FROM orders")
    orders_cnt = cursor.fetchone()["cnt"]

    # Recent 5 orders for dashboard
    cursor.execute("""
        SELECT order_id, customer_name, product_name, status, order_date
        FROM orders
        ORDER BY order_date DESC, order_id DESC
        LIMIT 5
    """)
    recent_orders = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Products count & list
    products = load_products_json()
    products_cnt = len(products)

    # Top products (take first 5)
    top_products = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "category": p.get("category"),
            "stock": p.get("stock"),
            "price": p.get("price"),
            "image": p.get("image", "/images/product_laptop.jpg")
        }
        for p in products[:5]
    ]

    # AI demo status from environment
    demo_mock_mode = os.getenv("DEMO_MOCK_MODE", "true").lower() in ("true", "1", "yes")
    llm_provider = os.getenv("LLM_PROVIDER", "openai").title()
    llm_model = os.getenv("LLM_MODEL", "gpt-4o")

    return {
        "metrics": {
            "total_products": products_cnt,
            "total_customers": customers_cnt,
            "total_orders": orders_cnt,
            "todays_sales": 1250.00
        },
        "recent_orders": recent_orders,
        "top_products": top_products,
        "ai_security_status": {
            "prompt_firewall": "OFF",
            "input_protection": "OFF",
            "output_protection": "OFF",
            "environment": "INTENTIONALLY VULNERABLE"
        },
        "ai_demo_info": {
            "llm_provider": f"{llm_provider} (Demo)",
            "model": f"{llm_model} (Demo)",
            "mock_mode": "ON" if demo_mock_mode else "OFF",
            "conversation_memory": "In-Memory",
            "max_tokens": 4096
        }
    }


# Product Management
@router.get("/products", summary="List Products for Admin")
def admin_get_products():
    return load_products_json()


@router.post("/products", summary="Add a New Demo Product")
def admin_add_product(product: ProductModel):
    products = load_products_json()
    new_id = product.id or f"P00{len(products) + 1}"
    
    # Check if ID exists
    for p in products:
        if p.get("id", "").lower() == new_id.lower():
            raise HTTPException(status_code=400, detail="Product ID already exists.")

    new_prod = product.model_dump()
    new_prod["id"] = new_id
    products.append(new_prod)
    save_products_json(products)
    return {"success": True, "product": new_prod}


@router.put("/products/{product_id}", summary="Edit an Existing Demo Product")
def admin_update_product(product_id: str, product: ProductModel):
    products = load_products_json()
    updated = False
    for i, p in enumerate(products):
        if p.get("id", "").lower() == product_id.lower():
            prod_data = product.model_dump()
            prod_data["id"] = product_id
            products[i] = prod_data
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found.")

    save_products_json(products)
    return {"success": True, "product": products[i]}


@router.delete("/products/{product_id}", summary="Delete a Demo Product")
def admin_delete_product(product_id: str):
    products = load_products_json()
    initial_len = len(products)
    products = [p for p in products if p.get("id", "").lower() != product_id.lower()]

    if len(products) == initial_len:
        raise HTTPException(status_code=404, detail="Product not found.")

    save_products_json(products)
    return {"success": True, "message": "Product deleted successfully."}


# Customer Management
@router.get("/customers", summary="List Fictional Customers")
def admin_get_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, orders_count, total_spent, registered_date
        FROM customers
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/customers/{customer_id}", summary="Get Customer Details and Orders")
def admin_get_customer_detail(customer_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    if not customer:
        conn.close()
        raise HTTPException(status_code=404, detail="Customer not found.")

    cursor.execute("SELECT * FROM orders WHERE customer_email = ? ORDER BY order_date DESC", (customer["email"],))
    orders = cursor.fetchall()
    conn.close()

    return {
        "customer": dict(customer),
        "orders": [dict(o) for o in orders]
    }


# Order Management
@router.get("/orders", summary="List Fictional Orders")
def admin_get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, customer_name, customer_email, product_id, product_name,
               price, quantity, total_amount, status, carrier, tracking_number, order_date
        FROM orders
        ORDER BY order_date DESC, order_id DESC
    """)
    orders = cursor.fetchall()
    conn.close()
    return [dict(o) for o in orders]


@router.put("/orders/{order_id}/status", summary="Update Demo Order Status")
def admin_update_order_status(order_id: str, payload: OrderStatusUpdate):
    valid_statuses = ["Processing", "Shipped", "Delivered", "Cancelled"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Choose one of: {', '.join(valid_statuses)}"
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (payload.status, order_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found.")
    conn.commit()
    conn.close()

    return {"success": True, "order_id": order_id, "status": payload.status}


# AI Demo Status & Internal Demo Data
@router.get("/ai-demo", summary="AI Demo Environment Details")
def admin_ai_demo_info():
    demo_mock_mode = os.getenv("DEMO_MOCK_MODE", "true").lower() in ("true", "1", "yes")
    llm_provider = os.getenv("LLM_PROVIDER", "openai").title()
    llm_model = os.getenv("LLM_MODEL", "gpt-4o")

    return {
        "status": "Online",
        "security": {
            "prompt_firewall": "OFF",
            "input_protection": "OFF",
            "output_protection": "OFF",
            "risk_scoring": "OFF",
            "environment": "INTENTIONALLY VULNERABLE"
        },
        "config": {
            "llm_provider": llm_provider,
            "model": llm_model,
            "mock_mode": demo_mock_mode,
            "conversation_memory": "In-Memory Window (6 turns)",
            "max_tokens": 4096
        },
        "axf_purpose": (
            "Queen Sheba AI is configured without security guardrails to serve as a target "
            "for testing AI firewall (AXF) capabilities. Prompt injections, system instruction "
            "overrides, and internal data requests will succeed in this demo state."
        )
    }


@router.get("/internal-demo-data", summary="Internal Fictional Demo Data")
def admin_internal_demo_data():
    if not INTERNAL_DATA_FILE.exists():
        return {}
    with open(INTERNAL_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
