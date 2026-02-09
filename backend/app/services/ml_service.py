"""
ML service orchestrating feature engineering and anomaly detection.
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from ..ml.feature_engineering import FeatureEngineer
from ..ml.isolation_forest import IsolationForestDetector
from ..ml.autoencoder import AutoencoderDetector
from ..config import settings
from .data_service import DataService


class MLService:
    """Service for running ML anomaly detection pipeline."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.data_service = DataService(db)
        self.feature_engineer = FeatureEngineer()
        self.isolation_forest = IsolationForestDetector(
            contamination=settings.ISOLATION_FOREST_CONTAMINATION
        )
        self.autoencoder = AutoencoderDetector()
    
    async def run_detection(
        self,
        model: str = "isolation_forest",
        threshold: Optional[float] = None,
        meter_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Run anomaly detection on all or specified meters.
        
        Args:
            model: Model to use ('isolation_forest' or 'autoencoder')
            threshold: Optional custom threshold
            meter_ids: Optional list of specific meters to analyze
            
        Returns:
            List of detection results
        """
        # Get readings grouped by meter
        all_readings = await self.data_service.get_readings_by_meter()
        
        # Filter to specific meters if requested
        if meter_ids:
            all_readings = {
                mid: readings for mid, readings in all_readings.items()
                if mid in meter_ids
            }
        
        if not all_readings:
            return []
        
        # Extract features for all meters
        features_by_meter = self.feature_engineer.extract_features_batch(all_readings)
        
        # Convert to array format for ML
        meter_ids_list, features_array = self.feature_engineer.batch_to_array(features_by_meter)
        
        if len(features_array) == 0:
            return []
        
        # Select and run model
        if model == "autoencoder":
            detector = self.autoencoder
        else:
            detector = self.isolation_forest
        
        # Fit and predict
        anomaly_scores, is_anomaly = detector.fit_predict(features_array)
        
        # Apply custom threshold if provided
        if threshold is not None:
            is_anomaly = anomaly_scores >= threshold
        
        # Generate results with explanations
        results = []
        for i, meter_id in enumerate(meter_ids_list):
            score = float(anomaly_scores[i])
            suspicious = bool(is_anomaly[i])
            features = features_by_meter[meter_id]
            
            # Generate explanation
            explanation = detector.generate_explanation(features, score, suspicious)
            
            # Determine risk level
            risk_level = detector.get_risk_level(score)
            
            result_data = {
                'meter_id': meter_id,
                'anomaly_score': score,
                'is_suspicious': suspicious,
                'risk_level': risk_level,
                'hourly_avg': features.get('hourly_avg'),
                'daily_variance': features.get('daily_variance'),
                'night_ratio': features.get('night_ratio'),
                'explanation': explanation,
                'model_used': model
            }
            
            # Save to database
            await self.data_service.save_anomaly_result(result_data)
            results.append(result_data)
        
        await self.db.commit()
        
        return results
    
    async def get_meter_analysis(self, meter_id: str) -> Optional[Dict]:
        """
        Get detailed analysis for a specific meter.
        
        Returns:
            Dict with readings, features, and anomaly result
        """
        # Get readings
        readings = await self.data_service.get_readings_for_meter(meter_id)
        if not readings:
            return None
        
        # Convert readings to dicts
        readings_data = [
            {'timestamp': r.timestamp, 'consumption_kwh': r.consumption_kwh}
            for r in readings
        ]
        
        # Calculate features
        features = self.feature_engineer.extract_features(readings_data)
        
        # Get anomaly result
        anomaly_result = await self.data_service.get_anomaly_result_for_meter(meter_id)
        
        return {
            'meter_id': meter_id,
            'readings_count': len(readings_data),
            'features': features,
            'anomaly_result': anomaly_result
        }
