from fastapi import APIRouter
from app.database import execute_query, execute_single_query

router = APIRouter()

@router.get("/orders")
def get_orders():
    return execute_query('SELECT * FROM orders LIMIT 10;')

@router.get("/orders/{order_id}")
def get_order(order_id: int):
    return execute_single_query('SELECT * FROM orders WHERE id = %s;', (order_id,))
