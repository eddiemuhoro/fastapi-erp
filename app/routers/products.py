from fastapi import APIRouter
from app.database import execute_query, execute_single_query

router = APIRouter()

@router.get("/products")
def get_products():
    return execute_query('SELECT * FROM products LIMIT 10;')

@router.get("/products/{product_id}")
def get_product(product_id: int):
    return execute_single_query('SELECT * FROM products WHERE id = %s;', (product_id,))
