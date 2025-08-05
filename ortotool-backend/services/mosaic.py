import logging
import os
from typing import List, Optional

from utils.gdal import RasterProcessor, GDALUtils
from storage.handler import storage_handler

logger = logging.getLogger(__name__)


class MosaicService:
    """Service for creating mosaics from multiple raster files"""
    
    SUPPORTED_METHODS = ["first", "last", "min", "max", "mean"]
    
    @staticmethod
    def create_mosaic(
        raster_files: List[str],
        output_name: Optional[str] = None,
        method: str = "first"
    ) -> str:
        """
        Create a mosaic from multiple raster files
        
        Args:
            raster_files: List of paths to raster files
            output_name: Optional custom output filename
            method: Mosaic method (first, last, min, max, mean)
            
        Returns:
            Path to the mosaic raster file
        """
        try:
            logger.info(f"Starting mosaic operation with {len(raster_files)} files")
            
            # Validate inputs
            if not raster_files or len(raster_files) < 2:
                raise ValueError("At least 2 raster files are required for mosaic")
            
            if method not in MosaicService.SUPPORTED_METHODS:
                raise ValueError(f"Unsupported mosaic method: {method}. "
                               f"Supported methods: {MosaicService.SUPPORTED_METHODS}")
            
            # Validate all input files
            validated_files = []
            for raster_file in raster_files:
                if not storage_handler.file_exists(raster_file):
                    logger.warning(f"Raster file not found, skipping: {raster_file}")
                    continue
                
                if not GDALUtils.validate_raster_file(raster_file):
                    logger.warning(f"Invalid raster file, skipping: {raster_file}")
                    continue
                
                validated_files.append(raster_file)
            
            if len(validated_files) < 2:
                raise ValueError("Insufficient valid raster files for mosaic operation")
            
            logger.info(f"Using {len(validated_files)} valid files for mosaic")
            
            # Check compatibility
            compatibility_info = MosaicService._check_raster_compatibility(validated_files)
            
            if not compatibility_info['compatible']:
                logger.warning("Rasters have different properties:")
                for warning in compatibility_info['warnings']:
                    logger.warning(f"  - {warning}")
                
                # For now, proceed with warning - GDAL will handle reprojection
                logger.info("Proceeding with mosaic despite compatibility warnings")
            
            # Generate output path
            if output_name:
                output_path = os.path.join(storage_handler.output_dir, output_name)
            else:
                output_path = GDALUtils.create_output_path(
                    validated_files[0], 
                    f"mosaic_{method}_{len(validated_files)}files"
                )
            
            # Perform mosaicking
            result_path = RasterProcessor.mosaic_rasters(
                raster_paths=validated_files,
                output_path=output_path,
                method=method
            )
            
            # Validate output
            if not storage_handler.file_exists(result_path):
                raise RuntimeError("Mosaic file was not created successfully")
            
            # Get output info for logging
            output_info = GDALUtils.get_raster_info(result_path)
            logger.info(f"Mosaic completed successfully")
            logger.info(f"Output dimensions: {output_info['width']}x{output_info['height']}")
            logger.info(f"Output CRS: {output_info['crs']}")
            logger.info(f"Output bounds: {output_info['bounds']}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Error in mosaic operation: {e}")
            raise
    
    @staticmethod
    def _check_raster_compatibility(raster_files: List[str]) -> dict:
        """
        Check compatibility between raster files for mosaicking
        
        Args:
            raster_files: List of raster file paths
            
        Returns:
            Dictionary with compatibility information
        """
        try:
            if not raster_files:
                return {"compatible": False, "warnings": ["No files provided"]}
            
            # Get info for all rasters
            raster_infos = []
            for raster_file in raster_files:
                try:
                    info = GDALUtils.get_raster_info(raster_file)
                    raster_infos.append(info)
                except Exception as e:
                    logger.error(f"Error getting info for {raster_file}: {e}")
                    continue
            
            if len(raster_infos) < 2:
                return {"compatible": False, "warnings": ["Insufficient valid raster files"]}
            
            # Check compatibility
            warnings = []
            reference = raster_infos[0]
            
            # Check CRS
            crs_list = [info['crs'] for info in raster_infos]
            if len(set(crs_list)) > 1:
                warnings.append(f"Different CRS found: {set(crs_list)}")
            
            # Check band count
            band_counts = [info['count'] for info in raster_infos]
            if len(set(band_counts)) > 1:
                warnings.append(f"Different band counts: {set(band_counts)}")
            
            # Check data types
            dtypes = [info['dtype'] for info in raster_infos]
            if len(set(dtypes)) > 1:
                warnings.append(f"Different data types: {set(dtypes)}")
            
            # Check resolution (approximate)
            resolutions = []
            for info in raster_infos:
                transform = info['transform']
                res = min(abs(transform[0]), abs(transform[4]))
                resolutions.append(round(res, 6))
            
            if len(set(resolutions)) > 1:
                warnings.append(f"Different resolutions: {set(resolutions)}")
            
            # Check nodata values
            nodata_values = [info['nodata'] for info in raster_infos]
            if len(set(nodata_values)) > 1:
                warnings.append(f"Different nodata values: {set(nodata_values)}")
            
            compatible = len(warnings) == 0
            
            return {
                "compatible": compatible,
                "warnings": warnings,
                "raster_count": len(raster_infos),
                "reference_info": reference
            }
            
        except Exception as e:
            logger.error(f"Error checking raster compatibility: {e}")
            return {"compatible": False, "warnings": [f"Error checking compatibility: {e}"]}
    
    @staticmethod
    def get_mosaic_preview_info(raster_files: List[str]) -> dict:
        """
        Get preview information about the mosaic operation
        
        Args:
            raster_files: List of raster file paths
            
        Returns:
            Dictionary with preview information
        """
        try:
            # Validate files exist
            existing_files = []
            missing_files = []
            
            for raster_file in raster_files:
                if storage_handler.file_exists(raster_file):
                    existing_files.append(raster_file)
                else:
                    missing_files.append(raster_file)
            
            if not existing_files:
                raise ValueError("No existing raster files found")
            
            # Get compatibility info
            compatibility_info = MosaicService._check_raster_compatibility(existing_files)
            
            # Calculate combined bounds
            all_bounds = []
            total_area = 0
            
            for raster_file in existing_files:
                try:
                    info = GDALUtils.get_raster_info(raster_file)
                    bounds = info['bounds']
                    all_bounds.append(bounds)
                    
                    # Calculate area (simplified)
                    area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
                    total_area += area
                    
                except Exception as e:
                    logger.warning(f"Error processing {raster_file}: {e}")
            
            # Calculate combined bounds
            if all_bounds:
                combined_bounds = [
                    min(b[0] for b in all_bounds),  # min_x
                    min(b[1] for b in all_bounds),  # min_y
                    max(b[2] for b in all_bounds),  # max_x
                    max(b[3] for b in all_bounds)   # max_y
                ]
            else:
                combined_bounds = None
            
            # Estimate output size
            if existing_files and combined_bounds:
                try:
                    reference_info = GDALUtils.get_raster_info(existing_files[0])
                    transform = reference_info['transform']
                    pixel_size_x = abs(transform[0])
                    pixel_size_y = abs(transform[4])
                    
                    estimated_width = int((combined_bounds[2] - combined_bounds[0]) / pixel_size_x)
                    estimated_height = int((combined_bounds[3] - combined_bounds[1]) / pixel_size_y)
                    
                except Exception:
                    estimated_width = estimated_height = None
            else:
                estimated_width = estimated_height = None
            
            return {
                "file_info": {
                    "total_files": len(raster_files),
                    "existing_files": len(existing_files),
                    "missing_files": missing_files,
                    "valid_files": existing_files
                },
                "compatibility": compatibility_info,
                "spatial_info": {
                    "combined_bounds": combined_bounds,
                    "total_area": total_area,
                    "estimated_width": estimated_width,
                    "estimated_height": estimated_height
                },
                "supported_methods": MosaicService.SUPPORTED_METHODS,
                "recommendations": MosaicService._get_mosaic_recommendations(compatibility_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting mosaic preview: {e}")
            raise
    
    @staticmethod
    def _get_mosaic_recommendations(compatibility_info: dict) -> List[str]:
        """Generate recommendations based on compatibility analysis"""
        recommendations = []
        
        if not compatibility_info.get('compatible', True):
            recommendations.append("Consider preprocessing files to ensure compatibility")
            
            for warning in compatibility_info.get('warnings', []):
                if 'CRS' in warning:
                    recommendations.append("Reproject all rasters to the same CRS before mosaicking")
                elif 'resolution' in warning:
                    recommendations.append("Resample all rasters to the same resolution")
                elif 'band' in warning:
                    recommendations.append("Ensure all rasters have the same number of bands")
                elif 'data type' in warning:
                    recommendations.append("Convert all rasters to the same data type")
        
        if compatibility_info.get('raster_count', 0) > 10:
            recommendations.append("Large number of files - consider processing in batches")
        
        return recommendations
