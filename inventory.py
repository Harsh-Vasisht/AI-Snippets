
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

MOCK_INVENTORY = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "stockStatus": "InStock"},
    {"id": 2, "name": "T-Shirt", "category": "Apparel", "stockStatus": "OutOfStock"},
    {"id": 3, "name": "Headphones", "category": "Electronics", "stockStatus": "InStock"},
]

@router.get("/inventory/search")
def search_inventory(
    q: Optional[str] = Query("", alias="q"),
    category: Optional[str] = None,
    stockStatus: Optional[str] = None,
):
    results = MOCK_INVENTORY
    if q:
        results = [item for item in results if q.lower() in item["name"].lower()]
    if category:
        results = [item for item in results if item["category"] == category]
    if stockStatus:
        results = [item for item in results if item["stockStatus"] == stockStatus]
    return {"results": results}
