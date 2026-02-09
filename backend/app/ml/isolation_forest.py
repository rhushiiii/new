"""
Isolation Forest anomaly detection model.
Primary model for detecting electricity theft patterns.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os


class IsolationForestDetector:
    """
    Isolation Forest based anomaly detector for electricity consumption.
    
    The model identifies anomalies by isolating observations. Anomalies are 
    easier to isolate and thus have shorter path lengths in the tree.
    """
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize the detector.
        
        Args:
            contamination: Expected proportion of anomalies (0-0.5)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        # Feature importance for explainability
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
        
        # Thresholds for explanation generation
        self.thresholds = {
            'night_ratio': {'high': 1.5, 'low': 0.5, 'desc': 'night-time consumption'},
            'peak_ratio': {'high': 1.5, 'low': 0.5, 'desc': 'peak hour consumption'},
            'daily_variance': {'high': 2.0, 'desc': 'daily consumption variance'},
            'consumption_std': {'high': 2.0, 'desc': 'consumption variability'},
            'hourly_avg': {'high': 2.0, 'low': 0.3, 'desc': 'average consumption'},
        }
    
    def fit(self, features: np.ndarray) -> 'IsolationForestDetector':
        """
        Fit the model on feature data.
        
        Args:
            features: 2D array of shape (n_samples, n_features)
            
        Returns:
            self
        """
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Initialize and fit Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        self.model.fit(scaled_features)
        self.is_fitted = True
        
        return self
    
    def predict(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomaly scores and labels.
        
        Args:
            features: 2D array of shape (n_samples, n_features)
            
        Returns:
            Tuple of (anomaly_scores, is_anomaly)
            - anomaly_scores: float array in range [0, 1], higher = more anomalous
            - is_anomaly: boolean array
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Scale features
        scaled_features = self.scaler.transform(features)
        
        # Get raw scores (negative = more anomalous in sklearn)
        raw_scores = self.model.decision_function(scaled_features)
        
        # Convert to 0-1 range where 1 = most anomalous
        # decision_function returns negative values for anomalies
        # Normalize using sigmoid-like transformation
        min_score = raw_scores.min()
        max_score = raw_scores.max()
        if max_score - min_score > 0:
            normalized_scores = 1 - (raw_scores - min_score) / (max_score - min_score)
        else:
            normalized_scores = np.zeros_like(raw_scores)
        
        # Get predictions (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(scaled_features)
        is_anomaly = predictions == -1
        
        return normalized_scores, is_anomaly
    
    def fit_predict(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Fit model and predict in one step."""
        self.fit(features)
        return self.predict(features)
    
    def generate_explanation(
        self, 
        features: Dict[str, float],
        anomaly_score: float,
        is_suspicious: bool
    ) -> str:
        """
        Generate human-readable explanation for why a meter was flagged.
        
        Args:
            features: Feature dictionary for the meter
            anomaly_score: The computed anomaly score
            is_suspicious: Whether the meter was flagged as suspicious
            
        Returns:
            Explanation string
        """
        if not is_suspicious:
            return "No anomalies detected. Consumption patterns appear normal."
        
        explanations = []
        
        # Check each feature against thresholds
        for feature_name, thresholds in self.thresholds.items():
            value = features.get(feature_name, 0)
            desc = thresholds['desc']
            
            if 'high' in thresholds and value > thresholds['high']:
                if feature_name == 'night_ratio':
                    explanations.append(f"Unusually high {desc} ({value:.1%} of expected)")
                elif feature_name == 'daily_variance':
                    explanations.append(f"High {desc} indicating irregular usage patterns")
                elif feature_name == 'consumption_std':
                    explanations.append(f"Highly variable consumption suggesting irregular patterns")
                elif feature_name == 'hourly_avg':
                    explanations.append(f"Extremely high {desc} compared to typical households")
                else:
                    explanations.append(f"Elevated {desc}")
            
            if 'low' in thresholds and value < thresholds['low']:
                if feature_name == 'night_ratio':
                    explanations.append(f"Abnormally low {desc} ({value:.1%} of expected)")
                elif feature_name == 'hourly_avg':
                    explanations.append(f"Suspiciously low {desc} - possible meter tampering")
                else:
                    explanations.append(f"Unusually low {desc}")
        
        # Check for consumption spikes
        if features.get('consumption_range', 0) > features.get('hourly_avg', 1) * 5:
            explanations.append("Extreme consumption spikes detected")
        
        if not explanations:
            explanations.append("Unusual consumption pattern detected by statistical analysis")
        
        # Add severity indicator
        if anomaly_score > 0.8:
            severity = "CRITICAL"
        elif anomaly_score > 0.6:
            severity = "HIGH"
        elif anomaly_score > 0.4:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        explanation = f"[{severity} RISK] " + "; ".join(explanations) + "."
        
        return explanation
    
    def get_risk_level(self, anomaly_score: float) -> str:
        """Convert anomaly score to risk level category."""
        if anomaly_score >= 0.75:
            return "critical"
        elif anomaly_score >= 0.5:
            return "high"
        elif anomaly_score >= 0.25:
            return "medium"
        else:
            return "low"
    
    def save(self, path: str):
        """Save model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'contamination': self.contamination
        }, path)
    
    def load(self, path: str):
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.contamination = data['contamination']
        self.is_fitted = True
