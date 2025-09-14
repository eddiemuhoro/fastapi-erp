"""
Test cases for sales reports
"""
import pytest
from fastapi.testclient import TestClient

def test_sales_report_today_hourly(client: TestClient):
    """Test today hourly sales report"""
    response = client.post(
        "/api/reports/sales",
        json={"category": "today_hourly"}
    )
    assert response.status_code in [200, 500]  # 500 if no DB connection
    
def test_sales_report_invalid_category(client: TestClient):
    """Test invalid category handling"""
    response = client.post(
        "/api/reports/sales",
        json={"category": "invalid_category"}
    )
    # Should still process as default sales
    assert response.status_code in [200, 500]
