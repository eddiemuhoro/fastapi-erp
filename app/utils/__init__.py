"""
Utility functions for the application
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
import json

def setup_logging(level: str = "INFO"):
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

def serialize_datetime(obj: Any) -> Any:
    """JSON serializer for datetime objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency with proper symbols"""
    return f"{currency} {amount:,.2f}"

class DateHelper:
    @staticmethod
    def get_date_range(period: str) -> tuple[date, date]:
        """Get date range for common periods"""
        today = date.today()
        
        if period == "today":
            return today, today
        elif period == "yesterday":
            yesterday = today.replace(day=today.day - 1)
            return yesterday, yesterday
        elif period == "this_week":
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == "this_month":
            start = today.replace(day=1)
            return start, today
        elif period == "last_month":
            if today.month == 1:
                start = today.replace(year=today.year - 1, month=12, day=1)
                end = today.replace(day=1) - timedelta(days=1)
            else:
                start = today.replace(month=today.month - 1, day=1)
                end = today.replace(day=1) - timedelta(days=1)
            return start, end
        else:
            return today, today
