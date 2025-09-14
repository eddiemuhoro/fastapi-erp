from fastapi import APIRouter, HTTPException, status
from app.schemas.reports import CustomerReportRequest, StandardResponse
from app.services.customer_service import CustomerReportService
from datetime import date

router = APIRouter()

@router.post("/customers", response_model=StandardResponse)
def get_customer_report(request: CustomerReportRequest):
    """Generate customer reports based on category"""
    
    try:
        if request.category == "overview":
            data = CustomerReportService.get_overview()
            return StandardResponse(success=1, data=data)
            
        elif request.category == "customer_balances":
            data = CustomerReportService.get_customer_balances(request.as_of_date)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "due_invoices":
            from_date = request.from_date or date(2000, 1, 1)
            to_date = request.to_date or date.today()
            data = CustomerReportService.get_due_invoices(from_date, to_date)
            return StandardResponse(success=1, data=data)
            
        elif request.category == "customer_list":
            data = CustomerReportService.get_customer_list()
            return StandardResponse(success=1, data=data)
            
        elif request.category == "aging_summary":
            data = CustomerReportService.get_aging_summary()
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
            detail=f"Error generating customer report: {str(e)}"
        )
