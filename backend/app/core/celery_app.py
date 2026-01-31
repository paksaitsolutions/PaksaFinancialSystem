"""Async task processing with Celery"""
from celery import Celery
from app.core.config import settings

# Initialize Celery
celery_app = Celery(
    "paksa_financial",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Task routes for different queues
celery_app.conf.task_routes = {
    "app.tasks.reports.*": {"queue": "reports"},
    "app.tasks.email.*": {"queue": "email"},
    "app.tasks.calculations.*": {"queue": "calculations"},
    "app.tasks.imports.*": {"queue": "imports"},
}

# Common async tasks
@celery_app.task(name="generate_financial_report")
def generate_financial_report_task(report_type: str, company_id: int, params: dict):
    """Generate financial report asynchronously"""
    from app.services.reports.report_service import ReportService
    service = ReportService()
    return service.generate_report(report_type, company_id, params)

@celery_app.task(name="send_bulk_email")
def send_bulk_email_task(recipients: list, subject: str, body: str):
    """Send bulk emails asynchronously"""
    from app.services.notifications.email_service import EmailService
    service = EmailService()
    return service.send_bulk(recipients, subject, body)

@celery_app.task(name="calculate_payroll")
def calculate_payroll_task(pay_run_id: int):
    """Calculate payroll asynchronously"""
    from app.services.payroll.payroll_service import PayrollService
    service = PayrollService()
    return service.calculate_pay_run(pay_run_id)

@celery_app.task(name="import_transactions")
def import_transactions_task(file_path: str, company_id: int):
    """Import transactions asynchronously"""
    from app.services.imports.transaction_import_service import TransactionImportService
    service = TransactionImportService()
    return service.import_from_file(file_path, company_id)

@celery_app.task(name="reconcile_bank_account")
def reconcile_bank_account_task(account_id: int, statement_data: dict):
    """Reconcile bank account asynchronously"""
    from app.services.cash.reconciliation_service import ReconciliationService
    service = ReconciliationService()
    return service.auto_reconcile(account_id, statement_data)

# Periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "update-exchange-rates": {
        "task": "update_exchange_rates",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "cleanup-old-sessions": {
        "task": "cleanup_sessions",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "generate-daily-reports": {
        "task": "generate_daily_reports",
        "schedule": crontab(hour=6, minute=0),  # Daily at 6 AM
    },
}
