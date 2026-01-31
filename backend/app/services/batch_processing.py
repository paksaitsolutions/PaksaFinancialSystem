"""
Batch processing system for bulk operations.
"""
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
import asyncio

import uuid

from app.core.logging import logger
from app.services.background_jobs import job_queue



class BatchProcessor:
    """Batch processing manager for bulk operations."""
    
    def __init__(self, batch_size: int = 100):
        """  Init  ."""
        self.batch_size = batch_size
        self.processors: Dict[str, Callable] = {}
    
    def register_processor(self, operation_type: str, processor: Callable):
        """Register Processor."""
        """Register batch processor."""
        self.processors[operation_type] = processor
        logger.info(f"Registered batch processor: {operation_type}")
    
    async def process_batch(
        """Process Batch."""
        self,
        operation_type: str,
        items: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
        chunk_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process Batch."""
        """Process items in batches."""
        if operation_type not in self.processors:
            raise ValueError(f"No processor registered for: {operation_type}")
        
        chunk_size = chunk_size or self.batch_size
        processor = self.processors[operation_type]
        
        batch_id = str(uuid.uuid4())
        total_items = len(items)
        processed_items = 0
        failed_items = 0
        results = []
        
        logger.info(f"Starting batch {batch_id}: {total_items} items, chunk size {chunk_size}")
        
        # Process items in chunks
        for i in range(0, total_items, chunk_size):
            chunk = items[i:i + chunk_size]
            
            try:
                chunk_results = await processor(chunk, tenant_id)
                results.extend(chunk_results)
                processed_items += len(chunk)
                
                logger.info(f"Batch {batch_id}: Processed chunk {i//chunk_size + 1}, items {processed_items}/{total_items}")
                
            except Exception as e:
                failed_items += len(chunk)
                logger.error(f"Batch {batch_id}: Chunk {i//chunk_size + 1} failed: {str(e)}")
                
                # Add failed items to results
                for item in chunk:
                    results.append({
                        "item": item,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return {
            "batch_id": batch_id,
            "total_items": total_items,
            "processed_items": processed_items,
            "failed_items": failed_items,
            "success_rate": (processed_items / total_items) * 100 if total_items > 0 else 0,
            "results": results
        }
    
    async def schedule_batch_job(
        """Schedule Batch Job."""
        self,
        operation_type: str,
        items: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
        delay: int = 0
    ) -> str:
        """Schedule Batch Job."""
        """Schedule batch processing as background job."""
        job_id = await job_queue.enqueue(
            "batch_processing",
            {
                "operation_type": operation_type,
                "items": items,
                "tenant_id": tenant_id
            },
            tenant_id=tenant_id,
            delay=delay
        )
        
        logger.info(f"Scheduled batch job {job_id} for {len(items)} items")
        return job_id

# Global batch processor
batch_processor = BatchProcessor()

# Batch processing job handler
async def batch_processing_job(payload: Dict[str, Any], tenant_id: Optional[str]):
        """Batch Processing Job."""
    """Background job handler for batch processing."""
    operation_type = payload["operation_type"]
    items = payload["items"]
    
    result = await batch_processor.process_batch(
        operation_type, items, tenant_id
    )
    
    logger.info(f"Batch job completed: {result['success_rate']:.1f}% success rate")

# Register batch processing job handler
job_queue.register_handler("batch_processing", batch_processing_job)

# Default batch processors
async def bulk_invoice_processor(items: List[Dict[str, Any]], tenant_id: Optional[str]) -> List[Dict[str, Any]]:
        """Bulk Invoice Processor."""
    """Process bulk invoice creation."""
    results = []
    
    for item in items:
        try:
            # Simulate invoice creation
            await asyncio.sleep(0.1)
            
            results.append({
                "item": item,
                "status": "success",
                "invoice_id": str(uuid.uuid4())
            })
            
        except Exception as e:
            results.append({
                "item": item,
                "status": "failed",
                "error": str(e)
            })
    
    return results

async def bulk_payment_processor(items: List[Dict[str, Any]], tenant_id: Optional[str]) -> List[Dict[str, Any]]:
        """Bulk Payment Processor."""
    """Process bulk payments."""
    results = []
    
    for item in items:
        try:
            # Simulate payment processing
            await asyncio.sleep(0.2)
            
            results.append({
                "item": item,
                "status": "success",
                "payment_id": str(uuid.uuid4())
            })
            
        except Exception as e:
            results.append({
                "item": item,
                "status": "failed",
                "error": str(e)
            })
    
    return results

async def bulk_employee_import_processor(items: List[Dict[str, Any]], tenant_id: Optional[str]) -> List[Dict[str, Any]]:
        """Bulk Employee Import Processor."""
    """Process bulk employee import."""
    results = []
    
    for item in items:
        try:
            # Simulate employee creation
            await asyncio.sleep(0.05)
            
            results.append({
                "item": item,
                "status": "success",
                "employee_id": str(uuid.uuid4())
            })
            
        except Exception as e:
            results.append({
                "item": item,
                "status": "failed",
                "error": str(e)
            })
    
    return results

# Register batch processors
batch_processor.register_processor("bulk_invoices", bulk_invoice_processor)
batch_processor.register_processor("bulk_payments", bulk_payment_processor)
batch_processor.register_processor("bulk_employee_import", bulk_employee_import_processor)