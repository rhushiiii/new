"""
Feature Engineering for electricity consumption anomaly detection.
Extracts meaningful features from raw time-series meter data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class FeatureEngineer:
    """
    Extracts features from smart meter readings for anomaly detection.
    
    Features extracted:
    - Hourly average consumption
    - Daily variance
    - Night-time usage ratio (10 PM - 6 AM)
    - Peak hour ratio
    - Weekend vs weekday ratio
    - Consumption trend
    """
    
    # Night hours: 10 PM (22) to 6 AM (6)
    NIGHT_HOURS = list(range(22, 24)) + list(range(0, 6))
    
    # Peak hours: 6 PM to 10 PM
    PEAK_HOURS = list(range(18, 22))
    
    def __init__(self):
        self.feature_names = [
            'hourly_avg',
            'daily_variance', 
            'night_ratio',
            'peak_ratio',
            'weekend_ratio',
            'consumption_std',
            'max_consumption',
            'min_consumption',
            'consumption_range'
        ]
    
    def extract_features(self, readings: List[Dict]) -> Dict[str, float]:
        """
        Extract features from a list of readings for a single meter.
        
        Args:
            readings: List of dicts with 'timestamp' and 'consumption_kwh'
            
        Returns:
            Dictionary of feature names to values
        """
        if not readings:
            return self._empty_features()
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Extract time components
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['date'] = df['timestamp'].dt.date
        
        consumption = df['consumption_kwh'].values
        
        features = {}
        
        # Basic statistics
        features['hourly_avg'] = float(np.mean(consumption))
        features['consumption_std'] = float(np.std(consumption))
        features['max_consumption'] = float(np.max(consumption))
        features['min_consumption'] = float(np.min(consumption))
        features['consumption_range'] = features['max_consumption'] - features['min_consumption']
        
        # Daily variance - average variance per day
        daily_groups = df.groupby('date')['consumption_kwh']
        if len(daily_groups) > 0:
            daily_variances = daily_groups.var().dropna()
            features['daily_variance'] = float(daily_variances.mean()) if len(daily_variances) > 0 else 0.0
        else:
            features['daily_variance'] = 0.0
        
        # Night-time usage ratio
        night_mask = df['hour'].isin(self.NIGHT_HOURS)
        total_consumption = consumption.sum()
        if total_consumption > 0:
            night_consumption = df.loc[night_mask, 'consumption_kwh'].sum()
            # Normalize by the proportion of night hours
            night_hour_ratio = len(self.NIGHT_HOURS) / 24
            expected_night = total_consumption * night_hour_ratio
            features['night_ratio'] = float(night_consumption / expected_night) if expected_night > 0 else 1.0
        else:
            features['night_ratio'] = 1.0
        
        # Peak hour ratio
        peak_mask = df['hour'].isin(self.PEAK_HOURS)
        if total_consumption > 0:
            peak_consumption = df.loc[peak_mask, 'consumption_kwh'].sum()
            peak_hour_ratio = len(self.PEAK_HOURS) / 24
            expected_peak = total_consumption * peak_hour_ratio
            features['peak_ratio'] = float(peak_consumption / expected_peak) if expected_peak > 0 else 1.0
        else:
            features['peak_ratio'] = 1.0
        
        # Weekend vs weekday ratio
        weekend_mask = df['day_of_week'].isin([5, 6])  # Saturday, Sunday
        weekday_mask = ~weekend_mask
        weekend_consumption = df.loc[weekend_mask, 'consumption_kwh'].sum()
        weekday_consumption = df.loc[weekday_mask, 'consumption_kwh'].sum()
        
        # Normalize by expected proportions (2/7 weekend, 5/7 weekday)
        if weekday_consumption > 0:
            weekend_expected_ratio = 2 / 5  # Weekend days / Weekday days
            actual_ratio = weekend_consumption / weekday_consumption if weekday_consumption > 0 else 0
            features['weekend_ratio'] = float(actual_ratio / weekend_expected_ratio) if weekend_expected_ratio > 0 else 1.0
        else:
            features['weekend_ratio'] = 1.0 if weekend_consumption == 0 else 2.0
        
        return features
    
    def extract_features_batch(self, readings_by_meter: Dict[str, List[Dict]]) -> Dict[str, Dict[str, float]]:
        """
        Extract features for multiple meters.
        
        Args:
            readings_by_meter: Dict mapping meter_id to list of readings
            
        Returns:
            Dict mapping meter_id to feature dict
        """
        return {
            meter_id: self.extract_features(readings)
            for meter_id, readings in readings_by_meter.items()
        }
    
    def _empty_features(self) -> Dict[str, float]:
        """Return empty feature dict with zeros."""
        return {name: 0.0 for name in self.feature_names}
    
    def features_to_array(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dict to numpy array in consistent order."""
        return np.array([features.get(name, 0.0) for name in self.feature_names])
    
    def batch_to_array(self, features_by_meter: Dict[str, Dict[str, float]]) -> Tuple[List[str], np.ndarray]:
        """
        Convert batch of features to array format for ML models.
        
        Returns:
            Tuple of (meter_ids list, features array)
        """
        meter_ids = list(features_by_meter.keys())
        features_array = np.array([
            self.features_to_array(features_by_meter[mid])
            for mid in meter_ids
        ])
        return meter_ids, features_array
