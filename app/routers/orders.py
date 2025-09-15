from fastapi import APIRouter
from app.database import execute_query, execute_single_query

router = APIRouter()

@router.get("/sales")
def get_sales():
    return execute_query('SELECT * FROM sales LIMIT 10;')

@router.get("/sales/{sale_id}")
def get_sale(sale_id: int):
    return execute_single_query('SELECT * FROM sales WHERE id = %s;', (sale_id,))
