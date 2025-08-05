from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

from models.job import ClipRequest, JobResponse, ErrorResponse
from services.clip import ClipService
from workers.tasks import submit_job, get_job_status
from models.job import JobType
from storage.handler import storage_handler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/raster", tags=["raster"])


@router.post("/clip", response_model=JobResponse)
async def clip_raster(request: ClipRequest):
    """
    Clip raster by vector geometry (asynchronous)
    
    Args:
        request: Clip request with raster and vector file paths
        
    Returns:
        Job information with job ID for tracking
    """
    try:
        logger.info(f"Received clip request: {request.raster_file} with {request.vector_file}")
        
        # Validate input files exist
        if not storage_handler.file_exists(request.raster_file):
            raise HTTPException(status_code=404, detail=f"Raster file not found: {request.raster_file}")
        
        if not storage_handler.file_exists(request.vector_file):
            raise HTTPException(status_code=404, detail=f"Vector file not found: {request.vector_file}")
        
        # Submit job to Celery
        job_id = submit_job(
            job_type=JobType.CLIP,
            raster_file=request.raster_file,
            vector_file=request.vector_file,
            output_name=request.output_name
        )
        
        # Get initial job status
        job_status = get_job_status(job_id)
        
        return JobResponse(
            job_id=job_id,
            status=job_status['status'],
            job_type=JobType.CLIP,
            created_at=job_status.get('created_at'),
            progress=job_status.get('progress', 0),
            message=job_status.get('message', 'Clip job submitted successfully')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting clip job: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting clip job: {str(e)}")


@router.post("/clip/preview")
async def preview_clip(request: ClipRequest):
    """
    Get preview information for clip operation without executing it
    
    Args:
        request: Clip request with raster and vector file paths
        
    Returns:
        Preview information about the clip operation
    """
    try:
        # Validate input files exist
        if not storage_handler.file_exists(request.raster_file):
            raise HTTPException(status_code=404, detail=f"Raster file not found: {request.raster_file}")
        
        if not storage_handler.file_exists(request.vector_file):
            raise HTTPException(status_code=404, detail=f"Vector file not found: {request.vector_file}")
        
        # Get preview info
        preview_info = ClipService.get_clip_preview_info(
            raster_file=request.raster_file,
            vector_file=request.vector_file
        )
        
        return preview_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clip preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting clip preview: {str(e)}")


@router.post("/reproject", response_model=JobResponse)
async def reproject_raster(
    raster_file: str,
    target_crs: str,
    output_name: Optional[str] = None
):
    """
    Reproject raster to target CRS (asynchronous)
    
    Args:
        raster_file: Path to raster file
        target_crs: Target CRS (e.g., 'EPSG:4326')
        output_name: Optional output filename
        
    Returns:
        Job information with job ID for tracking
    """
    try:
        logger.info(f"Received reproject request: {raster_file} to {target_crs}")
        
        # Validate input file exists
        if not storage_handler.file_exists(raster_file):
            raise HTTPException(status_code=404, detail=f"Raster file not found: {raster_file}")
        
        # Submit job to Celery
        job_id = submit_job(
            job_type=JobType.REPROJECT,
            raster_file=raster_file,
            target_crs=target_crs,
            output_name=output_name
        )
        
        # Get initial job status
        job_status = get_job_status(job_id)
        
        return JobResponse(
            job_id=job_id,
            status=job_status['status'],
            job_type=JobType.REPROJECT,
            created_at=job_status.get('created_at'),
            progress=job_status.get('progress', 0),
            message=job_status.get('message', 'Reproject job submitted successfully')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting reproject job: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting reproject job: {str(e)}")


@router.post("/reproject/preview")
async def preview_reproject(
    raster_file: str,
    target_crs: str
):
    """
    Get preview information for reproject operation without executing it
    
    Args:
        raster_file: Path to raster file
        target_crs: Target CRS
        
    Returns:
        Preview information about the reproject operation
    """
    try:
        # Validate input file exists
        if not storage_handler.file_exists(raster_file):
            raise HTTPException(status_code=404, detail=f"Raster file not found: {raster_file}")
        
        # Get preview info
        from services.reproject import ReprojectService
        preview_info = ReprojectService.get_reproject_preview_info(
            raster_file=raster_file,
            target_crs=target_crs
        )
        
        return preview_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reproject preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting reproject preview: {str(e)}")


@router.post("/resample", response_model=JobResponse)
async def resample_raster(
    raster_file: str,
    target_resolution: float,
    resampling_method: str = "bilinear",
    output_name: Optional[str] = None
):
    """
    Resample raster to target resolution (asynchronous)
    
    Args:
        raster_file: Path to raster file
        target_resolution: Target resolution in map units
        resampling_method: Resampling method (nearest, bilinear, cubic, average)
        output_name: Optional output filename
        
    Returns:
        Job information with job ID for tracking
    """
    try:
        logger.info(f"Received resample request: {raster_file} to resolution {target_resolution}")
        
        # Validate input file exists
        if not storage_handler.file_exists(raster_file):
            raise HTTPException(status_code=404, detail=f"Raster file not found: {raster_file}")
        
        # Submit job to Celery
        job_id = submit_job(
            job_type=JobType.RESAMPLE,
            raster_file=raster_file,
            target_resolution=target_resolution,
            resampling_method=resampling_method,
            output_name=output_name
        )
        
        # Get initial job status
        job_status = get_job_status(job_id)
        
        return JobResponse(
            job_id=job_id,
            status=job_status['status'],
            job_type=JobType.RESAMPLE,
            created_at=job_status.get('created_at'),
            progress=job_status.get('progress', 0),
            message=job_status.get('message', 'Resample job submitted successfully')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting resample job: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting resample job: {str(e)}")


@router.post("/resample/preview")
async def preview_resample(
    raster_file: str,
    target_resolution: float
):
    """
    Get preview information for resample operation without executing it
    
    Args:
        raster_file: Path to raster file
        target_resolution: Target resolution
        
    Returns:
        Preview information about the resample operation
    """
    try:
        # Validate input file exists
        if not storage_handler.file_exists(raster_file):
            raise HTTPException(status_code=404, detail=f"Raster file not found: {raster_file}")
        
        # Get preview info
        from services.resample import ResampleService
        preview_info = ResampleService.get_resample_preview_info(
            raster_file=raster_file,
            target_resolution=target_resolution
        )
        
        return preview_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resample preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting resample preview: {str(e)}")


@router.post("/mosaic", response_model=JobResponse)
async def create_mosaic(
    raster_files: list[str],
    method: str = "first",
    output_name: Optional[str] = None
):
    """
    Create mosaic from multiple raster files (asynchronous)
    
    Args:
        raster_files: List of raster file paths
        method: Mosaic method (first, last, min, max, mean)
        output_name: Optional output filename
        
    Returns:
        Job information with job ID for tracking
    """
    try:
        logger.info(f"Received mosaic request: {len(raster_files)} files with method {method}")
        
        # Validate input files exist
        missing_files = []
        for raster_file in raster_files:
            if not storage_handler.file_exists(raster_file):
                missing_files.append(raster_file)
        
        if missing_files:
            raise HTTPException(
                status_code=404, 
                detail=f"Raster files not found: {missing_files}"
            )
        
        # Submit job to Celery
        job_id = submit_job(
            job_type=JobType.MOSAIC,
            raster_files=raster_files,
            method=method,
            output_name=output_name
        )
        
        # Get initial job status
        job_status = get_job_status(job_id)
        
        return JobResponse(
            job_id=job_id,
            status=job_status['status'],
            job_type=JobType.MOSAIC,
            created_at=job_status.get('created_at'),
            progress=job_status.get('progress', 0),
            message=job_status.get('message', 'Mosaic job submitted successfully')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting mosaic job: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting mosaic job: {str(e)}")


@router.post("/mosaic/preview")
async def preview_mosaic(raster_files: list[str]):
    """
    Get preview information for mosaic operation without executing it
    
    Args:
        raster_files: List of raster file paths
        
    Returns:
        Preview information about the mosaic operation
    """
    try:
        # Get preview info
        from services.mosaic import MosaicService
        preview_info = MosaicService.get_mosaic_preview_info(raster_files=raster_files)
        
        return preview_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mosaic preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting mosaic preview: {str(e)}")


@router.get("/crs/common")
async def get_common_crs():
    """
    Get list of commonly used coordinate reference systems
    
    Returns:
        List of common CRS with codes and descriptions
    """
    try:
        from services.reproject import ReprojectService
        return ReprojectService.get_common_crs_list()
        
    except Exception as e:
        logger.error(f"Error getting common CRS list: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting CRS list: {str(e)}")


@router.get("/methods/resample")
async def get_resample_methods():
    """
    Get list of supported resampling methods
    
    Returns:
        List of supported resampling methods
    """
    try:
        from services.resample import ResampleService
        return {
            "methods": ResampleService.SUPPORTED_METHODS,
            "descriptions": {
                "nearest": "Nearest neighbor - Fast, preserves exact values",
                "bilinear": "Bilinear interpolation - Good for continuous data",
                "cubic": "Cubic interpolation - Best quality for continuous data",
                "average": "Average of all valid pixels - Good for downsampling"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting resample methods: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting resample methods: {str(e)}")


@router.get("/methods/mosaic")
async def get_mosaic_methods():
    """
    Get list of supported mosaic methods
    
    Returns:
        List of supported mosaic methods
    """
    try:
        from services.mosaic import MosaicService
        return {
            "methods": MosaicService.SUPPORTED_METHODS,
            "descriptions": {
                "first": "Use values from the first raster",
                "last": "Use values from the last raster",
                "min": "Use minimum values from all rasters",
                "max": "Use maximum values from all rasters",
                "mean": "Use mean values from all rasters"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting mosaic methods: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting mosaic methods: {str(e)}")
