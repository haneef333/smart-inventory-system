from pydantic import BaseModel, Field
from typing import Literal, Optional


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
    payment_method: str = "cash"  # "cash" or "online"


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


# --- Online orders (sent by the storefront app) ---

class OnlineOrderItemIn(BaseModel):
    product_name: str  # must match recipes.product_name
    display_name: Optional[str] = None  # name shown on the storefront menu, with size/flavour
    quantity: int = Field(ge=1, le=50)
    unit_price: float = Field(ge=0)
    recipe_scale: float = Field(default=1, gt=0, le=10)  # 2 kg cake = 2 x the recipe
    details: Optional[str] = None  # occasion, message on the cake, candles
    photo_url: Optional[str] = None  # customer's reference design


class OnlineOrderIn(BaseModel):
    external_id: str = Field(min_length=1, max_length=40)  # storefront order number
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    fulfilment: Literal["pickup", "delivery"] = "pickup"
    address: Optional[str] = None
    due_date: str  # 'YYYY-MM-DD'
    time_slot: Optional[str] = None
    payment_method: Literal["cash", "online"] = "cash"
    notes: Optional[str] = None
    delivery_fee: float = 0
    coupon_code: Optional[str] = None
    discount: float = Field(default=0, ge=0)
    total: float = 0
    items: list[OnlineOrderItemIn] = Field(min_length=1)


class OnlineOrderDecline(BaseModel):
    reason: Optional[str] = None


class OnlineOrderStatusUpdate(BaseModel):
    status: Optional[Literal["baking", "ready", "completed"]] = None
    payment_status: Optional[Literal["paid", "unpaid"]] = None


class OwnerLogin(BaseModel):
    password: str
