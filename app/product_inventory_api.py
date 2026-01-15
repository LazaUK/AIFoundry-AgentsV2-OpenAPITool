"""
Product Inventory API - Mock Backend Service

A simple FastAPI service with API key authentication for Azure AI Foundry agent demo.
Provides read-only access to mock product inventory data.
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Security, Query, Path
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Configuration
API_KEY = os.environ.get("API_KEY", "test-api-key-12345")
API_KEY_NAME = "x-api-key"

app = FastAPI(
    title="Product Inventory API",
    description="Mock product inventory API for Azure AI Foundry agent demo",
    version="1.0.0",
)

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key is missing")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    quantity: int
    stock_status: str
    description: Optional[str] = None


class InventorySummary(BaseModel):
    total_products: int
    total_value: float
    by_category: dict
    low_stock_count: int
    out_of_stock_count: int


# Mock product database
PRODUCTS = {
    "PROD-001": Product(
        id="PROD-001", name="Wireless Bluetooth Headphones", category="electronics",
        price=79.99, quantity=150, stock_status="in_stock",
        description="Premium wireless headphones with noise cancellation"
    ),
    "PROD-002": Product(
        id="PROD-002", name="Organic Cotton T-Shirt", category="clothing",
        price=29.99, quantity=8, stock_status="low_stock",
        description="Comfortable 100% organic cotton t-shirt"
    ),
    "PROD-003": Product(
        id="PROD-003", name="Python Programming Guide", category="books",
        price=49.99, quantity=45, stock_status="in_stock",
        description="Comprehensive guide to Python programming"
    ),
    "PROD-004": Product(
        id="PROD-004", name="Smart LED Desk Lamp", category="home",
        price=39.99, quantity=0, stock_status="out_of_stock",
        description="Adjustable LED lamp with USB charging port"
    ),
    "PROD-005": Product(
        id="PROD-005", name="Gourmet Coffee Beans", category="food",
        price=24.99, quantity=200, stock_status="in_stock",
        description="Premium arabica coffee beans, 1kg bag"
    ),
}


@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "Product Inventory API", "version": "1.0.0"}


@app.get("/products", response_model=list[Product])
async def list_products(
    api_key: str = Security(verify_api_key),
    category: Optional[str] = Query(None, description="Filter by category"),
    stock_status: Optional[str] = Query(None, description="Filter by stock status"),
):
    """List all products with optional filtering."""
    products = list(PRODUCTS.values())
    if category:
        products = [p for p in products if p.category == category]
    if stock_status:
        products = [p for p in products if p.stock_status == stock_status]
    return products


@app.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str = Path(..., description="Product ID"),
    api_key: str = Security(verify_api_key),
):
    """Get a specific product by ID."""
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return PRODUCTS[product_id]


@app.get("/inventory/summary", response_model=InventorySummary)
async def get_inventory_summary(api_key: str = Security(verify_api_key)):
    """Get inventory summary statistics."""
    products = list(PRODUCTS.values())
    by_category = {}
    for p in products:
        by_category[p.category] = by_category.get(p.category, 0) + 1
    
    return InventorySummary(
        total_products=len(products),
        total_value=sum(p.price * p.quantity for p in products),
        by_category=by_category,
        low_stock_count=len([p for p in products if p.stock_status == "low_stock"]),
        out_of_stock_count=len([p for p in products if p.stock_status == "out_of_stock"]),
    )


@app.get("/inventory/alerts", response_model=list[Product])
async def get_stock_alerts(api_key: str = Security(verify_api_key)):
    """Get products with low or out of stock status."""
    return [p for p in PRODUCTS.values() if p.stock_status in ("low_stock", "out_of_stock")]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
