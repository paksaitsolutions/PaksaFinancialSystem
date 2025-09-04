"""
Reports API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_enhanced import get_current_user
from app.services.reporting_engine import *
from typing import Optional, Dict, List
from datetime import date, datetime
import os

router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Financial Statement Generation
@router.get("/trial-balance")
async def generate_trial_balance(
    as_of_date: Optional[date] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate trial balance report"""
    try:
        data = ReportGenerator.generate_trial_balance(db, as_of_date)
        
        if format.lower() == "pdf":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/trial_balance_{timestamp}.pdf"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            PDFReportGenerator.create_pdf_report(data, output_path)
            return FileResponse(output_path, filename=f"trial_balance_{timestamp}.pdf")
        
        elif format.lower() == "excel":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/trial_balance_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ExcelReportGenerator.create_excel_report(data, output_path)
            return FileResponse(output_path, filename=f"trial_balance_{timestamp}.xlsx")
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance-sheet")
async def generate_balance_sheet(
    as_of_date: Optional[date] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate balance sheet report"""
    try:
        data = ReportGenerator.generate_balance_sheet(db, as_of_date)
        
        if format.lower() == "pdf":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/balance_sheet_{timestamp}.pdf"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            PDFReportGenerator.create_pdf_report(data, output_path)
            return FileResponse(output_path, filename=f"balance_sheet_{timestamp}.pdf")
        
        elif format.lower() == "excel":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/balance_sheet_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ExcelReportGenerator.create_excel_report(data, output_path)
            return FileResponse(output_path, filename=f"balance_sheet_{timestamp}.xlsx")
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/income-statement")
async def generate_income_statement(
    start_date: date,
    end_date: date,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate profit & loss statement"""
    try:
        data = ReportGenerator.generate_income_statement(db, start_date, end_date)
        
        if format.lower() == "pdf":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/income_statement_{timestamp}.pdf"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            PDFReportGenerator.create_pdf_report(data, output_path)
            return FileResponse(output_path, filename=f"income_statement_{timestamp}.pdf")
        
        elif format.lower() == "excel":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/income_statement_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ExcelReportGenerator.create_excel_report(data, output_path)
            return FileResponse(output_path, filename=f"income_statement_{timestamp}.xlsx")
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cash-flow")
async def generate_cash_flow(
    start_date: date,
    end_date: date,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate cash flow statement"""
    try:
        data = ReportGenerator.generate_cash_flow(db, start_date, end_date)
        
        if format.lower() == "pdf":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/cash_flow_{timestamp}.pdf"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            PDFReportGenerator.create_pdf_report(data, output_path)
            return FileResponse(output_path, filename=f"cash_flow_{timestamp}.pdf")
        
        elif format.lower() == "excel":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/cash_flow_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ExcelReportGenerator.create_excel_report(data, output_path)
            return FileResponse(output_path, filename=f"cash_flow_{timestamp}.xlsx")
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Report Scheduling
@router.post("/schedule")
async def schedule_report(
    template_id: str,
    schedule_config: Dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Schedule a report for automatic generation"""
    try:
        run_id = ReportScheduler.schedule_report(db, template_id, schedule_config, current_user.id)
        return {"message": "Report scheduled successfully", "run_id": run_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-scheduled")
async def execute_scheduled_reports(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Execute all pending scheduled reports"""
    try:
        executed_reports = ReportScheduler.execute_scheduled_reports(db)
        return {"message": f"Executed {len(executed_reports)} reports", "report_ids": executed_reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduled")
async def get_scheduled_reports(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all scheduled reports"""
    try:
        from app.models.financial_core import ReportRun
        
        scheduled_reports = db.query(ReportRun).filter(
            ReportRun.created_by == current_user.id
        ).order_by(ReportRun.created_at.desc()).all()
        
        return [{
            "id": report.id,
            "template_id": report.template_id,
            "run_date": report.run_date,
            "status": report.status,
            "file_path": report.file_path,
            "created_at": report.created_at
        } for report in scheduled_reports]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Custom Report Builder
@router.get("/builder/fields")
async def get_available_fields():
    """Get available fields for custom report builder"""
    return CustomReportBuilder.get_available_fields()

@router.post("/templates")
async def create_report_template(
    template_config: Dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create custom report template"""
    try:
        template_id = CustomReportBuilder.create_custom_report_template(
            db, template_config, current_user.id
        )
        return {"message": "Template created successfully", "template_id": template_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_report_templates(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all report templates"""
    try:
        from app.models.financial_core import ReportTemplate
        
        templates = db.query(ReportTemplate).filter(
            ReportTemplate.is_active == True
        ).order_by(ReportTemplate.created_at.desc()).all()
        
        return [{
            "id": template.id,
            "report_name": template.report_name,
            "report_type": template.report_type,
            "created_at": template.created_at,
            "is_active": template.is_active
        } for template in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_report_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific report template"""
    try:
        from app.models.financial_core import ReportTemplate
        
        template = db.query(ReportTemplate).filter(
            ReportTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.id,
            "report_name": template.report_name,
            "report_type": template.report_type,
            "template_data": json.loads(template.template_data) if template.template_data else {},
            "created_at": template.created_at,
            "is_active": template.is_active
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom/{template_id}")
async def generate_custom_report(
    template_id: str,
    parameters: Optional[Dict] = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate report from custom template"""
    try:
        data = CustomReportBuilder.generate_custom_report(db, template_id, parameters)
        
        if format.lower() == "pdf":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/custom_{timestamp}.pdf"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            PDFReportGenerator.create_pdf_report(data, output_path)
            return FileResponse(output_path, filename=f"custom_report_{timestamp}.pdf")
        
        elif format.lower() == "excel":
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"reports/custom_{timestamp}.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ExcelReportGenerator.create_excel_report(data, output_path)
            return FileResponse(output_path, filename=f"custom_report_{timestamp}.xlsx")
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Report Management
@router.get("/files")
async def list_report_files():
    """List all generated report files"""
    try:
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            return []
        
        files = []
        for filename in os.listdir(reports_dir):
            if filename.endswith(('.pdf', '.xlsx')):
                file_path = os.path.join(reports_dir, filename)
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(files, key=lambda x: x['created'], reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{filename}")
async def download_report_file(filename: str):
    """Download a specific report file"""
    try:
        file_path = os.path.join("reports", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(file_path, filename=filename)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{filename}")
async def delete_report_file(
    filename: str,
    current_user = Depends(get_current_user)
):
    """Delete a report file"""
    try:
        file_path = os.path.join("reports", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(file_path)
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Report Analytics
@router.get("/analytics")
async def get_report_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get report generation analytics"""
    try:
        from app.models.financial_core import ReportRun
        
        # Report counts by status
        total_reports = db.query(ReportRun).count()
        completed_reports = db.query(ReportRun).filter(ReportRun.status == 'completed').count()
        failed_reports = db.query(ReportRun).filter(ReportRun.status == 'failed').count()
        scheduled_reports = db.query(ReportRun).filter(ReportRun.status == 'scheduled').count()
        
        # Recent activity
        recent_reports = db.query(ReportRun).order_by(
            ReportRun.created_at.desc()
        ).limit(10).all()
        
        return {
            "summary": {
                "total_reports": total_reports,
                "completed_reports": completed_reports,
                "failed_reports": failed_reports,
                "scheduled_reports": scheduled_reports,
                "success_rate": (completed_reports / total_reports * 100) if total_reports > 0 else 0
            },
            "recent_activity": [{
                "id": report.id,
                "template_id": report.template_id,
                "status": report.status,
                "run_date": report.run_date,
                "created_at": report.created_at
            } for report in recent_reports]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))