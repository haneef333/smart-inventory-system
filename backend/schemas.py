from pydantic import BaseModel
from typing import Optional


class InventoryItemCreate(BaseModel):
    item_name: str
    category: Optional[str] = None
    quantity: float = 0
    unit: Optional[str] = None
    cost_per_unit: float = 0
    reorder_threshold: float = 10


class InventoryRestock(BaseModel):
    add_quantity: float


class RecipeCreate(BaseModel):
    product_name: str
    ingredient_name: str
    quantity_needed: float
    unit: Optional[str] = None


class OrderCreate(BaseModel):
    product_name: str
    order_quantity: int
    selling_price: float
