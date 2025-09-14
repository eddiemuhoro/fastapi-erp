"""
Main FastAPI application with improved structure
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.utils import setup_logging

# Import routers
from app.routers import users, orders, products, purchase_orders, suppliers, auth
from app.routers.reports import sales, customers, inventory

# Setup logging
setup_logging(level="INFO" if settings.environment == "production" else "DEBUG")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with versioning
API_PREFIX = "/api/v1"

# Authentication routes
app.include_router(
    auth.router, 
    prefix=f"{API_PREFIX}/auth", 
    tags=["authentication"]
)

# Basic CRUD routes
app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
app.include_router(orders.router, prefix=API_PREFIX, tags=["orders"])
app.include_router(products.router, prefix=API_PREFIX, tags=["products"])
app.include_router(purchase_orders.router, prefix=API_PREFIX, tags=["purchase_orders"])
app.include_router(suppliers.router, prefix=API_PREFIX, tags=["suppliers"])

# Report routes
app.include_router(
    sales.router, 
    prefix=f"{API_PREFIX}/reports", 
    tags=["sales_reports"]
)
app.include_router(
    customers.router, 
    prefix=f"{API_PREFIX}/reports", 
    tags=["customer_reports"]
)
app.include_router(
    inventory.router, 
    prefix=f"{API_PREFIX}/reports", 
    tags=["inventory_reports"]
)

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.api_title}",
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.api_version
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "app.main:app" if settings.environment == "production" else "app.main:app",
        host='0.0.0.0', 
        port=5000,
        reload=settings.debug,
        log_level="info" if settings.environment == "production" else "debug"
    )
