from fastapi import APIRouter
from app.database import execute_query, execute_single_query

router = APIRouter()

@router.get("/purchase-orders")
def get_purchase_orders():
    return execute_query('SELECT * FROM purchase_orders LIMIT 10;')

@router.get("/purchase-orders/{po_id}")
def get_purchase_order(po_id: int):
    return execute_single_query('SELECT * FROM purchase_orders WHERE id = %s;', (po_id,))
