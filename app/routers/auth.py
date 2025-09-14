from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import hashlib
from app.database import execute_single_query

router = APIRouter()

class LoginRequest(BaseModel):
    email: str  # Changed from username to email to match PHP
    password: str

class LoginResponse(BaseModel):
    issuccess: str
    success: int
    userid: int
    loccode: str
    username: str
    roleid: int
    message: str

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest):
    """Login using email/password with MD5 verification (matching PHP legacy system)"""
    
    try:
        # Get user from database using email (like PHP code)
        user = execute_single_query(
            "SELECT * FROM users WHERE email = %s AND active = '1'", 
            (login_data.email,)
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid Email Address!"
            )
        
        # Check password length (matching PHP validation)
        if len(login_data.password) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Your password must be at least 4 characters long!"
            )
        
        # Verify password using MD5 (matching PHP: md5($password)==$row['password'])
        hashed_input_password = hashlib.md5(login_data.password.encode()).hexdigest()
        
        if hashed_input_password != user['password']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid Password!"
            )
        
        # Return response matching PHP structure
        return LoginResponse(
            issuccess="True",
            success=1,
            userid=user['id'],
            loccode=user['loccode'],
            username=user['username'],
            roleid=user['type'],
            message="You have successfully logged in."
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the actual error for debugging
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login system error"
        )

@router.get("/debug/{email}")
def debug_user(email: str):
    """Debug endpoint to check user data structure"""
    user = execute_single_query(
        "SELECT id, username, email, password, active, loccode, type FROM users WHERE email = %s LIMIT 1", 
        (email,)
    )
    if user:
        return {
            "found": True,
            "user_id": user.get('id'),
            "username": user.get('username'),
            "email": user.get('email'),
            "active": user.get('active'),
            "loccode": user.get('loccode'),
            "type": user.get('type'),
            "password_exists": bool(user.get('password')),
            "password_length": len(user.get('password', '')) if user.get('password') else 0,
        }
    return {"found": False}
