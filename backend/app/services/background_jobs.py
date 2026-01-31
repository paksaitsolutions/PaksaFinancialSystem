"""
Background job processing system.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Callable, Optional
import asyncio
import json

from enum import Enum
import uuid

from app.core.cache import cache_manager
from app.core.logging import logger



class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class BackgroundJob:
    """Background job definition."""
    
    def __init__(
        self,
        job_id: str,
        job_type: str,
        payload: Dict[str, Any],
        tenant_id: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 60
    ):
        """  Init  ."""
        self.job_id = job_id
        self.job_type = job_type
        self.payload = payload
        self.tenant_id = tenant_id
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.status = JobStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.retry_count = 0

class JobQueue:
    """Background job queue manager."""
    
    def __init__(self):
        """  Init  ."""
        self.jobs: Dict[str, BackgroundJob] = {}
        self.job_handlers: Dict[str, Callable] = {}
        self.running = False
        self.worker_tasks = []
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register Handler."""
        """Register job handler."""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered job handler: {job_type}")
    
    async def enqueue(
        self,
        job_type: str,
        payload: Dict[str, Any],
        tenant_id: Optional[str] = None,
        delay: int = 0
    ) -> str:
        """Enqueue."""
        """Enqueue background job."""
        job_id = str(uuid.uuid4())
        job = BackgroundJob(job_id, job_type, payload, tenant_id)
        
        if delay > 0:
            job.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
        
        self.jobs[job_id] = job
        
        # Store in cache for persistence
        await cache_manager.set(f"job:{job_id}", {
            "job_id": job_id,
            "job_type": job_type,
            "payload": payload,
            "tenant_id": tenant_id,
            "status": job.status.value,
            "created_at": job.created_at.isoformat()
        }, ttl=86400)  # 24 hours
        
        logger.info(f"Enqueued job {job_id} of type {job_type}")
        return job_id
    
    async def start_workers(self, num_workers: int = 3):
        """Start Workers."""
        """Start background workers."""
        self.running = True
        
        for i in range(num_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(task)
        
        logger.info(f"Started {num_workers} background workers")
    
    async def stop_workers(self):
        """Stop Workers."""
        """Stop background workers."""
        self.running = False
        
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        logger.info("Stopped background workers")
    
    async def _worker(self, worker_name: str):
        """Worker."""
        """Background worker process."""
        logger.info(f"Worker {worker_name} started")
        
        while self.running:
            try:
                job = await self._get_next_job()
                if job:
                    await self._process_job(job, worker_name)
                else:
                    await asyncio.sleep(1)  # No jobs available
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _get_next_job(self) -> Optional[BackgroundJob]:
        """Get Next Job."""
        """Get next pending job."""
        for job in self.jobs.values():
            if job.status == JobStatus.PENDING:
                scheduled_at = getattr(job, 'scheduled_at', None)
                if not scheduled_at or datetime.utcnow() >= scheduled_at:
                    return job
        return None
    
    async def _process_job(self, job: BackgroundJob, worker_name: str):
        """Process Job."""
        """Process a background job."""
        if job.job_type not in self.job_handlers:
            logger.error(f"No handler for job type: {job.job_type}")
            job.status = JobStatus.FAILED
            job.error_message = f"No handler for job type: {job.job_type}"
            return
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        logger.info(f"Worker {worker_name} processing job {job.job_id}")
        
        try:
            handler = self.job_handlers[job.job_type]
            await handler(job.payload, job.tenant_id)
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            job.error_message = str(e)
            
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.RETRYING
                job.scheduled_at = datetime.utcnow() + timedelta(seconds=job.retry_delay)
                
                logger.warning(f"Job {job.job_id} failed, retrying ({job.retry_count}/{job.max_retries})")
            else:
                job.status = JobStatus.FAILED
                logger.error(f"Job {job.job_id} failed permanently: {str(e)}")
        
        # Update cache
        await self._update_job_cache(job)
    
    async def _update_job_cache(self, job: BackgroundJob):
        """Update Job Cache."""
        """Update job status in cache."""
        await cache_manager.set(f"job:{job.job_id}", {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status.value,
            "error_message": job.error_message,
            "retry_count": job.retry_count,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }, ttl=86400)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get Job Status."""
        """Get job status."""
        return await cache_manager.get(f"job:{job_id}")

# Global job queue
job_queue = JobQueue()

# Register default job handlers
async def send_email_job(payload: Dict[str, Any], tenant_id: Optional[str]):
        """Send Email Job."""
    """Send email job handler."""
    logger.info(f"Sending email to {payload.get('recipient')}")
    await asyncio.sleep(2)  # Simulate email sending

async def generate_report_job(payload: Dict[str, Any], tenant_id: Optional[str]):
        """Generate Report Job."""
    """Generate report job handler."""
    logger.info(f"Generating report {payload.get('report_type')}")
    await asyncio.sleep(5)  # Simulate report generation

async def sync_data_job(payload: Dict[str, Any], tenant_id: Optional[str]):
        """Sync Data Job."""
    """Data sync job handler."""
    logger.info(f"Syncing data for tenant {tenant_id}")
    await asyncio.sleep(3)  # Simulate data sync

# Register handlers
job_queue.register_handler("send_email", send_email_job)
job_queue.register_handler("generate_report", generate_report_job)
job_queue.register_handler("sync_data", sync_data_job)