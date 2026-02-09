"""
Upload router for CSV data ingestion.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.data_service import DataService
from ..models.pydantic_schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/data",
    response_model=UploadResponse,
    summary="Upload smart meter data",
    description="""
    Upload a CSV file containing smart meter readings.
    
    Expected CSV format:
    - meter_id: Unique identifier for the meter
    - timestamp: ISO datetime (YYYY-MM-DDTHH:MM:SS)
    - consumption_kwh: Energy consumption in kWh
    """
)
async def upload_data(
    file: UploadFile = File(..., description="CSV file with meter readings"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload CSV data with smart meter readings.
    
    The CSV should have columns: meter_id, timestamp, consumption_kwh
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    # Read file content
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File encoding not supported. Please use UTF-8"
        )
    
    # Parse and store data
    data_service = DataService(db)
    result = await data_service.parse_and_store_csv(csv_content)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@router.post(
    "/clear",
    summary="Clear all data",
    description="Remove all meters, readings, and anomaly results from the database"
)
async def clear_data(db: AsyncSession = Depends(get_db)):
    """Clear all data from the database (for testing/reset)."""
    data_service = DataService(db)
    await data_service.clear_all_data()
    return {"success": True, "message": "All data cleared"}
