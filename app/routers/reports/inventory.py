from fastapi import APIRouter, HTTPException, status
from app.schemas.reports import InventoryReportRequest, StandardResponse
from app.services.inventory_service import InventoryReportService
from datetime import date

router = APIRouter()

@router.post("/inventory", response_model=StandardResponse)
def get_inventory_report(request: InventoryReportRequest):
    """Generate inventory reports based on category"""
    
    try:
        if request.category == "summary":
            data = InventoryReportService.get_summary()
            return StandardResponse(success=1, data=data)
            
        elif request.category == "stock_levels":
            data = InventoryReportService.get_stock_levels(request.location_id)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "low_stock":
            threshold = request.threshold or 10
            data = InventoryReportService.get_low_stock(threshold)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "overstock":
            threshold = request.threshold or 100
            data = InventoryReportService.get_overstock(threshold)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "top_selling":
            from_date = request.from_date or date.today().replace(day=1)
            to_date = request.to_date or date.today()
            limit = request.limit or 5
            data = InventoryReportService.get_top_selling(from_date, to_date, limit)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "slow_moving":
            from_date = request.from_date or date.today().replace(day=1)
            to_date = request.to_date or date.today()
            limit = request.limit or 5
            data = InventoryReportService.get_slow_moving(from_date, to_date, limit)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "negative_quantities":
            data = InventoryReportService.get_negative_quantities()
            return StandardResponse(success=1, data=data)
            
        elif request.category == "turnover_rate":
            from_date = request.fromdate or date.today().replace(day=1)
            to_date = request.todate or date.today()
            data = InventoryReportService.get_turnover_rate(from_date, to_date)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "incoming_stock":
            from_date = request.from_date or date.today().replace(day=1)
            to_date = request.to_date or date.today()
            data = InventoryReportService.get_incoming_stock(from_date, to_date, request.location)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "outgoing_stock":
            from_date = request.from_date or date.today().replace(month=date.today().month-1)
            to_date = request.to_date or date.today()
            data = InventoryReportService.get_outgoing_stock(from_date, to_date)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "dead_stock":
            from_date = request.from_date or date.today().replace(day=1)
            to_date = request.to_date or date.today()
            data = InventoryReportService.get_dead_stock(from_date, to_date, request.location)
            return StandardResponse(success=1, data=data)
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating inventory report: {str(e)}"
        )
