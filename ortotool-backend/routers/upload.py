from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import List, Optional
import logging

from storage.handler import storage_handler
from models.job import UploadResponse, ErrorResponse
from utils.gdal import GDALUtils

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/raster", response_model=UploadResponse)
async def upload_raster(file: UploadFile = File(...)):
    """
    Upload a raster file (GeoTIFF)
    
    Args:
        file: Uploaded raster file
        
    Returns:
        Upload response with file information
    """
    try:
        logger.info(f"Uploading raster file: {file.filename}")
        
        # Validate file extension
        if not file.filename.lower().endswith(('.tif', '.tiff', '.geotiff')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only GeoTIFF files are supported (.tif, .tiff)"
            )
        
        # Save file
        upload_result = await storage_handler.save_upload_file(file)
        
        # Validate raster file
        if not GDALUtils.validate_raster_file(upload_result['file_path']):
            # Clean up invalid file
            storage_handler.delete_file(upload_result['file_path'])
            raise HTTPException(
                status_code=400,
                detail="Invalid raster file. Please ensure it's a valid GeoTIFF."
            )
        
        logger.info(f"Raster file uploaded successfully: {upload_result['filename']}")
        
        return UploadResponse(**upload_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading raster file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/vector", response_model=UploadResponse)
async def upload_vector(file: UploadFile = File(...)):
    """
    Upload a vector file (Shapefile or GeoJSON)
    
    Args:
        file: Uploaded vector file
        
    Returns:
        Upload response with file information
    """
    try:
        logger.info(f"Uploading vector file: {file.filename}")
        
        # Validate file extension
        valid_extensions = ('.shp', '.geojson', '.json')
        if not file.filename.lower().endswith(valid_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Supported formats: {valid_extensions}"
            )
        
        # Save file
        upload_result = await storage_handler.save_upload_file(file)
        
        # Validate vector file
        if not GDALUtils.validate_vector_file(upload_result['file_path']):
            # Clean up invalid file
            storage_handler.delete_file(upload_result['file_path'])
            raise HTTPException(
                status_code=400,
                detail="Invalid vector file. Please ensure it contains valid geometries."
            )
        
        logger.info(f"Vector file uploaded successfully: {upload_result['filename']}")
        
        return UploadResponse(**upload_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading vector file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/multiple", response_model=List[UploadResponse])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files (raster and/or vector)
    
    Args:
        files: List of uploaded files
        
    Returns:
        List of upload responses
    """
    try:
        logger.info(f"Uploading {len(files)} files")
        
        if len(files) > 20:  # Limit number of files
            raise HTTPException(
                status_code=400,
                detail="Too many files. Maximum 20 files allowed per upload."
            )
        
        results = []
        errors = []
        
        for file in files:
            try:
                # Save file
                upload_result = await storage_handler.save_upload_file(file)
                
                # Validate file based on type
                file_path = upload_result['file_path']
                filename = file.filename.lower()
                
                if filename.endswith(('.tif', '.tiff', '.geotiff')):
                    if not GDALUtils.validate_raster_file(file_path):
                        storage_handler.delete_file(file_path)
                        errors.append(f"Invalid raster file: {file.filename}")
                        continue
                elif filename.endswith(('.shp', '.geojson', '.json')):
                    if not GDALUtils.validate_vector_file(file_path):
                        storage_handler.delete_file(file_path)
                        errors.append(f"Invalid vector file: {file.filename}")
                        continue
                else:
                    storage_handler.delete_file(file_path)
                    errors.append(f"Unsupported file format: {file.filename}")
                    continue
                
                results.append(UploadResponse(**upload_result))
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                errors.append(f"Error processing {file.filename}: {str(e)}")
        
        if errors:
            logger.warning(f"Upload completed with errors: {errors}")
        
        if not results:
            raise HTTPException(
                status_code=400,
                detail=f"No files were uploaded successfully. Errors: {errors}"
            )
        
        logger.info(f"Successfully uploaded {len(results)} files")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading multiple files: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")


@router.get("/files")
async def list_uploaded_files():
    """
    List all uploaded files
    
    Returns:
        Dictionary with lists of raster and vector files
    """
    try:
        all_files = storage_handler.list_files()
        
        raster_files = []
        vector_files = []
        other_files = []
        
        for filename in all_files:
            file_path = storage_handler.get_file_path(filename)
            file_info = storage_handler.get_file_info(file_path)
            
            filename_lower = filename.lower()
            if filename_lower.endswith(('.tif', '.tiff', '.geotiff')):
                raster_files.append(file_info)
            elif filename_lower.endswith(('.shp', '.geojson', '.json')):
                vector_files.append(file_info)
            else:
                other_files.append(file_info)
        
        return {
            "raster_files": raster_files,
            "vector_files": vector_files,
            "other_files": other_files,
            "total_files": len(all_files)
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.get("/files/{filename}/info")
async def get_file_info(filename: str):
    """
    Get detailed information about an uploaded file
    
    Args:
        filename: Name of the file
        
    Returns:
        Detailed file information including spatial metadata
    """
    try:
        file_path = storage_handler.get_file_path(filename)
        
        if not storage_handler.file_exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get basic file info
        file_info = storage_handler.get_file_info(file_path)
        
        # Get spatial info based on file type
        filename_lower = filename.lower()
        if filename_lower.endswith(('.tif', '.tiff', '.geotiff')):
            try:
                spatial_info = GDALUtils.get_raster_info(file_path)
                file_info['spatial_info'] = spatial_info
                file_info['file_type'] = 'raster'
            except Exception as e:
                file_info['spatial_error'] = str(e)
        elif filename_lower.endswith(('.shp', '.geojson', '.json')):
            try:
                spatial_info = GDALUtils.get_vector_info(file_path)
                file_info['spatial_info'] = spatial_info
                file_info['file_type'] = 'vector'
            except Exception as e:
                file_info['spatial_error'] = str(e)
        else:
            file_info['file_type'] = 'unknown'
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete an uploaded file
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        Confirmation message
    """
    try:
        file_path = storage_handler.get_file_path(filename)
        
        if not storage_handler.file_exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        success = storage_handler.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete file")
        
        logger.info(f"File deleted: {filename}")
        return {"message": f"File {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_files(max_age_days: int = 7):
    """
    Clean up old uploaded files
    
    Args:
        max_age_days: Maximum age in days for files to keep
        
    Returns:
        Cleanup summary
    """
    try:
        if max_age_days < 1:
            raise HTTPException(status_code=400, detail="max_age_days must be at least 1")
        
        deleted_count = storage_handler.cleanup_old_files(max_age_days=max_age_days)
        
        logger.info(f"Cleanup completed: {deleted_count} files deleted")
        return {
            "message": f"Cleanup completed successfully",
            "deleted_files": deleted_count,
            "max_age_days": max_age_days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")
