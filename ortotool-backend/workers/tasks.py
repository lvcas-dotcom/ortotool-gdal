import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from celery import Celery
from celery.result import AsyncResult

from config.settings import settings
from services.clip import ClipService
from services.reproject import ReprojectService
from services.resample import ResampleService
from services.mosaic import MosaicService
from models.job import JobStatus, JobType

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "geo_processor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.job_timeout,
    task_soft_time_limit=settings.job_timeout - 60,  # 1 minute before hard limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,
    task_max_retries=3,
    result_expires=3600,  # 1 hour
)


@celery_app.task(bind=True, name='clip_raster_task')
def clip_raster_task(self, raster_file: str, vector_file: str, output_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Celery task for clipping raster by vector
    
    Args:
        raster_file: Path to raster file
        vector_file: Path to vector file
        output_name: Optional output filename
        
    Returns:
        Dictionary with task result
    """
    task_id = self.request.id
    logger.info(f"Starting clip task {task_id}")
    
    try:
        # Update task status
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 0, 'message': 'Starting clip operation...'}
        )
        
        # Validate inputs
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 10, 'message': 'Validating input files...'}
        )
        
        # Perform clipping
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 30, 'message': 'Clipping raster...'}
        )
        
        result_path = ClipService.clip_raster_by_vector(
            raster_file=raster_file,
            vector_file=vector_file,
            output_name=output_name
        )
        
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 90, 'message': 'Finalizing...'}
        )
        
        # Return success result
        return {
            'status': JobStatus.SUCCESS,
            'result_file': result_path,
            'message': 'Clip operation completed successfully',
            'progress': 100
        }
        
    except Exception as exc:
        logger.error(f"Clip task {task_id} failed: {exc}")
        logger.error(traceback.format_exc())
        
        return {
            'status': JobStatus.FAILED,
            'error': str(exc),
            'message': f'Clip operation failed: {exc}',
            'progress': 0
        }


@celery_app.task(bind=True, name='reproject_raster_task')
def reproject_raster_task(self, raster_file: str, target_crs: str, output_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Celery task for reprojecting raster
    
    Args:
        raster_file: Path to raster file
        target_crs: Target CRS
        output_name: Optional output filename
        
    Returns:
        Dictionary with task result
    """
    task_id = self.request.id
    logger.info(f"Starting reproject task {task_id}")
    
    try:
        # Update task status
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 0, 'message': 'Starting reprojection...'}
        )
        
        # Validate inputs
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 10, 'message': 'Validating input file and CRS...'}
        )
        
        # Perform reprojection
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 30, 'message': 'Reprojecting raster...'}
        )
        
        result_path = ReprojectService.reproject_raster(
            raster_file=raster_file,
            target_crs=target_crs,
            output_name=output_name
        )
        
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 90, 'message': 'Finalizing...'}
        )
        
        # Return success result
        return {
            'status': JobStatus.SUCCESS,
            'result_file': result_path,
            'message': 'Reprojection completed successfully',
            'progress': 100
        }
        
    except Exception as exc:
        logger.error(f"Reproject task {task_id} failed: {exc}")
        logger.error(traceback.format_exc())
        
        return {
            'status': JobStatus.FAILED,
            'error': str(exc),
            'message': f'Reprojection failed: {exc}',
            'progress': 0
        }


@celery_app.task(bind=True, name='resample_raster_task')
def resample_raster_task(
    self, 
    raster_file: str, 
    target_resolution: float, 
    resampling_method: str = "bilinear",
    output_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Celery task for resampling raster
    
    Args:
        raster_file: Path to raster file
        target_resolution: Target resolution
        resampling_method: Resampling method
        output_name: Optional output filename
        
    Returns:
        Dictionary with task result
    """
    task_id = self.request.id
    logger.info(f"Starting resample task {task_id}")
    
    try:
        # Update task status
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 0, 'message': 'Starting resampling...'}
        )
        
        # Validate inputs
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 10, 'message': 'Validating input parameters...'}
        )
        
        # Perform resampling
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 30, 'message': 'Resampling raster...'}
        )
        
        result_path = ResampleService.resample_raster(
            raster_file=raster_file,
            target_resolution=target_resolution,
            resampling_method=resampling_method,
            output_name=output_name
        )
        
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 90, 'message': 'Finalizing...'}
        )
        
        # Return success result
        return {
            'status': JobStatus.SUCCESS,
            'result_file': result_path,
            'message': 'Resampling completed successfully',
            'progress': 100
        }
        
    except Exception as exc:
        logger.error(f"Resample task {task_id} failed: {exc}")
        logger.error(traceback.format_exc())
        
        return {
            'status': JobStatus.FAILED,
            'error': str(exc),
            'message': f'Resampling failed: {exc}',
            'progress': 0
        }


@celery_app.task(bind=True, name='mosaic_rasters_task')
def mosaic_rasters_task(
    self, 
    raster_files: List[str], 
    method: str = "first",
    output_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Celery task for creating mosaic from multiple rasters
    
    Args:
        raster_files: List of raster file paths
        method: Mosaic method
        output_name: Optional output filename
        
    Returns:
        Dictionary with task result
    """
    task_id = self.request.id
    logger.info(f"Starting mosaic task {task_id}")
    
    try:
        # Update task status
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 0, 'message': 'Starting mosaic creation...'}
        )
        
        # Validate inputs
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 10, 'message': 'Validating input files...'}
        )
        
        # Perform mosaicking
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 30, 'message': 'Creating mosaic...'}
        )
        
        result_path = MosaicService.create_mosaic(
            raster_files=raster_files,
            method=method,
            output_name=output_name
        )
        
        self.update_state(
            state=JobStatus.RUNNING,
            meta={'progress': 90, 'message': 'Finalizing...'}
        )
        
        # Return success result
        return {
            'status': JobStatus.SUCCESS,
            'result_file': result_path,
            'message': 'Mosaic creation completed successfully',
            'progress': 100
        }
        
    except Exception as exc:
        logger.error(f"Mosaic task {task_id} failed: {exc}")
        logger.error(traceback.format_exc())
        
        return {
            'status': JobStatus.FAILED,
            'error': str(exc),
            'message': f'Mosaic creation failed: {exc}',
            'progress': 0
        }


def submit_job(job_type: JobType, **kwargs) -> str:
    """
    Submit a job to Celery queue
    
    Args:
        job_type: Type of job to submit
        **kwargs: Job parameters
        
    Returns:
        Job ID (Celery task ID)
    """
    try:
        if job_type == JobType.CLIP:
            task = clip_raster_task.delay(
                raster_file=kwargs['raster_file'],
                vector_file=kwargs['vector_file'],
                output_name=kwargs.get('output_name')
            )
        elif job_type == JobType.REPROJECT:
            task = reproject_raster_task.delay(
                raster_file=kwargs['raster_file'],
                target_crs=kwargs['target_crs'],
                output_name=kwargs.get('output_name')
            )
        elif job_type == JobType.RESAMPLE:
            task = resample_raster_task.delay(
                raster_file=kwargs['raster_file'],
                target_resolution=kwargs['target_resolution'],
                resampling_method=kwargs.get('resampling_method', 'bilinear'),
                output_name=kwargs.get('output_name')
            )
        elif job_type == JobType.MOSAIC:
            task = mosaic_rasters_task.delay(
                raster_files=kwargs['raster_files'],
                method=kwargs.get('method', 'first'),
                output_name=kwargs.get('output_name')
            )
        else:
            raise ValueError(f"Unsupported job type: {job_type}")
        
        logger.info(f"Job submitted: {task.id} (type: {job_type})")
        return task.id
        
    except Exception as e:
        logger.error(f"Error submitting job: {e}")
        raise


def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get job status from Celery
    
    Args:
        job_id: Celery task ID
        
    Returns:
        Dictionary with job status information
    """
    try:
        result = AsyncResult(job_id, app=celery_app)
        
        if result.state == 'PENDING':
            status = JobStatus.PENDING
            progress = 0
            message = 'Job is waiting to be processed'
            error = None
            result_file = None
        elif result.state == 'STARTED' or result.state == 'RETRY':
            status = JobStatus.RUNNING
            progress = result.info.get('progress', 0) if result.info else 0
            message = result.info.get('message', 'Job is running') if result.info else 'Job is running'
            error = None
            result_file = None
        elif result.state == 'SUCCESS':
            status = JobStatus.SUCCESS
            progress = 100
            message = result.result.get('message', 'Job completed successfully')
            error = None
            result_file = result.result.get('result_file')
        elif result.state == 'FAILURE':
            status = JobStatus.FAILED
            progress = 0
            message = 'Job failed'
            error = str(result.info) if result.info else 'Unknown error'
            result_file = None
        elif result.state == 'REVOKED':
            status = JobStatus.CANCELLED
            progress = 0
            message = 'Job was cancelled'
            error = None
            result_file = None
        else:
            # Handle custom states
            if result.info and isinstance(result.info, dict):
                status = result.info.get('status', JobStatus.RUNNING)
                progress = result.info.get('progress', 0)
                message = result.info.get('message', f'Job state: {result.state}')
                error = result.info.get('error')
                result_file = result.info.get('result_file')
            else:
                status = JobStatus.RUNNING
                progress = 0
                message = f'Job state: {result.state}'
                error = None
                result_file = None
        
        return {
            'job_id': job_id,
            'status': status,
            'progress': progress,
            'message': message,
            'error': error,
            'result_file': result_file,
            'celery_state': result.state
        }
        
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return {
            'job_id': job_id,
            'status': JobStatus.FAILED,
            'progress': 0,
            'message': 'Error retrieving job status',
            'error': str(e),
            'result_file': None,
            'celery_state': 'UNKNOWN'
        }


def cancel_job(job_id: str) -> bool:
    """
    Cancel a job
    
    Args:
        job_id: Celery task ID
        
    Returns:
        True if cancelled successfully
    """
    try:
        celery_app.control.revoke(job_id, terminate=True)
        logger.info(f"Job cancelled: {job_id}")
        return True
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        return False


def get_worker_status() -> Dict[str, Any]:
    """
    Get Celery worker status
    
    Returns:
        Dictionary with worker status information
    """
    try:
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active_tasks = inspect.active()
        
        # Get worker stats
        stats = inspect.stats()
        
        # Get registered tasks
        registered = inspect.registered()
        
        return {
            'active_tasks': active_tasks or {},
            'stats': stats or {},
            'registered_tasks': registered or {},
            'queue_length': len(active_tasks) if active_tasks else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        return {
            'active_tasks': {},
            'stats': {},
            'registered_tasks': {},
            'queue_length': 0,
            'error': str(e)
        }


# For running Celery worker
if __name__ == '__main__':
    celery_app.start()
