"""
Main FastAPI application for Vercel deployment
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Simplified imports for Vercel (avoid complex middleware for now)
from app.routers import users, orders, purchase_orders, suppliers, auth
from app.routers.reports import sales, customers, inventory

# Create FastAPI app with Vercel-friendly configuration
app = FastAPI(
    title="Crystal API",
    description="API for wholesale business data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(purchase_orders.router, prefix="/api", tags=["purchase_orders"])
app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])

# Crystal Reports migration - organized report endpoints
app.include_router(sales.router, prefix="/api/reports", tags=["sales_reports"])
app.include_router(customers.router, prefix="/api/reports", tags=["customer_reports"])
app.include_router(inventory.router, prefix="/api/reports", tags=["inventory_reports"])

@app.get("/")
def root():
    return {
        "message": "Welcome to Crystal API", 
        "status": "running on Vercel",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Crystal API",
        "environment": os.getenv("VERCEL_ENV", "development")
    }

# Local development server (works with both local and Vercel)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
