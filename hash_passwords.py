"""
Script to hash existing plain text passwords in your database
Run this ONCE to convert plain text passwords to hashed passwords
"""
from app.database import get_db_cursor
from app.auth import get_password_hash

def hash_existing_passwords():
    """Hash all plain text passwords in the users table"""
    with get_db_cursor() as cursor:
        # Get all users with plain text passwords
        cursor.execute("SELECT id, username, password FROM users WHERE password_hash IS NULL OR password_hash = ''")
        users = cursor.fetchall()
        
        for user in users:
            if user['password']:  # If password exists
                hashed_password = get_password_hash(user['password'])
                
                # Update with hashed password
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s", 
                    (hashed_password, user['id'])
                )
                print(f"Hashed password for user: {user['username']}")
        
        # Commit changes
        cursor.connection.commit()
        print("Password hashing completed!")

if __name__ == "__main__":
    hash_existing_passwords()
