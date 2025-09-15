from fastapi import APIRouter
from app.database import execute_query, execute_single_query

router = APIRouter()

@router.get("/suppliers")
def get_suppliers():
    return execute_query('SELECT * FROM supplier LIMIT 10;')

@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: int):
    return execute_single_query('SELECT * FROM supplier WHERE id = %s;', (supplier_id,))
