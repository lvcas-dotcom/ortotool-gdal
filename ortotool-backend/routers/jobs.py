from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

from workers.tasks import get_job_status, cancel_job, get_worker_status
from models.job import JobResponse, JobStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Get job status and information
    
    Args:
        job_id: Job ID (Celery task ID)
        
    Returns:
        Job status information
    """
    try:
        # Get job status from Celery
        job_info = get_job_status(job_id)
        
        return JobResponse(
            job_id=job_id,
            status=job_info['status'],
            job_type=None,  # We'll need to store this separately if needed
            created_at=datetime.now(),  # Placeholder - should be stored
            progress=job_info.get('progress', 0),
            message=job_info.get('message'),
            error=job_info.get('error'),
            result_file=job_info.get('result_file')
        )
        
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting job status: {str(e)}")


@router.post("/{job_id}/cancel")
async def cancel_job_endpoint(job_id: str):
    """
    Cancel a running job
    
    Args:
        job_id: Job ID (Celery task ID)
        
    Returns:
        Cancellation confirmation
    """
    try:
        # Check if job exists first
        job_info = get_job_status(job_id)
        
        if job_info['status'] in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel job in status: {job_info['status']}"
            )
        
        # Cancel the job
        success = cancel_job(job_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to cancel job")
        
        logger.info(f"Job cancelled: {job_id}")
        return {
            "message": f"Job {job_id} cancelled successfully",
            "job_id": job_id,
            "status": JobStatus.CANCELLED
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error cancelling job: {str(e)}")


@router.get("/")
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by job status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of jobs to return")
):
    """
    List jobs (limited implementation - requires job tracking database)
    
    Args:
        status: Optional status filter
        limit: Maximum number of jobs to return
        
    Returns:
        List of jobs
    """
    try:
        # This is a simplified implementation
        # In a real system, you'd store job information in a database
        
        worker_status = get_worker_status()
        active_tasks = worker_status.get('active_tasks', {})
        
        jobs = []
        
        # Get active jobs from all workers
        for worker_name, tasks in active_tasks.items():
            for task in tasks:
                job_info = {
                    "job_id": task['id'],
                    "status": JobStatus.RUNNING,
                    "job_type": task.get('name', 'unknown'),
                    "worker": worker_name,
                    "created_at": datetime.now(),  # Placeholder
                    "progress": None,
                    "message": "Job is running"
                }
                
                if status is None or job_info['status'] == status:
                    jobs.append(job_info)
        
        # Limit results
        jobs = jobs[:limit]
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "active_workers": len(active_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing jobs: {str(e)}")


@router.get("/worker/status")
async def get_worker_status_endpoint():
    """
    Get Celery worker status information
    
    Returns:
        Worker status and statistics
    """
    try:
        status = get_worker_status()
        
        # Process the status for better readability
        processed_status = {
            "workers": {},
            "queue_length": status.get('queue_length', 0),
            "total_active_tasks": 0
        }
        
        # Process active tasks
        active_tasks = status.get('active_tasks', {})
        for worker_name, tasks in active_tasks.items():
            processed_status['workers'][worker_name] = {
                "active_tasks": len(tasks),
                "tasks": [
                    {
                        "id": task['id'],
                        "name": task.get('name', 'unknown'),
                        "args": task.get('args', []),
                        "kwargs": task.get('kwargs', {})
                    }
                    for task in tasks
                ]
            }
            processed_status['total_active_tasks'] += len(tasks)
        
        # Process worker stats
        stats = status.get('stats', {})
        for worker_name, worker_stats in stats.items():
            if worker_name in processed_status['workers']:
                processed_status['workers'][worker_name]['stats'] = worker_stats
            else:
                processed_status['workers'][worker_name] = {'stats': worker_stats}
        
        # Add registered tasks
        registered = status.get('registered_tasks', {})
        processed_status['registered_tasks'] = registered
        
        return processed_status
        
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting worker status: {str(e)}")


@router.get("/stats/summary")
async def get_job_stats():
    """
    Get job statistics summary
    
    Returns:
        Summary statistics about jobs
    """
    try:
        # This is a simplified implementation
        # In a real system, you'd query job statistics from a database
        
        worker_status = get_worker_status()
        
        stats = {
            "active_jobs": worker_status.get('queue_length', 0),
            "total_workers": len(worker_status.get('stats', {})),
            "available_task_types": [
                "clip_raster_task",
                "reproject_raster_task", 
                "resample_raster_task",
                "mosaic_rasters_task"
            ],
            "system_status": "healthy" if worker_status.get('stats') else "no_workers"
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting job stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting job stats: {str(e)}")


@router.post("/cleanup")
async def cleanup_completed_jobs():
    """
    Clean up completed job results (placeholder)
    
    Returns:
        Cleanup summary
    """
    try:
        # This would clean up old job results from Redis/database
        # For now, it's just a placeholder
        
        logger.info("Job cleanup requested")
        
        return {
            "message": "Job cleanup completed",
            "cleaned_jobs": 0,  # Placeholder
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error during job cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check for the job system
    
    Returns:
        Health status of the job processing system
    """
    try:
        # Check if workers are available
        worker_status = get_worker_status()
        
        has_workers = bool(worker_status.get('stats'))
        active_tasks = sum(
            len(tasks) for tasks in worker_status.get('active_tasks', {}).values()
        )
        
        health_status = {
            "status": "healthy" if has_workers else "degraded",
            "workers_available": has_workers,
            "active_tasks": active_tasks,
            "timestamp": datetime.now(),
            "details": {
                "celery_workers": len(worker_status.get('stats', {})),
                "redis_connection": "unknown",  # Would need to test Redis connection
                "queue_status": "operational" if has_workers else "no_workers"
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }
