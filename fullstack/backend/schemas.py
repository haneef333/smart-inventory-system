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
    customer_name: Optional[str] = None
    due_date: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    delivery_status: Optional[str] = None
    payment_status: Optional[str] = None


class ExpenseCreate(BaseModel):
    description: str
    category: str
    amount: float


class ShoppingListItem(BaseModel):
    product_name: str
    quantity: int


class ShoppingListRequest(BaseModel):
    items: list[ShoppingListItem] = []
    include_low_stock: bool = True


class TaskCreate(BaseModel):
    task_date: str  # 'YYYY-MM-DD'
    title: str


class TaskUpdate(BaseModel):
    is_done: Optional[bool] = None
    title: Optional[str] = None
