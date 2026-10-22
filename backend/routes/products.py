import json
import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/products", tags=["Products"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "products.json"


def load_products() -> List[dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("", summary="List all products")
def get_products():
    """Retrieve all available products from the Queen Sheba catalog."""
    return load_products()


@router.get("/{product_id}", summary="Get product details")
def get_product(product_id: str):
    """Retrieve details for a specific product by its ID."""
    products = load_products()
    for item in products:
        if item.get("id", "").lower() == product_id.lower():
            return item
    raise HTTPException(status_code=404, detail="Product not found")
