from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    CLIP = "clip"
    REPROJECT = "reproject"
    RESAMPLE = "resample"
    MOSAIC = "mosaic"


class FileType(str, Enum):
    GEOTIFF = "geotiff"
    SHAPEFILE = "shapefile"
    GEOJSON = "geojson"


class JobCreate(BaseModel):
    job_type: JobType
    raster_files: List[str] = Field(..., description="List of raster file paths")
    vector_file: Optional[str] = Field(None, description="Vector file path for clipping")
    target_crs: Optional[str] = Field(None, description="Target CRS (e.g., EPSG:4326)")
    target_resolution: Optional[float] = Field(None, description="Target resolution in map units")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    job_type: JobType
    created_at: datetime
    updated_at: Optional[datetime] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    result_file: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    result_file: Optional[str] = None


class UploadResponse(BaseModel):
    filename: str
    file_path: str
    file_type: FileType
    file_size: int
    upload_time: datetime


class ClipRequest(BaseModel):
    raster_file: str = Field(..., description="Path to the raster file")
    vector_file: str = Field(..., description="Path to the vector file for clipping")
    output_name: Optional[str] = Field(None, description="Output filename")


class ReprojectRequest(BaseModel):
    raster_file: str = Field(..., description="Path to the raster file")
    target_crs: str = Field(..., description="Target CRS (e.g., EPSG:4326)")
    output_name: Optional[str] = Field(None, description="Output filename")


class ResampleRequest(BaseModel):
    raster_file: str = Field(..., description="Path to the raster file")
    target_resolution: float = Field(..., description="Target resolution in map units")
    resampling_method: Optional[str] = Field("bilinear", description="Resampling method")
    output_name: Optional[str] = Field(None, description="Output filename")


class MosaicRequest(BaseModel):
    raster_files: List[str] = Field(..., description="List of raster file paths")
    output_name: Optional[str] = Field(None, description="Output filename")
    method: Optional[str] = Field("first", description="Mosaic method (first, last, min, max, mean)")


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
