# API Guide

This guide provides detailed information about using the FastAPI ERP System APIs.

## Table of Contents

- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Request/Response Format](#requestresponse-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Authentication

The API uses simple authentication compatible with the legacy PHP system.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "your_username",
    "message": "Login successful"
  },
  "message": "Login successful",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

### Get Current User

```http
GET /api/v1/auth/me
```

## API Endpoints

### Sales Reports

#### Get Sales Summary

```http
POST /api/v1/reports/sales
Content-Type: application/json

{
  "category": "today_hourly",
  "fromdate": "2024-01-01",
  "todate": "2024-12-31"
}
```

**Available Categories:**

- `today_hourly` - Hourly sales for today
- `rep` - Sales by representative
- `location` - Sales by location
- `route` - Sales by route
- `category` - Sales by product category
- `item` - Sales by item
- `item_trend` - Item sales trend
- `customer` - Sales by customer
- `inventory` - Inventory-related sales data

### Customer Reports

#### Get Customer Balances

```http
POST /api/v1/reports/customers
Content-Type: application/json

{
  "category": "customer_balances",
  "as_of_date": "2024-12-31"
}
```

**Available Categories:**

- `overview` - Customer overview
- `customer_balances` - Current balances
- `due_invoices` - Outstanding invoices
- `customer_list` - Customer listing
- `aging_summary` - Aging analysis

### Inventory Reports

#### Get Inventory Summary

```http
POST /api/v1/reports/inventory
Content-Type: application/json

{
  "category": "summary",
  "location_id": 1
}
```

**Available Categories:**

- `summary` - Overall inventory summary
- `stock_levels` - Current stock levels
- `low_stock` - Items below threshold
- `overstock` - Overstocked items
- `top_selling` - Best-selling products
- `slow_moving` - Slow-moving inventory
- `negative_quantities` - Negative stock items
- `turnover_rate` - Inventory turnover
- `incoming_stock` - Incoming inventory
- `outgoing_stock` - Outgoing inventory
- `dead_stock` - Dead stock analysis

### Customer Management

#### List Customers

```http
GET /api/v1/customers/
```

#### Get Customer Details

```http
GET /api/v1/customers/{customer_id}
```

#### Search Customers

```http
GET /api/v1/customers/search?q=search_term
```

### Inventory Management

#### List Inventory

```http
GET /api/v1/inventory/
```

#### Get Low Stock Items

```http
GET /api/v1/inventory/low-stock?threshold=10
```

#### Search Products

```http
GET /api/v1/inventory/search?q=product_name
```

## Request/Response Format

### Standard Response Format

All API responses follow this consistent format:

```json
{
  "success": boolean,
  "data": object | array | null,
  "message": string,
  "timestamp": string (ISO 8601)
}
```

### Success Response Example

```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      }
    ],
    "total": 1
  },
  "message": "Customers retrieved successfully",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

### Error Response Example

```json
{
  "success": false,
  "data": null,
  "message": "Customer not found",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Validation Errors

When validation fails, you'll receive a detailed error response:

```json
{
  "success": false,
  "data": {
    "detail": [
      {
        "loc": ["body", "fromdate"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  },
  "message": "Validation error",
  "timestamp": "2025-09-15T10:30:00Z"
}
```

## Rate Limiting

Currently, there are no rate limits implemented, but for production use, consider:

- 100 requests per minute per IP
- 1000 requests per hour per authenticated user
- Different limits for different endpoint types

## Examples

### Complete Sales Report Workflow

1. **Login**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

2. **Get Today's Hourly Sales**

```bash
curl -X POST "http://localhost:8000/api/v1/reports/sales" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "today_hourly"
  }'
```

3. **Get Sales by Representative**

```bash
curl -X POST "http://localhost:8000/api/v1/reports/sales" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "rep",
    "fromdate": "2024-01-01",
    "todate": "2024-12-31"
  }'
```

### Customer Management Workflow

1. **List All Customers**

```bash
curl -X GET "http://localhost:8000/api/v1/customers/"
```

2. **Search for Customers**

```bash
curl -X GET "http://localhost:8000/api/v1/customers/search?q=John"
```

3. **Get Customer Details**

```bash
curl -X GET "http://localhost:8000/api/v1/customers/123"
```

### Inventory Management Workflow

1. **Get Inventory Summary**

```bash
curl -X POST "http://localhost:8000/api/v1/reports/inventory" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "summary"
  }'
```

2. **Check Low Stock Items**

```bash
curl -X POST "http://localhost:8000/api/v1/reports/inventory" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "low_stock",
    "threshold": 10
  }'
```

3. **Get Top Selling Items**

```bash
curl -X POST "http://localhost:8000/api/v1/reports/inventory" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "top_selling",
    "limit": 5,
    "from_date": "2024-01-01",
    "to_date": "2024-12-31"
  }'
```

## Best Practices

1. **Always handle errors gracefully**
2. **Use appropriate HTTP methods**
3. **Include proper Content-Type headers**
4. **Validate input data before sending requests**
5. **Implement proper logging on the client side**
6. **Use environment-specific base URLs**

## SDK Examples

### Python

```python
import requests

class FastAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, username, password):
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        return response.json()

    def get_sales_report(self, category, **kwargs):
        response = self.session.post(
            f"{self.base_url}/api/v1/reports/sales",
            json={"category": category, **kwargs}
        )
        return response.json()
```

### JavaScript

```javascript
class FastAPIClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });
    return await response.json();
  }

  async getSalesReport(category, options = {}) {
    const response = await fetch(`${this.baseUrl}/api/v1/reports/sales`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ category, ...options }),
    });
    return await response.json();
  }
}
```

This guide provides the foundation for integrating with the FastAPI ERP System. For more specific use cases, refer to the interactive documentation at `/docs`.
