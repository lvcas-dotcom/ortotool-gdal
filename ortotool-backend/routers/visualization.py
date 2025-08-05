from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import logging
import os
import json

from utils.gdal import GDALUtils
from storage.handler import storage_handler
from models.job import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visualization", tags=["visualization"])


@router.get("/metadata/{file_path:path}")
async def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata for a geospatial file (raster or vector)
    
    Args:
        file_path: Path to the file relative to uploads directory
        
    Returns:
        Metadata including bounds, CRS, dimensions, etc.
    """
    try:
        # Sanitize and validate file path
        full_path = storage_handler.get_file_path(file_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine file type and get appropriate metadata
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.tif', '.tiff']:
            metadata = await _get_raster_metadata(full_path)
        elif file_extension in ['.shp', '.geojson', '.json']:
            metadata = await _get_vector_metadata(full_path)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}"
            )
        
        metadata['file_path'] = file_path
        metadata['file_size'] = os.path.getsize(full_path)
        
        logger.info(f"Retrieved metadata for file: {file_path}")
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/preview/{file_path:path}")
async def get_file_preview(file_path: str, format: str = Query("geojson")) -> Dict[str, Any]:
    """
    Get a preview/sample of the geospatial data
    
    Args:
        file_path: Path to the file relative to uploads directory
        format: Output format (geojson for vectors, thumbnail for rasters)
        
    Returns:
        Preview data suitable for web visualization
    """
    try:
        full_path = storage_handler.get_file_path(file_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.tif', '.tiff']:
            # For rasters, return bounds and basic info for now
            # TODO: Implement thumbnail generation
            metadata = await _get_raster_metadata(full_path)
            return {
                "type": "raster_preview",
                "bounds": metadata["bounds"],
                "crs": metadata["crs"],
                "message": "Raster preview - bounds only for now"
            }
        elif file_extension in ['.shp', '.geojson', '.json']:
            # For vectors, convert to GeoJSON for display
            geojson_data = await _convert_to_geojson(full_path)
            return geojson_data
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


async def _get_raster_metadata(file_path: str) -> Dict[str, Any]:
    """Get metadata for raster files"""
    try:
        import rasterio
        
        with rasterio.open(file_path) as src:
            # Get basic raster information
            metadata = {
                "type": "raster",
                "driver": src.driver,
                "width": src.width,
                "height": src.height,
                "count": src.count,
                "dtype": str(src.dtypes[0]),
                "crs": src.crs.to_string() if src.crs else None,
                "bounds": list(src.bounds),
                "transform": list(src.transform),
                "nodata": src.nodata,
                "description": src.descriptions[0] if src.descriptions else None,
                "tags": dict(src.tags()) if src.tags() else {}
            }
            
            # Add additional useful information
            metadata["resolution"] = [abs(src.transform[0]), abs(src.transform[4])]
            metadata["pixel_count"] = src.width * src.height
            
            # Get band information
            bands = []
            for i in range(1, src.count + 1):
                band_stats = src.statistics(i)
                bands.append({
                    "index": i,
                    "dtype": str(src.dtypes[i-1]),
                    "nodata": src.nodatavals[i-1],
                    "min": band_stats.min if band_stats else None,
                    "max": band_stats.max if band_stats else None,
                    "mean": band_stats.mean if band_stats else None,
                    "std": band_stats.std if band_stats else None
                })
            
            metadata["bands"] = bands
            
        return metadata
        
    except Exception as e:
        logger.error(f"Error reading raster metadata from {file_path}: {e}")
        raise


async def _get_vector_metadata(file_path: str) -> Dict[str, Any]:
    """Get metadata for vector files"""
    try:
        import geopandas as gpd
        
        # Read vector file
        gdf = gpd.read_file(file_path)
        
        metadata = {
            "type": "vector",
            "driver": "Shapefile" if file_path.endswith('.shp') else "GeoJSON",
            "feature_count": len(gdf),
            "crs": gdf.crs.to_string() if gdf.crs else None,
            "bounds": list(gdf.total_bounds),
            "geometry_type": gdf.geom_type.iloc[0] if len(gdf) > 0 else None,
            "columns": list(gdf.columns),
            "column_types": {col: str(gdf[col].dtype) for col in gdf.columns if col != 'geometry'}
        }
        
        # Add geometry type distribution
        if len(gdf) > 0:
            geom_types = gdf.geom_type.value_counts().to_dict()
            metadata["geometry_types"] = geom_types
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error reading vector metadata from {file_path}: {e}")
        raise


async def _convert_to_geojson(file_path: str) -> Dict[str, Any]:
    """Convert vector file to GeoJSON for web display"""
    try:
        import geopandas as gpd
        
        # Read vector file
        gdf = gpd.read_file(file_path)
        
        # Convert to WGS84 for web display if needed
        if gdf.crs and gdf.crs.to_string() != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        # Limit features for performance (show first 1000 features)
        if len(gdf) > 1000:
            gdf = gdf.head(1000)
            logger.info(f"Limited vector preview to first 1000 features")
        
        # Convert to GeoJSON
        geojson = json.loads(gdf.to_json())
        
        # Add metadata
        geojson["metadata"] = {
            "original_feature_count": len(gdf),
            "preview_feature_count": len(geojson["features"]),
            "crs": "EPSG:4326",
            "bounds": list(gdf.total_bounds)
        }
        
        return geojson
        
    except Exception as e:
        logger.error(f"Error converting {file_path} to GeoJSON: {e}")
        raise


@router.get("/files")
async def list_uploaded_files() -> List[Dict[str, Any]]:
    """
    List all uploaded files with basic metadata
    
    Returns:
        List of files with basic information
    """
    try:
        files = storage_handler.list_files()
        file_list = []
        
        for file_name in files:
            if file_name.startswith('.'):
                continue
                
            file_path = storage_handler.get_file_path(file_name)
            file_info = {
                "name": file_name,
                "path": file_name,
                "size": os.path.getsize(file_path),
                "extension": os.path.splitext(file_name)[1].lower(),
                "modified": os.path.getmtime(file_path)
            }
            
            # Determine file type
            ext = file_info["extension"]
            if ext in ['.tif', '.tiff']:
                file_info["type"] = "raster"
            elif ext in ['.shp', '.geojson', '.json']:
                file_info["type"] = "vector"
            else:
                file_info["type"] = "unknown"
            
            file_list.append(file_info)
        
        # Sort by modification time (newest first)
        file_list.sort(key=lambda x: x["modified"], reverse=True)
        
        logger.info(f"Listed {len(file_list)} uploaded files")
        return file_list
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
