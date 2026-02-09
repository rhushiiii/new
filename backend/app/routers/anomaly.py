"""
Anomaly detection router for ML operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..services.ml_service import MLService
from ..services.data_service import DataService
from ..models.pydantic_schemas import (
    DetectionRequest, 
    DetectionResponse, 
    AnomalyResultResponse,
    DashboardStats
)

router = APIRouter(prefix="/anomaly", tags=["Anomaly Detection"])


@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Run anomaly detection",
    description="""
    Run ML-based anomaly detection on uploaded meter data.
    
    Available models:
    - isolation_forest: Fast, efficient, good for general anomaly detection
    - autoencoder: Neural network based, better for complex patterns
    """
)
async def detect_anomalies(
    request: DetectionRequest = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Run anomaly detection on all or specified meters.
    """
    if request is None:
        request = DetectionRequest()
    
    ml_service = MLService(db)
    
    try:
        results = await ml_service.run_detection(
            model=request.model,
            threshold=request.threshold,
            meter_ids=request.meter_ids
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )
    
    suspicious_count = sum(1 for r in results if r['is_suspicious'])
    
    # Convert to response format
    result_responses = [
        AnomalyResultResponse(
            id=i,
            meter_id=r['meter_id'],
            anomaly_score=r['anomaly_score'],
            is_suspicious=r['is_suspicious'],
            risk_level=r['risk_level'],
            hourly_avg=r.get('hourly_avg'),
            daily_variance=r.get('daily_variance'),
            night_ratio=r.get('night_ratio'),
            explanation=r.get('explanation'),
            model_used=r['model_used'],
            detection_timestamp=None
        )
        for i, r in enumerate(results)
    ]
    
    return DetectionResponse(
        success=True,
        message=f"Analyzed {len(results)} meters, found {suspicious_count} suspicious",
        meters_analyzed=len(results),
        suspicious_count=suspicious_count,
        results=result_responses
    )


@router.get(
    "/results",
    response_model=List[AnomalyResultResponse],
    summary="Get all anomaly results",
    description="Retrieve all stored anomaly detection results, sorted by score"
)
async def get_results(
    suspicious_only: bool = Query(False, description="Only return suspicious meters"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all anomaly detection results.
    """
    data_service = DataService(db)
    results = await data_service.get_anomaly_results()
    
    if suspicious_only:
        results = [r for r in results if r.is_suspicious]
    
    return results[:limit]


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get dashboard statistics",
    description="Get aggregated statistics for the dashboard"
)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get dashboard statistics including counts and percentages.
    """
    data_service = DataService(db)
    stats = await data_service.get_dashboard_stats()
    return DashboardStats(**stats)


@router.get(
    "/result/{meter_id}",
    response_model=AnomalyResultResponse,
    summary="Get result for specific meter",
    description="Get anomaly detection result for a specific meter"
)
async def get_meter_result(
    meter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get anomaly result for a specific meter.
    """
    data_service = DataService(db)
    result = await data_service.get_anomaly_result_for_meter(meter_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for meter {meter_id}"
        )
    
    return result
