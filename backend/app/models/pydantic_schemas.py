"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ============== Meter Schemas ==============

class MeterCreate(BaseModel):
    """Schema for creating a new meter."""
    meter_id: str = Field(..., min_length=1, max_length=50)
    location: Optional[str] = None


class MeterResponse(BaseModel):
    """Schema for meter response."""
    id: int
    meter_id: str
    location: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Reading Schemas ==============

class ReadingCreate(BaseModel):
    """Schema for creating a reading."""
    meter_id: str
    timestamp: datetime
    consumption_kwh: float = Field(..., ge=0)


class ReadingResponse(BaseModel):
    """Schema for reading response."""
    id: int
    meter_id: str
    timestamp: datetime
    consumption_kwh: float
    
    class Config:
        from_attributes = True


class ReadingDataPoint(BaseModel):
    """Single data point for time series."""
    timestamp: datetime
    consumption_kwh: float
    is_anomaly: bool = False


# ============== Anomaly Result Schemas ==============

class AnomalyResultCreate(BaseModel):
    """Schema for creating anomaly result."""
    meter_id: str
    anomaly_score: float = Field(..., ge=0, le=1)
    is_suspicious: bool
    risk_level: str = "low"
    hourly_avg: Optional[float] = None
    daily_variance: Optional[float] = None
    night_ratio: Optional[float] = None
    explanation: Optional[str] = None
    model_used: str = "isolation_forest"


class AnomalyResultResponse(BaseModel):
    """Schema for anomaly result response."""
    id: int
    meter_id: str
    anomaly_score: float
    is_suspicious: bool
    risk_level: str
    hourly_avg: Optional[float]
    daily_variance: Optional[float]
    night_ratio: Optional[float]
    explanation: Optional[str]
    model_used: str
    detection_timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============== API Request/Response Schemas ==============

class UploadResponse(BaseModel):
    """Response after uploading CSV data."""
    success: bool
    message: str
    meters_count: int
    readings_count: int
    errors: List[str] = []


class DetectionRequest(BaseModel):
    """Request for running anomaly detection."""
    model: str = Field(default="isolation_forest", pattern="^(isolation_forest|autoencoder)$")
    threshold: Optional[float] = Field(default=None, ge=0, le=1)
    meter_ids: Optional[List[str]] = None  # If None, detect for all meters


class DetectionResponse(BaseModel):
    """Response after running detection."""
    success: bool
    message: str
    meters_analyzed: int
    suspicious_count: int
    results: List[AnomalyResultResponse]


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_meters: int
    total_readings: int
    suspicious_meters: int
    suspicious_percentage: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    last_detection: Optional[datetime]


class MeterTimeSeries(BaseModel):
    """Time series data for a specific meter."""
    meter_id: str
    readings: List[ReadingDataPoint]
    anomaly_result: Optional[AnomalyResultResponse]
    stats: dict = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
