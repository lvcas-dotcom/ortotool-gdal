import logging
import os
from typing import Optional

from utils.gdal import RasterProcessor, GDALUtils
from storage.handler import storage_handler

logger = logging.getLogger(__name__)


class ClipService:
    """Service for clipping raster data with vector geometries"""
    
    @staticmethod
    def clip_raster_by_vector(
        raster_file: str,
        vector_file: str,
        output_name: Optional[str] = None
    ) -> str:
        """
        Clip a raster file using a vector geometry
        
        Args:
            raster_file: Path to the raster file
            vector_file: Path to the vector file (shapefile or GeoJSON)
            output_name: Optional custom output filename
            
        Returns:
            Path to the clipped raster file
        """
        try:
            logger.info(f"Starting clip operation: {raster_file} with {vector_file}")
            
            # Validate input files
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            if not storage_handler.file_exists(vector_file):
                raise FileNotFoundError(f"Vector file not found: {vector_file}")
            
            # Validate file formats
            if not GDALUtils.validate_raster_file(raster_file):
                raise ValueError(f"Invalid raster file: {raster_file}")
            
            if not GDALUtils.validate_vector_file(vector_file):
                raise ValueError(f"Invalid vector file: {vector_file}")
            
            # Generate output path
            if output_name:
                output_path = os.path.join(storage_handler.output_dir, output_name)
            else:
                output_path = GDALUtils.create_output_path(raster_file, "clipped")
            
            # Get file information for logging
            raster_info = GDALUtils.get_raster_info(raster_file)
            vector_info = GDALUtils.get_vector_info(vector_file)
            
            logger.info(f"Raster CRS: {raster_info['crs']}, Vector CRS: {vector_info['crs']}")
            
            # Perform clipping
            result_path = RasterProcessor.clip_raster(
                raster_path=raster_file,
                vector_path=vector_file,
                output_path=output_path
            )
            
            # Validate output
            if not storage_handler.file_exists(result_path):
                raise RuntimeError("Clipped file was not created successfully")
            
            logger.info(f"Clip operation completed successfully: {result_path}")
            return result_path
            
        except Exception as e:
            logger.error(f"Error in clip operation: {e}")
            raise
    
    @staticmethod
    def get_clip_preview_info(raster_file: str, vector_file: str) -> dict:
        """
        Get preview information about the clip operation without actually performing it
        
        Args:
            raster_file: Path to the raster file
            vector_file: Path to the vector file
            
        Returns:
            Dictionary with preview information
        """
        try:
            # Validate files
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            if not storage_handler.file_exists(vector_file):
                raise FileNotFoundError(f"Vector file not found: {vector_file}")
            
            raster_info = GDALUtils.get_raster_info(raster_file)
            vector_info = GDALUtils.get_vector_info(vector_file)
            
            # Check if CRS match
            crs_match = raster_info['crs'] == vector_info['crs']
            
            # Calculate approximate output size (simplified)
            vector_bounds = vector_info['bounds']
            raster_bounds = raster_info['bounds']
            
            # Check if geometries intersect (simplified check)
            intersects = (
                vector_bounds[0] < raster_bounds[2] and  # min_x < max_x
                vector_bounds[2] > raster_bounds[0] and  # max_x > min_x
                vector_bounds[1] < raster_bounds[3] and  # min_y < max_y
                vector_bounds[3] > raster_bounds[1]      # max_y > min_y
            )
            
            return {
                "raster_info": raster_info,
                "vector_info": vector_info,
                "crs_match": crs_match,
                "geometries_intersect": intersects,
                "estimated_output_bounds": vector_bounds if intersects else None,
                "warnings": [] if crs_match and intersects else [
                    "CRS mismatch - vector will be reprojected" if not crs_match else "",
                    "Geometries don't appear to intersect" if not intersects else ""
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting clip preview: {e}")
            raise
