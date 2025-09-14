from fastapi import APIRouter, HTTPException, status
from app.schemas.reports import SalesReportRequest, StandardResponse
from app.services.sales_service import SalesReportService
from datetime import date

router = APIRouter()

@router.post("/sales", response_model=StandardResponse)
def get_sales_report(request: SalesReportRequest):
    """Generate sales reports based on category"""
    
    try:
        # Set default dates if not provided
        from_date = request.fromdate or date.today()
        to_date = request.todate or date.today()
        
        if request.category == "today_hourly":
            data = SalesReportService.get_today_hourly_sales()
        elif request.category == "rep":
            data = SalesReportService.get_rep_sales(from_date, to_date)
        elif request.category == "location":
            data = SalesReportService.get_location_sales(from_date, to_date)
        elif request.category == "route":
            data = SalesReportService.get_route_sales(from_date, to_date)
        elif request.category == "category":
            data = SalesReportService.get_category_sales(from_date, to_date)
        elif request.category == "item":
            data = SalesReportService.get_item_sales(from_date, to_date)
        elif request.category == "item_trend":
            if not request.filter_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="filter_name is required for item_trend category"
                )
            data = SalesReportService.get_item_trend(request.filter_name)
        elif request.category == "customer":
            data = SalesReportService.get_customer_sales(from_date, to_date)
        elif request.category == "inventory":
            data = SalesReportService.get_inventory_sales(from_date, to_date)
        else:
            # Default sales report
            data = SalesReportService.get_default_sales(from_date, to_date)
        
        return StandardResponse(success=1, data=data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating sales report: {str(e)}"
        )
