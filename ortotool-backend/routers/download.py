from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import os
import logging

from storage.handler import storage_handler
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/download", tags=["download"])


@router.get("/file/{filename}")
async def download_file(filename: str):
    """
    Download a processed file
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File download response
    """
    try:
        # Check both upload and output directories
        upload_path = storage_handler.get_file_path(filename, settings.upload_dir)
        output_path = storage_handler.get_file_path(filename, settings.output_dir)
        
        file_path = None
        if storage_handler.file_exists(upload_path):
            file_path = upload_path
        elif storage_handler.file_exists(output_path):
            file_path = output_path
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Get file info
        file_info = storage_handler.get_file_info(file_path)
        
        logger.info(f"Downloading file: {filename} (size: {file_info['file_size']} bytes)")
        
        # Return file response
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.get("/result/{job_id}")
async def download_job_result(job_id: str):
    """
    Download the result file of a completed job
    
    Args:
        job_id: Job ID (Celery task ID)
        
    Returns:
        File download response
    """
    try:
        # Get job status to find result file
        from workers.tasks import get_job_status
        job_info = get_job_status(job_id)
        
        if job_info['status'] != 'SUCCESS':
            raise HTTPException(
                status_code=400, 
                detail=f"Job not completed successfully. Status: {job_info['status']}"
            )
        
        result_file = job_info.get('result_file')
        if not result_file:
            raise HTTPException(status_code=404, detail="No result file found for this job")
        
        if not storage_handler.file_exists(result_file):
            raise HTTPException(status_code=404, detail="Result file not found on disk")
        
        # Get filename from path
        filename = os.path.basename(result_file)
        
        logger.info(f"Downloading job result: {job_id} -> {filename}")
        
        # Return file response
        return FileResponse(
            path=result_file,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading job result {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading job result: {str(e)}")


@router.get("/files/list")
async def list_downloadable_files():
    """
    List all files available for download
    
    Returns:
        List of available files with metadata
    """
    try:
        # Get files from both directories
        upload_files = storage_handler.list_files(settings.upload_dir)
        output_files = storage_handler.list_files(settings.output_dir)
        
        files_info = []
        
        # Process upload files
        for filename in upload_files:
            file_path = storage_handler.get_file_path(filename, settings.upload_dir)
            file_info = storage_handler.get_file_info(file_path)
            file_info['directory'] = 'uploads'
            file_info['download_url'] = f"/download/file/{filename}"
            files_info.append(file_info)
        
        # Process output files
        for filename in output_files:
            file_path = storage_handler.get_file_path(filename, settings.output_dir)
            file_info = storage_handler.get_file_info(file_path)
            file_info['directory'] = 'outputs'
            file_info['download_url'] = f"/download/file/{filename}"
            files_info.append(file_info)
        
        # Sort by modification time (newest first)
        files_info.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return {
            "files": files_info,
            "total_files": len(files_info),
            "upload_files": len(upload_files),
            "output_files": len(output_files)
        }
        
    except Exception as e:
        logger.error(f"Error listing downloadable files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.head("/file/{filename}")
async def check_file_exists(filename: str):
    """
    Check if a file exists without downloading it
    
    Args:
        filename: Name of the file to check
        
    Returns:
        HTTP headers with file information
    """
    try:
        # Check both directories
        upload_path = storage_handler.get_file_path(filename, settings.upload_dir)
        output_path = storage_handler.get_file_path(filename, settings.output_dir)
        
        file_path = None
        if storage_handler.file_exists(upload_path):
            file_path = upload_path
        elif storage_handler.file_exists(output_path):
            file_path = output_path
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Get file info
        file_info = storage_handler.get_file_info(file_path)
        
        # Return headers with file information
        return Response(
            status_code=200,
            headers={
                "Content-Length": str(file_info['file_size']),
                "Last-Modified": file_info['modified_time'].strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "Content-Type": "application/octet-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking file: {str(e)}")


@router.get("/outputs/list")
async def list_output_files():
    """
    List only output/result files
    
    Returns:
        List of output files with metadata
    """
    try:
        output_files = storage_handler.list_files(settings.output_dir)
        
        files_info = []
        for filename in output_files:
            file_path = storage_handler.get_file_path(filename, settings.output_dir)
            file_info = storage_handler.get_file_info(file_path)
            file_info['download_url'] = f"/download/file/{filename}"
            files_info.append(file_info)
        
        # Sort by modification time (newest first)
        files_info.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return {
            "output_files": files_info,
            "total_files": len(files_info)
        }
        
    except Exception as e:
        logger.error(f"Error listing output files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing output files: {str(e)}")


@router.get("/uploads/list")
async def list_upload_files():
    """
    List only uploaded files
    
    Returns:
        List of uploaded files with metadata
    """
    try:
        upload_files = storage_handler.list_files(settings.upload_dir)
        
        files_info = []
        for filename in upload_files:
            file_path = storage_handler.get_file_path(filename, settings.upload_dir)
            file_info = storage_handler.get_file_info(file_path)
            file_info['download_url'] = f"/download/file/{filename}"
            files_info.append(file_info)
        
        # Sort by modification time (newest first)
        files_info.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return {
            "upload_files": files_info,
            "total_files": len(files_info)
        }
        
    except Exception as e:
        logger.error(f"Error listing upload files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing upload files: {str(e)}")
