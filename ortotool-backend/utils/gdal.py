import os
import logging
from typing import Optional, List
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.merge import merge
import geopandas as gpd
from shapely.geometry import mapping
import numpy as np

from config.settings import settings

logger = logging.getLogger(__name__)


class GDALUtils:
    """Utility class for GDAL/Rasterio operations"""
    
    @staticmethod
    def validate_raster_file(file_path: str) -> bool:
        """Validate if file is a valid raster"""
        try:
            with rasterio.open(file_path) as src:
                return True
        except Exception as e:
            logger.error(f"Invalid raster file {file_path}: {e}")
            return False
    
    @staticmethod
    def validate_vector_file(file_path: str) -> bool:
        """Validate if file is a valid vector"""
        try:
            gdf = gpd.read_file(file_path)
            return len(gdf) > 0
        except Exception as e:
            logger.error(f"Invalid vector file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_raster_info(file_path: str) -> dict:
        """Get raster metadata"""
        try:
            with rasterio.open(file_path) as src:
                return {
                    "crs": str(src.crs),
                    "transform": src.transform,
                    "bounds": src.bounds,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "dtype": str(src.dtype),
                    "nodata": src.nodata
                }
        except Exception as e:
            logger.error(f"Error getting raster info for {file_path}: {e}")
            raise
    
    @staticmethod
    def get_vector_info(file_path: str) -> dict:
        """Get vector metadata"""
        try:
            gdf = gpd.read_file(file_path)
            return {
                "crs": str(gdf.crs),
                "bounds": gdf.total_bounds.tolist(),
                "count": len(gdf),
                "geometry_type": gdf.geometry.type.iloc[0] if len(gdf) > 0 else None
            }
        except Exception as e:
            logger.error(f"Error getting vector info for {file_path}: {e}")
            raise
    
    @staticmethod
    def create_output_path(input_path: str, suffix: str, output_dir: Optional[str] = None) -> str:
        """Create output file path"""
        if output_dir is None:
            output_dir = settings.output_dir
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_name = f"{base_name}_{suffix}.tif"
        return os.path.join(output_dir, output_name)
    
    @staticmethod
    def ensure_same_crs(raster_path: str, vector_path: str) -> str:
        """Ensure vector has same CRS as raster, reproject if necessary"""
        try:
            with rasterio.open(raster_path) as raster:
                raster_crs = raster.crs
            
            gdf = gpd.read_file(vector_path)
            
            if gdf.crs != raster_crs:
                logger.info(f"Reprojecting vector from {gdf.crs} to {raster_crs}")
                gdf = gdf.to_crs(raster_crs)
                
                # Save reprojected vector to temp file
                temp_vector_path = vector_path.replace('.shp', '_reprojected.shp').replace('.geojson', '_reprojected.geojson')
                gdf.to_file(temp_vector_path)
                return temp_vector_path
            
            return vector_path
            
        except Exception as e:
            logger.error(f"Error ensuring same CRS: {e}")
            raise


class RasterProcessor:
    """High-level raster processing operations"""
    
    @staticmethod
    def clip_raster(raster_path: str, vector_path: str, output_path: str) -> str:
        """Clip raster by vector geometry"""
        try:
            logger.info(f"Clipping raster {raster_path} with vector {vector_path}")
            
            # Ensure same CRS
            vector_path = GDALUtils.ensure_same_crs(raster_path, vector_path)
            
            # Read vector geometry
            gdf = gpd.read_file(vector_path)
            geometries = [mapping(geom) for geom in gdf.geometry]
            
            # Clip raster
            with rasterio.open(raster_path) as src:
                out_image, out_transform = mask(src, geometries, crop=True)
                out_meta = src.meta.copy()
                
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)
            
            logger.info(f"Clipped raster saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error clipping raster: {e}")
            raise
    
    @staticmethod
    def reproject_raster(raster_path: str, target_crs: str, output_path: str) -> str:
        """Reproject raster to target CRS"""
        try:
            logger.info(f"Reprojecting raster {raster_path} to {target_crs}")
            
            with rasterio.open(raster_path) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds)
                
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                
                with rasterio.open(output_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=Resampling.nearest)
            
            logger.info(f"Reprojected raster saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error reprojecting raster: {e}")
            raise
    
    @staticmethod
    def resample_raster(raster_path: str, target_resolution: float, output_path: str, 
                       resampling_method: str = "bilinear") -> str:
        """Resample raster to target resolution"""
        try:
            logger.info(f"Resampling raster {raster_path} to resolution {target_resolution}")
            
            # Map resampling methods
            resampling_map = {
                "nearest": Resampling.nearest,
                "bilinear": Resampling.bilinear,
                "cubic": Resampling.cubic,
                "average": Resampling.average
            }
            
            resampling = resampling_map.get(resampling_method, Resampling.bilinear)
            
            with rasterio.open(raster_path) as src:
                # Calculate new dimensions
                scale_factor_x = src.res[0] / target_resolution
                scale_factor_y = src.res[1] / target_resolution
                
                new_width = int(src.width * scale_factor_x)
                new_height = int(src.height * scale_factor_y)
                
                # Calculate new transform
                new_transform = src.transform * src.transform.scale(
                    (src.width / new_width),
                    (src.height / new_height)
                )
                
                kwargs = src.meta.copy()
                kwargs.update({
                    'transform': new_transform,
                    'width': new_width,
                    'height': new_height
                })
                
                with rasterio.open(output_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=new_transform,
                            dst_crs=src.crs,
                            resampling=resampling)
            
            logger.info(f"Resampled raster saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error resampling raster: {e}")
            raise
    
    @staticmethod
    def mosaic_rasters(raster_paths: List[str], output_path: str, method: str = "first") -> str:
        """Create mosaic from multiple rasters"""
        try:
            logger.info(f"Creating mosaic from {len(raster_paths)} rasters")
            
            # Open all raster files
            src_files_to_mosaic = []
            for path in raster_paths:
                src = rasterio.open(path)
                src_files_to_mosaic.append(src)
            
            # Create mosaic
            mosaic, out_trans = merge(src_files_to_mosaic, method=method)
            
            # Copy metadata from first raster
            out_meta = src_files_to_mosaic[0].meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": out_trans,
                "crs": src_files_to_mosaic[0].crs
            })
            
            # Write mosaic
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(mosaic)
            
            # Close all files
            for src in src_files_to_mosaic:
                src.close()
            
            logger.info(f"Mosaic saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating mosaic: {e}")
            raise
