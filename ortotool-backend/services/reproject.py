import logging
import os
from typing import Optional

from utils.gdal import RasterProcessor, GDALUtils
from storage.handler import storage_handler

logger = logging.getLogger(__name__)


class ReprojectService:
    """Service for reprojecting raster data to different coordinate reference systems"""
    
    @staticmethod
    def reproject_raster(
        raster_file: str,
        target_crs: str,
        output_name: Optional[str] = None
    ) -> str:
        """
        Reproject a raster file to a target CRS
        
        Args:
            raster_file: Path to the raster file
            target_crs: Target CRS (e.g., 'EPSG:4326', 'EPSG:31982')
            output_name: Optional custom output filename
            
        Returns:
            Path to the reprojected raster file
        """
        try:
            logger.info(f"Starting reproject operation: {raster_file} to {target_crs}")
            
            # Validate input file
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            if not GDALUtils.validate_raster_file(raster_file):
                raise ValueError(f"Invalid raster file: {raster_file}")
            
            # Validate target CRS format
            if not ReprojectService._validate_crs(target_crs):
                raise ValueError(f"Invalid CRS format: {target_crs}")
            
            # Get current raster info
            raster_info = GDALUtils.get_raster_info(raster_file)
            current_crs = raster_info['crs']
            
            # Check if reprojection is necessary
            if current_crs == target_crs:
                logger.warning(f"Raster already in target CRS {target_crs}")
                return raster_file
            
            # Generate output path
            if output_name:
                output_path = os.path.join(storage_handler.output_dir, output_name)
            else:
                crs_suffix = target_crs.replace(':', '_').replace('+', '')
                output_path = GDALUtils.create_output_path(raster_file, f"reprojected_{crs_suffix}")
            
            logger.info(f"Reprojecting from {current_crs} to {target_crs}")
            
            # Perform reprojection
            result_path = RasterProcessor.reproject_raster(
                raster_path=raster_file,
                target_crs=target_crs,
                output_path=output_path
            )
            
            # Validate output
            if not storage_handler.file_exists(result_path):
                raise RuntimeError("Reprojected file was not created successfully")
            
            # Get output info for logging
            output_info = GDALUtils.get_raster_info(result_path)
            logger.info(f"Reprojection completed. Output CRS: {output_info['crs']}")
            logger.info(f"Output dimensions: {output_info['width']}x{output_info['height']}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Error in reproject operation: {e}")
            raise
    
    @staticmethod
    def _validate_crs(crs: str) -> bool:
        """
        Validate CRS format
        
        Args:
            crs: CRS string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation for common CRS formats
            crs = crs.strip().upper()
            
            # EPSG format
            if crs.startswith('EPSG:'):
                epsg_code = crs.split(':')[1]
                return epsg_code.isdigit() and len(epsg_code) <= 6
            
            # PROJ4 format (basic check)
            if crs.startswith('+PROJ='):
                return True
            
            # WKT format (basic check)
            if any(keyword in crs for keyword in ['GEOGCS', 'PROJCS', 'GEOGCRS', 'PROJCRS']):
                return True
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def get_reproject_preview_info(raster_file: str, target_crs: str) -> dict:
        """
        Get preview information about the reprojection operation
        
        Args:
            raster_file: Path to the raster file
            target_crs: Target CRS
            
        Returns:
            Dictionary with preview information
        """
        try:
            # Validate file
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            raster_info = GDALUtils.get_raster_info(raster_file)
            current_crs = raster_info['crs']
            
            # Check if reprojection is needed
            needs_reprojection = current_crs != target_crs
            
            # Estimate changes (simplified)
            warnings = []
            if not ReprojectService._validate_crs(target_crs):
                warnings.append(f"Invalid target CRS format: {target_crs}")
            
            if not needs_reprojection:
                warnings.append("Raster is already in the target CRS")
            
            # Get CRS information
            crs_info = {
                "current_crs": current_crs,
                "target_crs": target_crs,
                "needs_reprojection": needs_reprojection
            }
            
            return {
                "raster_info": raster_info,
                "crs_info": crs_info,
                "warnings": warnings,
                "estimated_changes": {
                    "coordinate_system": target_crs,
                    "bounds_will_change": needs_reprojection,
                    "resolution_may_change": needs_reprojection
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting reproject preview: {e}")
            raise
    
    @staticmethod
    def get_common_crs_list() -> list:
        """
        Get a list of commonly used CRS
        
        Returns:
            List of dictionaries with CRS information
        """
        return [
            {"code": "EPSG:4326", "name": "WGS 84 (Geographic)", "type": "Geographic"},
            {"code": "EPSG:3857", "name": "Web Mercator", "type": "Projected"},
            {"code": "EPSG:31982", "name": "SIRGAS 2000 / UTM zone 22S", "type": "Projected"},
            {"code": "EPSG:31983", "name": "SIRGAS 2000 / UTM zone 23S", "type": "Projected"},
            {"code": "EPSG:31984", "name": "SIRGAS 2000 / UTM zone 24S", "type": "Projected"},
            {"code": "EPSG:31985", "name": "SIRGAS 2000 / UTM zone 25S", "type": "Projected"},
            {"code": "EPSG:4674", "name": "SIRGAS 2000 (Geographic)", "type": "Geographic"},
            {"code": "EPSG:29193", "name": "SAD69 / UTM zone 23S", "type": "Projected"},
            {"code": "EPSG:32723", "name": "WGS 84 / UTM zone 23S", "type": "Projected"},
            {"code": "EPSG:32724", "name": "WGS 84 / UTM zone 24S", "type": "Projected"}
        ]
