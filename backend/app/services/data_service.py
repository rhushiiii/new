"""
Data service for managing meter readings and database operations.
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ..models.schemas import Meter, Reading, AnomalyResult
from ..models.pydantic_schemas import UploadResponse


class DataService:
    """Service for handling meter data operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def parse_and_store_csv(self, csv_content: str) -> UploadResponse:
        """
        Parse CSV content and store in database.
        
        Expected CSV format:
        meter_id,timestamp,consumption_kwh
        
        Args:
            csv_content: Raw CSV string
            
        Returns:
            UploadResponse with statistics
        """
        errors = []
        meters_created = set()
        readings_created = 0
        
        try:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_content))
            
            # Validate headers
            required_headers = {'meter_id', 'timestamp', 'consumption_kwh'}
            if not required_headers.issubset(set(reader.fieldnames or [])):
                return UploadResponse(
                    success=False,
                    message=f"Missing required headers. Expected: {required_headers}",
                    meters_count=0,
                    readings_count=0,
                    errors=["Invalid CSV format"]
                )
            
            readings_to_insert = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    meter_id = row['meter_id'].strip()
                    timestamp_str = row['timestamp'].strip()
                    consumption = float(row['consumption_kwh'])
                    
                    # Parse timestamp (supports multiple formats)
                    timestamp = self._parse_timestamp(timestamp_str)
                    
                    if meter_id not in meters_created:
                        # Create meter if not exists
                        await self._get_or_create_meter(meter_id)
                        meters_created.add(meter_id)
                    
                    readings_to_insert.append({
                        'meter_id': meter_id,
                        'timestamp': timestamp,
                        'consumption_kwh': consumption
                    })
                    
                except ValueError as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                except KeyError as e:
                    errors.append(f"Row {row_num}: Missing column {str(e)}")
            
            # Bulk insert readings
            if readings_to_insert:
                for reading_data in readings_to_insert:
                    reading = Reading(**reading_data)
                    self.db.add(reading)
                readings_created = len(readings_to_insert)
            
            await self.db.commit()
            
            return UploadResponse(
                success=True,
                message=f"Successfully uploaded {readings_created} readings for {len(meters_created)} meters",
                meters_count=len(meters_created),
                readings_count=readings_created,
                errors=errors[:10]  # Limit errors shown
            )
            
        except Exception as e:
            await self.db.rollback()
            return UploadResponse(
                success=False,
                message=f"Upload failed: {str(e)}",
                meters_count=0,
                readings_count=0,
                errors=[str(e)]
            )
    
    async def _get_or_create_meter(self, meter_id: str) -> Meter:
        """Get existing meter or create new one."""
        result = await self.db.execute(
            select(Meter).where(Meter.meter_id == meter_id)
        )
        meter = result.scalar_one_or_none()
        
        if not meter:
            meter = Meter(meter_id=meter_id)
            self.db.add(meter)
            await self.db.flush()
        
        return meter
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp from various formats."""
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%m/%d/%Y %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")
    
    async def get_all_meters(self) -> List[Meter]:
        """Get all meters."""
        result = await self.db.execute(select(Meter))
        return result.scalars().all()
    
    async def get_meter_ids(self) -> List[str]:
        """Get all meter IDs."""
        result = await self.db.execute(select(Meter.meter_id))
        return [row[0] for row in result.fetchall()]
    
    async def get_readings_for_meter(self, meter_id: str) -> List[Reading]:
        """Get all readings for a specific meter."""
        result = await self.db.execute(
            select(Reading)
            .where(Reading.meter_id == meter_id)
            .order_by(Reading.timestamp)
        )
        return result.scalars().all()
    
    async def get_readings_by_meter(self) -> Dict[str, List[Dict]]:
        """Get all readings grouped by meter."""
        result = await self.db.execute(
            select(Reading).order_by(Reading.meter_id, Reading.timestamp)
        )
        readings = result.scalars().all()
        
        readings_by_meter = {}
        for reading in readings:
            if reading.meter_id not in readings_by_meter:
                readings_by_meter[reading.meter_id] = []
            readings_by_meter[reading.meter_id].append({
                'timestamp': reading.timestamp,
                'consumption_kwh': reading.consumption_kwh
            })
        
        return readings_by_meter
    
    async def save_anomaly_result(self, result_data: Dict) -> AnomalyResult:
        """Save or update anomaly result for a meter."""
        # Delete existing result for this meter
        await self.db.execute(
            delete(AnomalyResult).where(AnomalyResult.meter_id == result_data['meter_id'])
        )
        
        # Create new result
        anomaly_result = AnomalyResult(**result_data)
        self.db.add(anomaly_result)
        await self.db.flush()
        
        return anomaly_result
    
    async def get_anomaly_results(self) -> List[AnomalyResult]:
        """Get all anomaly results."""
        result = await self.db.execute(
            select(AnomalyResult).order_by(AnomalyResult.anomaly_score.desc())
        )
        return result.scalars().all()
    
    async def get_anomaly_result_for_meter(self, meter_id: str) -> Optional[AnomalyResult]:
        """Get anomaly result for a specific meter."""
        result = await self.db.execute(
            select(AnomalyResult).where(AnomalyResult.meter_id == meter_id)
        )
        return result.scalar_one_or_none()
    
    async def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard."""
        # Total meters
        total_meters_result = await self.db.execute(
            select(func.count(Meter.id))
        )
        total_meters = total_meters_result.scalar() or 0
        
        # Total readings
        total_readings_result = await self.db.execute(
            select(func.count(Reading.id))
        )
        total_readings = total_readings_result.scalar() or 0
        
        # Suspicious meters
        suspicious_result = await self.db.execute(
            select(func.count(AnomalyResult.id)).where(AnomalyResult.is_suspicious == True)
        )
        suspicious_meters = suspicious_result.scalar() or 0
        
        # Risk level counts
        high_risk_result = await self.db.execute(
            select(func.count(AnomalyResult.id)).where(
                AnomalyResult.risk_level.in_(['high', 'critical'])
            )
        )
        high_risk = high_risk_result.scalar() or 0
        
        medium_risk_result = await self.db.execute(
            select(func.count(AnomalyResult.id)).where(AnomalyResult.risk_level == 'medium')
        )
        medium_risk = medium_risk_result.scalar() or 0
        
        low_risk_result = await self.db.execute(
            select(func.count(AnomalyResult.id)).where(AnomalyResult.risk_level == 'low')
        )
        low_risk = low_risk_result.scalar() or 0
        
        # Last detection time
        last_detection_result = await self.db.execute(
            select(func.max(AnomalyResult.detection_timestamp))
        )
        last_detection = last_detection_result.scalar()
        
        return {
            'total_meters': total_meters,
            'total_readings': total_readings,
            'suspicious_meters': suspicious_meters,
            'suspicious_percentage': (suspicious_meters / total_meters * 100) if total_meters > 0 else 0,
            'high_risk_count': high_risk,
            'medium_risk_count': medium_risk,
            'low_risk_count': low_risk,
            'last_detection': last_detection
        }
    
    async def clear_all_data(self):
        """Clear all data from database (for testing)."""
        await self.db.execute(delete(AnomalyResult))
        await self.db.execute(delete(Reading))
        await self.db.execute(delete(Meter))
        await self.db.commit()
