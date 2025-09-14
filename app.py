from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, orders, products, purchase_orders, suppliers, auth
from app.routers.reports import sales, customers, inventory

app = FastAPI(title="Wholesale API", description="API for wholesale business data")

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
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(purchase_orders.router, prefix="/api", tags=["purchase_orders"])
app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])

# Crystal Reports migration - organized report endpoints
app.include_router(sales.router, prefix="/api/reports", tags=["sales_reports"])
app.include_router(customers.router, prefix="/api/reports", tags=["customer_reports"])
app.include_router(inventory.router, prefix="/api/reports", tags=["inventory_reports"])

@app.get("/")
def root():
    return {"message": "Welcome to Wholesale API"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
