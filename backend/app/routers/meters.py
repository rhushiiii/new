"""
Meters router for meter-specific operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..services.data_service import DataService
from ..services.ml_service import MLService
from ..models.pydantic_schemas import (
    MeterResponse,
    MeterTimeSeries,
    ReadingDataPoint,
    AnomalyResultResponse
)

router = APIRouter(prefix="/meters", tags=["Meters"])


@router.get(
    "/",
    response_model=List[MeterResponse],
    summary="List all meters",
    description="Get list of all registered meters"
)
async def list_meters(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all registered meters.
    """
    data_service = DataService(db)
    meters = await data_service.get_all_meters()
    return meters[:limit]


@router.get(
    "/ids",
    response_model=List[str],
    summary="List all meter IDs",
    description="Get list of all meter IDs for dropdown selection"
)
async def list_meter_ids(db: AsyncSession = Depends(get_db)):
    """
    Get all meter IDs for UI dropdowns.
    """
    data_service = DataService(db)
    return await data_service.get_meter_ids()


@router.get(
    "/{meter_id}",
    response_model=MeterTimeSeries,
    summary="Get meter time series",
    description="Get consumption time series data for a specific meter"
)
async def get_meter_data(
    meter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get time series data and anomaly info for a specific meter.
    """
    data_service = DataService(db)
    ml_service = MLService(db)
    
    # Get readings
    readings = await data_service.get_readings_for_meter(meter_id)
    
    if not readings:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for meter {meter_id}"
        )
    
    # Get anomaly result if exists
    anomaly_result = await data_service.get_anomaly_result_for_meter(meter_id)
    
    # Get detailed analysis for stats
    analysis = await ml_service.get_meter_analysis(meter_id)
    
    # Convert readings to response format with anomaly flags
    reading_points = []
    for r in readings:
        reading_points.append(ReadingDataPoint(
            timestamp=r.timestamp,
            consumption_kwh=r.consumption_kwh,
            is_anomaly=False  # Individual reading anomalies could be added here
        ))
    
    # Mark anomalous readings (simplified: flag high consumption points)
    if anomaly_result and anomaly_result.is_suspicious:
        avg = analysis['features'].get('hourly_avg', 0) if analysis else 0
        std = analysis['features'].get('consumption_std', 0) if analysis else 0
        threshold = avg + 2 * std if std > 0 else avg * 2
        
        for point in reading_points:
            if point.consumption_kwh > threshold:
                point.is_anomaly = True
    
    return MeterTimeSeries(
        meter_id=meter_id,
        readings=reading_points,
        anomaly_result=AnomalyResultResponse.model_validate(anomaly_result) if anomaly_result else None,
        stats=analysis['features'] if analysis else {}
    )


@router.get(
    "/{meter_id}/analysis",
    summary="Get detailed meter analysis",
    description="Get detailed feature analysis for a meter"
)
async def get_meter_analysis(
    meter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analysis including computed features.
    """
    ml_service = MLService(db)
    analysis = await ml_service.get_meter_analysis(meter_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for meter {meter_id}"
        )
    
    return analysis
