from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import io
import csv

from ....core.database import get_db
from ....services.gl.trial_balance_service import TrialBalanceService
from ....schemas.gl.trial_balance import TrialBalanceParams

router = APIRouter()

@router.get("/trial-balance", response_model=None)
async def get_trial_balance(
    start_date: date = Query(..., description="Start date of the reporting period"),
    end_date: date = Query(..., description="End date of the reporting period"),
    include_zeros: bool = Query(False, description="Include accounts with zero balance"),
    format: str = Query("json", description="Output format (json, csv, excel)"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate a trial balance report for the specified date range.
    """
    try:
        # Get trial balance data
        trial_balance = TrialBalanceService.get_trial_balance(
            db=db,
            start_date=start_date,
            end_date=end_date,
            include_zeros=include_zeros
        )
        
        # Return in requested format
        if format.lower() == 'json':
            return trial_balance
            
        elif format.lower() in ['csv', 'excel']:
            # Convert to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Account Code', 'Account Name', 'Account Type',
                'Opening Balance', 'Period Activity', 'Ending Balance',
                'Debit Amount', 'Credit Amount'
            ])
            
            # Write data rows
            for entry in trial_balance.entries:
                writer.writerow([
                    entry.account_code,
                    entry.account_name,
                    entry.account_type,
                    entry.opening_balance,
                    entry.period_activity,
                    entry.ending_balance,
                    entry.debit_amount,
                    entry.credit_amount
                ])
            
            # Write totals
            writer.writerow([])
            writer.writerow(['', '', 'TOTALS:', '', '', '', 
                           trial_balance.total_debit, trial_balance.total_credit])
            
            # Prepare response
            output.seek(0)
            
            if format.lower() == 'csv':
                return Response(
                    content=output.getvalue(),
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment;filename=trial_balance_{start_date}_to_{end_date}.csv"}
                )
            else:  # excel
                # For Excel, we'd typically use openpyxl or similar
                # This is a simplified version that returns CSV with .xlsx extension
                return Response(
                    content=output.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment;filename=trial_balance_{start_date}_to_{end_date}.xlsx"}
                )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}. Supported formats are: json, csv, excel"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating trial balance: {str(e)}"
        )
