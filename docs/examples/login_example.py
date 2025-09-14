#!/usr/bin/env python3
"""
Authentication Example for FastAPI ERP System

This example demonstrates how to authenticate with the API and make authenticated requests.
"""

import requests
import json
from typing import Optional, Dict, Any


class FastAPIClient:
    """Simple client for FastAPI ERP System."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.user_data: Optional[Dict[str, Any]] = None
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the API.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.user_data = data.get("data")
                    print(f"✅ Login successful for user: {username}")
                    print(f"   User ID: {self.user_data.get('user_id')}")
                    return True
                else:
                    print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Login request failed with status code: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during login: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information.
        
        Returns:
            User data if successful, None otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data")
            
            print(f"❌ Failed to get current user: {response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error getting current user: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.user_data is not None
    
    def logout(self):
        """Clear authentication data."""
        self.user_data = None
        self.session.cookies.clear()
        print("🔓 Logged out successfully")


def main():
    """Demonstrate authentication workflow."""
    print("🚀 FastAPI ERP System - Authentication Example")
    print("=" * 50)
    
    # Create client
    client = FastAPIClient()
    
    # Example 1: Successful login
    print("\n📋 Example 1: User Login")
    print("-" * 30)
    
    # Note: Replace with actual credentials from your database
    username = input("Enter username (or press Enter for 'admin'): ").strip() or "admin"
    password = input("Enter password (or press Enter for 'password'): ").strip() or "password"
    
    if client.login(username, password):
        print(f"✅ Authentication successful!")
        
        # Get current user info
        user_info = client.get_current_user()
        if user_info:
            print(f"📄 Current user info:")
            for key, value in user_info.items():
                print(f"   {key}: {value}")
    else:
        print("❌ Authentication failed!")
        return
    
    # Example 2: Check authentication status
    print(f"\n🔍 Authentication Status: {'✅ Authenticated' if client.is_authenticated() else '❌ Not authenticated'}")
    
    # Example 3: Make authenticated request (if you have other endpoints)
    print("\n📊 Example 2: Making Authenticated Requests")
    print("-" * 40)
    
    if client.is_authenticated():
        # Try to access a protected endpoint (example)
        try:
            # This is just an example - replace with actual endpoint
            response = client.session.get(f"{client.base_url}/api/v1/customers/")
            if response.status_code == 200:
                print("✅ Successfully accessed protected endpoint")
            else:
                print(f"ℹ️  Endpoint returned status: {response.status_code}")
        except Exception as e:
            print(f"ℹ️  Could not test protected endpoint: {e}")
    
    # Example 4: Logout
    print("\n🔓 Example 3: Logout")
    print("-" * 20)
    client.logout()


if __name__ == "__main__":
    main()
