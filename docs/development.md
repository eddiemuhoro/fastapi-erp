# Development Guide

This guide covers development workflows, coding standards, and best practices for contributing to the FastAPI ERP System.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Debugging](#debugging)
- [Contributing](#contributing)

## Development Environment Setup

### Prerequisites

- Python 3.7+
- MySQL 5.5+ or MySQL 8.0+
- Git
- VS Code (recommended) or your preferred IDE

### Initial Setup

1. **Clone and setup the project**:

```bash
git clone <repository-url>
cd fastapi-mysql-app
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

2. **Configure environment**:

```bash
copy .env.example .env
# Edit .env with your database credentials
```

3. **Install development dependencies**:

```bash
pip install -r requirements-dev.txt  # If exists
# Or install individually:
pip install pytest pytest-cov black flake8 mypy
```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

#### VS Code Extensions

Recommended extensions:

- Python
- Python Docstring Generator
- GitLens
- MySQL
- REST Client
- Thunder Client

## Project Structure

### Folder Organization

```
fastapi-mysql-app/
├── app/                     # Main application package
│   ├── __init__.py
│   ├── main.py             # FastAPI app instance
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connections
│   ├── database_v2.py      # Enhanced DB with pooling
│   ├── auth.py             # Authentication utilities
│   ├── routers/            # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication routes
│   │   ├── customers.py    # Customer routes
│   │   ├── inventory.py    # Inventory routes
│   │   └── reports.py      # Report routes
│   ├── services/           # Business logic layer
│   │   ├── __init__.py
│   │   ├── sales_service.py
│   │   ├── customer_service.py
│   │   └── inventory_service.py
│   ├── schemas/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── inventory.py
│   │   └── sales.py
│   ├── middleware/         # Custom middleware
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── error_handling.py
│   ├── exceptions/         # Custom exceptions
│   │   ├── __init__.py
│   │   └── api_exceptions.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── date_utils.py
│       └── validators.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_inventory.py
│   └── test_reports.py
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Container configuration
└── README.md              # Project documentation
```

### Architecture Layers

1. **Routers Layer** (`app/routers/`):

   - Handle HTTP requests/responses
   - Input validation
   - Route to appropriate services
   - Return formatted responses

2. **Services Layer** (`app/services/`):

   - Business logic implementation
   - Data processing
   - Coordinate multiple data sources
   - Apply business rules

3. **Database Layer** (`app/database.py`):

   - Database connections
   - Query execution
   - Connection pooling
   - Transaction management

4. **Schemas Layer** (`app/schemas/`):
   - Request/response models
   - Data validation
   - Type definitions
   - Documentation

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specific guidelines:

1. **Line Length**: 88 characters (Black default)
2. **Imports**: Use absolute imports, group by standard/third-party/local
3. **Naming**:
   - Functions and variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_CASE`
   - Private methods: `_private_method`

### Code Formatting

Use Black for automatic formatting:

```bash
black app/ tests/
```

### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

def get_customers(limit: int = 10) -> List[Dict[str, Any]]:
    """Get list of customers with limit."""
    pass

class CustomerSchema(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
```

### Documentation

Use docstrings for all functions and classes:

```python
def calculate_sales_summary(
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Calculate sales summary for given date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary containing sales summary data

    Raises:
        ValueError: If date format is invalid
        DatabaseError: If database query fails
    """
    pass
```

## Development Workflow

### Feature Development

1. **Create feature branch**:

```bash
git checkout -b feature/customer-search
```

2. **Implement feature**:

   - Write tests first (TDD approach)
   - Implement business logic in services
   - Add API endpoints in routers
   - Update schemas as needed

3. **Test your changes**:

```bash
pytest tests/
pytest --cov=app tests/  # With coverage
```

4. **Format and lint**:

```bash
black app/ tests/
flake8 app/ tests/
mypy app/
```

5. **Commit and push**:

```bash
git add .
git commit -m "Add customer search functionality"
git push origin feature/customer-search
```

### Adding New API Endpoints

1. **Define schema** in `app/schemas/`:

```python
# app/schemas/customer.py
from pydantic import BaseModel
from typing import Optional

class CustomerSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
```

2. **Implement service** in `app/services/`:

```python
# app/services/customer_service.py
from typing import List, Dict, Any
from app.database import execute_query

class CustomerService:
    @staticmethod
    def search_customers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search customers by name or email."""
        sql = """
        SELECT id, name, email
        FROM customers
        WHERE name LIKE %s OR email LIKE %s
        LIMIT %s
        """
        search_term = f"%{query}%"
        return execute_query(sql, (search_term, search_term, limit))
```

3. **Add router endpoint** in `app/routers/`:

```python
# app/routers/customers.py
from fastapi import APIRouter, HTTPException
from app.schemas.customer import CustomerSearchRequest, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/search", response_model=List[CustomerResponse])
async def search_customers(request: CustomerSearchRequest):
    """Search for customers by name or email."""
    try:
        results = CustomerService.search_customers(
            request.query,
            request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

4. **Write tests** in `tests/`:

```python
# tests/test_customers.py
def test_search_customers(client):
    response = client.post(
        "/api/v1/customers/search",
        json={"query": "john", "limit": 5}
    )
    assert response.status_code == 200
    assert len(response.json()) <= 5
```

### Database Changes

1. **Create migration script** in `scripts/migrations/`:

```python
# scripts/migrations/001_add_customer_index.py
def upgrade():
    """Add index on customer name for faster searches."""
    return """
    CREATE INDEX idx_customers_name ON customers(name);
    CREATE INDEX idx_customers_email ON customers(email);
    """

def downgrade():
    """Remove customer indexes."""
    return """
    DROP INDEX idx_customers_name ON customers;
    DROP INDEX idx_customers_email ON customers;
    """
```

2. **Test with local database first**
3. **Document the change**
4. **Plan production deployment**

## Testing

### Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_auth.py         # Authentication tests
├── test_customers.py    # Customer endpoint tests
├── test_inventory.py    # Inventory endpoint tests
├── test_reports.py      # Report endpoint tests
├── test_services/       # Service layer tests
│   ├── test_customer_service.py
│   └── test_sales_service.py
└── test_utils/          # Utility function tests
    └── test_validators.py
```

### Test Configuration

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def test_user():
    """Test user fixture."""
    return {
        "username": "testuser",
        "password": "testpass"
    }
```

### Writing Tests

```python
# tests/test_customers.py
import pytest

def test_get_customers(client):
    """Test getting customer list."""
    response = client.get("/api/v1/customers/")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_customer_not_found(client):
    """Test getting non-existent customer."""
    response = client.get("/api/v1/customers/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_customer_service():
    """Test customer service directly."""
    from app.services.customer_service import CustomerService

    customers = CustomerService.get_customers(limit=5)
    assert len(customers) <= 5
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_customers.py

# Run with coverage
pytest --cov=app tests/

# Run tests matching pattern
pytest -k "customer" tests/

# Verbose output
pytest -v tests/

# Stop on first failure
pytest -x tests/
```

## Debugging

### Local Debugging

1. **Enable debug mode** in `.env`:

```
DEBUG=True
```

2. **Use Python debugger**:

```python
import pdb; pdb.set_trace()
# Or
import ipdb; ipdb.set_trace()  # Enhanced debugger
```

3. **FastAPI debug mode**:

```python
# app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, debug=True)
```

### Logging

Configure logging in `app/config.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

Use in your code:

```python
from app.config import logger

def get_customers():
    logger.info("Fetching customers from database")
    try:
        # Database operation
        logger.info(f"Retrieved {len(customers)} customers")
        return customers
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise
```

### Database Debugging

1. **Enable SQL logging**:

```python
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        # ... connection params
        use_unicode=True,
        charset='utf8mb4',
        sql_mode='STRICT_TRANS_TABLES',
        autocommit=False
    )
    if DEBUG:
        # Log all queries
        conn.set_converter_class(mysql.connector.MySQLConverter)
    return conn
```

2. **Query profiling**:

```python
import time

def execute_query_with_timing(query, params=None):
    start_time = time.time()
    result = execute_query(query, params)
    end_time = time.time()
    logger.info(f"Query took {end_time - start_time:.3f} seconds: {query[:100]}...")
    return result
```

## Contributing

### Code Review Process

1. **Self-review checklist**:

   - [ ] Code follows style guidelines
   - [ ] Tests are written and passing
   - [ ] Documentation is updated
   - [ ] No hardcoded values
   - [ ] Error handling is implemented
   - [ ] Logging is appropriate

2. **Pull Request template**:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### Release Process

1. **Version bumping**: Follow semantic versioning
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Full test suite on staging
4. **Documentation**: Update API docs
5. **Deployment**: Follow deployment guide

This development guide ensures consistent, high-quality code across the project. Always refer to this guide when contributing to the FastAPI ERP System.
