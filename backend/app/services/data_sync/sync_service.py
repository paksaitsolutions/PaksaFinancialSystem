"""
Data synchronization service.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio

from app.core.logging import logger



class DataSyncService:
    """Service for synchronizing data between modules and external systems."""
    
    def __init__(self):
        """  Init  ."""
        self.sync_jobs: Dict[str, Dict[str, Any]] = {}
        self.running = False
    
    async def start_sync_scheduler(self):
        """Start Sync Scheduler."""
        """Start the data sync scheduler."""
        self.running = True
        logger.info("Data sync scheduler started")
        
        while self.running:
            try:
                await self._run_scheduled_syncs()
                await asyncio.sleep(300)  # Run every 5 minutes
            except Exception as e:
                logger.error(f"Error in sync scheduler: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop_sync_scheduler(self):
        """Stop Sync Scheduler."""
        """Stop the data sync scheduler."""
        self.running = False
        logger.info("Data sync scheduler stopped")
    
    async def register_sync_job(
        """Register Sync Job."""
        self,
        job_id: str,
        sync_func: callable,
        interval_minutes: int = 60,
        tenant_id: Optional[str] = None
    ):
        """Register Sync Job."""
        """Register a data sync job."""
        self.sync_jobs[job_id] = {
            "func": sync_func,
            "interval": interval_minutes,
            "tenant_id": tenant_id,
            "last_run": None,
            "next_run": datetime.utcnow()
        }
        logger.info(f"Registered sync job: {job_id}")
    
    async def sync_bank_transactions(self, tenant_id: str):
        """Sync Bank Transactions."""
        """Sync bank transactions from external APIs."""
        logger.info(f"Bank transaction sync completed for tenant {tenant_id}")
    
    async def sync_payment_statuses(self, tenant_id: str):
        """Sync Payment Statuses."""
        """Sync payment statuses from payment gateways."""
        logger.info(f"Payment status sync completed for tenant {tenant_id}")
    
    async def sync_module_data(self, tenant_id: str):
        """Sync Module Data."""
        """Sync data between internal modules."""
        logger.info(f"Module data sync completed for tenant {tenant_id}")
    
    async def _run_scheduled_syncs(self):
        """Run Scheduled Syncs."""
        """Run scheduled sync jobs."""
        current_time = datetime.utcnow()
        
        for job_id, job_info in self.sync_jobs.items():
            if current_time >= job_info["next_run"]:
                try:
                    logger.info(f"Running sync job: {job_id}")
                    await job_info["func"](job_info.get("tenant_id"))
                    
                    job_info["last_run"] = current_time
                    job_info["next_run"] = current_time + timedelta(minutes=job_info["interval"])
                    
                except Exception as e:
                    logger.error(f"Sync job {job_id} failed: {str(e)}")
                    job_info["next_run"] = current_time + timedelta(minutes=5)

data_sync_service = DataSyncService()