import logging
import os
from typing import Optional

from utils.gdal import RasterProcessor, GDALUtils
from storage.handler import storage_handler

logger = logging.getLogger(__name__)


class ResampleService:
    """Service for resampling raster data to different resolutions"""
    
    SUPPORTED_METHODS = ["nearest", "bilinear", "cubic", "average"]
    
    @staticmethod
    def resample_raster(
        raster_file: str,
        target_resolution: float,
        resampling_method: str = "bilinear",
        output_name: Optional[str] = None
    ) -> str:
        """
        Resample a raster file to a target resolution
        
        Args:
            raster_file: Path to the raster file
            target_resolution: Target resolution in map units
            resampling_method: Resampling method (nearest, bilinear, cubic, average)
            output_name: Optional custom output filename
            
        Returns:
            Path to the resampled raster file
        """
        try:
            logger.info(f"Starting resample operation: {raster_file} to resolution {target_resolution}")
            
            # Validate input file
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            if not GDALUtils.validate_raster_file(raster_file):
                raise ValueError(f"Invalid raster file: {raster_file}")
            
            # Validate resampling method
            if resampling_method not in ResampleService.SUPPORTED_METHODS:
                raise ValueError(f"Unsupported resampling method: {resampling_method}. "
                               f"Supported methods: {ResampleService.SUPPORTED_METHODS}")
            
            # Validate target resolution
            if target_resolution <= 0:
                raise ValueError("Target resolution must be positive")
            
            # Get current raster info
            raster_info = GDALUtils.get_raster_info(raster_file)
            current_resolution = min(abs(raster_info['transform'][0]), abs(raster_info['transform'][4]))
            
            logger.info(f"Current resolution: {current_resolution}, Target resolution: {target_resolution}")
            
            # Check if resampling is necessary
            tolerance = current_resolution * 0.01  # 1% tolerance
            if abs(current_resolution - target_resolution) < tolerance:
                logger.warning(f"Raster resolution is already close to target resolution")
                return raster_file
            
            # Generate output path
            if output_name:
                output_path = os.path.join(storage_handler.output_dir, output_name)
            else:
                resolution_str = f"{target_resolution:.2f}".replace('.', '_')
                output_path = GDALUtils.create_output_path(
                    raster_file, 
                    f"resampled_{resolution_str}_{resampling_method}"
                )
            
            # Perform resampling
            result_path = RasterProcessor.resample_raster(
                raster_path=raster_file,
                target_resolution=target_resolution,
                output_path=output_path,
                resampling_method=resampling_method
            )
            
            # Validate output
            if not storage_handler.file_exists(result_path):
                raise RuntimeError("Resampled file was not created successfully")
            
            # Get output info for logging
            output_info = GDALUtils.get_raster_info(result_path)
            output_resolution = min(abs(output_info['transform'][0]), abs(output_info['transform'][4]))
            
            logger.info(f"Resampling completed successfully")
            logger.info(f"Output resolution: {output_resolution}")
            logger.info(f"Output dimensions: {output_info['width']}x{output_info['height']}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Error in resample operation: {e}")
            raise
    
    @staticmethod
    def get_resample_preview_info(raster_file: str, target_resolution: float) -> dict:
        """
        Get preview information about the resampling operation
        
        Args:
            raster_file: Path to the raster file
            target_resolution: Target resolution
            
        Returns:
            Dictionary with preview information
        """
        try:
            # Validate file
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            raster_info = GDALUtils.get_raster_info(raster_file)
            
            # Calculate current resolution
            transform = raster_info['transform']
            current_resolution_x = abs(transform[0])
            current_resolution_y = abs(transform[4])
            current_resolution = min(current_resolution_x, current_resolution_y)
            
            # Calculate scale factors
            scale_factor_x = current_resolution_x / target_resolution
            scale_factor_y = current_resolution_y / target_resolution
            
            # Estimate new dimensions
            new_width = int(raster_info['width'] * scale_factor_x)
            new_height = int(raster_info['height'] * scale_factor_y)
            
            # Calculate file size estimates
            current_pixels = raster_info['width'] * raster_info['height']
            new_pixels = new_width * new_height
            size_ratio = new_pixels / current_pixels if current_pixels > 0 else 1
            
            # Determine operation type
            if target_resolution < current_resolution:
                operation_type = "upsampling"  # Increasing resolution
            elif target_resolution > current_resolution:
                operation_type = "downsampling"  # Decreasing resolution
            else:
                operation_type = "no_change"
            
            # Generate warnings
            warnings = []
            if target_resolution <= 0:
                warnings.append("Target resolution must be positive")
            
            if size_ratio > 10:
                warnings.append("Output file will be significantly larger (>10x)")
            elif size_ratio > 4:
                warnings.append("Output file will be much larger (>4x)")
            
            if operation_type == "upsampling" and scale_factor_x > 5:
                warnings.append("High upsampling ratio may result in pixelated output")
            
            return {
                "raster_info": raster_info,
                "resolution_info": {
                    "current_resolution_x": current_resolution_x,
                    "current_resolution_y": current_resolution_y,
                    "current_resolution": current_resolution,
                    "target_resolution": target_resolution,
                    "scale_factor_x": scale_factor_x,
                    "scale_factor_y": scale_factor_y,
                    "operation_type": operation_type
                },
                "dimension_changes": {
                    "current_width": raster_info['width'],
                    "current_height": raster_info['height'],
                    "new_width": new_width,
                    "new_height": new_height,
                    "pixel_count_ratio": size_ratio
                },
                "warnings": warnings,
                "supported_methods": ResampleService.SUPPORTED_METHODS
            }
            
        except Exception as e:
            logger.error(f"Error getting resample preview: {e}")
            raise
    
    @staticmethod
    def calculate_optimal_resolution(raster_file: str, target_file_size_mb: float) -> float:
        """
        Calculate optimal resolution to achieve approximate target file size
        
        Args:
            raster_file: Path to the raster file
            target_file_size_mb: Target file size in megabytes
            
        Returns:
            Suggested resolution
        """
        try:
            if not storage_handler.file_exists(raster_file):
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
            
            # Get current file info
            file_info = storage_handler.get_file_info(raster_file)
            current_size_mb = file_info['file_size'] / (1024 * 1024)
            
            raster_info = GDALUtils.get_raster_info(raster_file)
            current_resolution = min(
                abs(raster_info['transform'][0]), 
                abs(raster_info['transform'][4])
            )
            
            # Estimate resolution needed
            # Assuming linear relationship between pixels and file size (simplified)
            size_ratio = target_file_size_mb / current_size_mb
            resolution_ratio = 1 / (size_ratio ** 0.5)  # Square root because of 2D
            
            suggested_resolution = current_resolution * resolution_ratio
            
            logger.info(f"Current size: {current_size_mb:.2f}MB, Target: {target_file_size_mb}MB")
            logger.info(f"Suggested resolution: {suggested_resolution:.6f}")
            
            return suggested_resolution
            
        except Exception as e:
            logger.error(f"Error calculating optimal resolution: {e}")
            raise
