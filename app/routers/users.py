from fastapi import APIRouter
from app.database import execute_query, execute_single_query

router = APIRouter()

@router.get("/users")
def get_users():
    return execute_query('SELECT * FROM users LIMIT 10;')

@router.get("/users/{user_id}")
def get_user(user_id: int):
    return execute_single_query('SELECT id, username, email FROM users WHERE id = %s;', (user_id,))
