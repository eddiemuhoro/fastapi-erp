from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Base request schemas
class BaseReportRequest(BaseModel):
    environment: str = "production"
    server_id: Optional[str] = None
    password: Optional[str] = None

class SalesReportRequest(BaseReportRequest):
    category: str
    fromdate: Optional[date] = None
    todate: Optional[date] = None
    filter_name: Optional[str] = None

class CustomerReportRequest(BaseReportRequest):
    category: str
    as_of_date: Optional[date] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None

class InventoryReportRequest(BaseReportRequest):
    category: str
    location_id: Optional[int] = None
    threshold: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    fromdate: Optional[date] = None
    todate: Optional[date] = None
    limit: Optional[int] = None
    location: Optional[str] = None

# Response schemas
class StandardResponse(BaseModel):
    success: int
    message: Optional[str] = None
    data: Optional[List[dict]] = None

# Sales response models
class HourlySales(BaseModel):
    hour: int
    total_sales: float
    currency_name: str

class RepSales(BaseModel):
    date: date
    username: str
    total_sales: float
    currency_name: str

class LocationSales(BaseModel):
    date: date
    total_sales: float
    locationname: str
    currency_name: str

# Customer response models
class CustomerOverview(BaseModel):
    total_customers: int
    new_customers_last_30_days: int
    active_customers: int
    inactive_customers: int
    customers_with_outstanding_balance: int

class CustomerBalance(BaseModel):
    customer_id: str
    customer_name: str
    creditlimit: float
    credit: float
    current_balance: float
    last_transaction_date: Optional[datetime]

# Inventory response models
class InventorySummary(BaseModel):
    total_value: float
    total_quantity: int

class StockLevel(BaseModel):
    category_id: int
    category_name: str
    total_stock_quantity: float
    total_stock_value: float
    items: List[dict]
