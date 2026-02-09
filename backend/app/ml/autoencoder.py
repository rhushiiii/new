"""
Autoencoder-based anomaly detection model.
Alternative model using neural network reconstruction error.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
import os

# Optional TensorFlow import - will work without it
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class AutoencoderDetector:
    """
    Autoencoder-based anomaly detector using reconstruction error.
    
    The model learns to reconstruct normal consumption patterns.
    High reconstruction error indicates anomalous behavior.
    """
    
    def __init__(
        self, 
        encoding_dim: int = 4,
        threshold_percentile: float = 95,
        epochs: int = 50,
        batch_size: int = 32
    ):
        """
        Initialize the detector.
        
        Args:
            encoding_dim: Size of the bottleneck layer
            threshold_percentile: Percentile for anomaly threshold
            epochs: Training epochs
            batch_size: Training batch size
        """
        self.encoding_dim = encoding_dim
        self.threshold_percentile = threshold_percentile
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.model = None
        self.scaler = StandardScaler()
        self.threshold = None
        self.is_fitted = False
        self.input_dim = None
        
        if not TF_AVAILABLE:
            print("Warning: TensorFlow not available. Autoencoder will use fallback mode.")
    
    def _build_model(self, input_dim: int) -> 'keras.Model':
        """Build the autoencoder architecture."""
        if not TF_AVAILABLE:
            return None
            
        # Encoder
        inputs = keras.Input(shape=(input_dim,))
        x = layers.Dense(16, activation='relu')(inputs)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(8, activation='relu')(x)
        encoded = layers.Dense(self.encoding_dim, activation='relu')(x)
        
        # Decoder
        x = layers.Dense(8, activation='relu')(encoded)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(16, activation='relu')(x)
        decoded = layers.Dense(input_dim, activation='linear')(x)
        
        autoencoder = keras.Model(inputs, decoded)
        autoencoder.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse'
        )
        
        return autoencoder
    
    def fit(self, features: np.ndarray) -> 'AutoencoderDetector':
        """
        Fit the model on feature data.
        
        Args:
            features: 2D array of shape (n_samples, n_features)
            
        Returns:
            self
        """
        self.input_dim = features.shape[1]
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        if TF_AVAILABLE:
            # Build and train model
            self.model = self._build_model(self.input_dim)
            
            # Early stopping
            early_stop = keras.callbacks.EarlyStopping(
                monitor='loss',
                patience=5,
                restore_best_weights=True
            )
            
            self.model.fit(
                scaled_features,
                scaled_features,
                epochs=self.epochs,
                batch_size=self.batch_size,
                shuffle=True,
                callbacks=[early_stop],
                verbose=0
            )
            
            # Calculate reconstruction error threshold
            reconstructions = self.model.predict(scaled_features, verbose=0)
            mse = np.mean(np.power(scaled_features - reconstructions, 2), axis=1)
            self.threshold = np.percentile(mse, self.threshold_percentile)
        else:
            # Fallback: use simple statistics
            self.mean_features = np.mean(scaled_features, axis=0)
            self.std_features = np.std(scaled_features, axis=0)
            self.threshold = 2.0  # 2 standard deviations
        
        self.is_fitted = True
        return self
    
    def predict(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomaly scores and labels.
        
        Args:
            features: 2D array of shape (n_samples, n_features)
            
        Returns:
            Tuple of (anomaly_scores, is_anomaly)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        scaled_features = self.scaler.transform(features)
        
        if TF_AVAILABLE and self.model is not None:
            # Get reconstruction error
            reconstructions = self.model.predict(scaled_features, verbose=0)
            mse = np.mean(np.power(scaled_features - reconstructions, 2), axis=1)
            
            # Normalize to 0-1 range
            anomaly_scores = np.clip(mse / (self.threshold * 2), 0, 1)
            is_anomaly = mse > self.threshold
        else:
            # Fallback: use distance from mean
            z_scores = np.abs((scaled_features - self.mean_features) / (self.std_features + 1e-8))
            max_z = np.max(z_scores, axis=1)
            
            anomaly_scores = np.clip(max_z / 4, 0, 1)  # Normalize
            is_anomaly = max_z > self.threshold
        
        return anomaly_scores, is_anomaly
    
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
        """Generate human-readable explanation."""
        if not is_suspicious:
            return "No anomalies detected. Consumption patterns appear normal."
        
        explanations = []
        
        # Analyze which features deviate most
        if features.get('night_ratio', 1) > 1.5:
            explanations.append("Unusual night-time consumption spike detected")
        elif features.get('night_ratio', 1) < 0.5:
            explanations.append("Abnormally low night-time consumption")
        
        if features.get('daily_variance', 0) > 2.0:
            explanations.append("Highly irregular daily consumption patterns")
        
        if features.get('consumption_std', 0) > 2.0:
            explanations.append("Extreme variability in consumption")
        
        if not explanations:
            explanations.append("Consumption pattern differs significantly from normal behavior")
        
        severity = "HIGH" if anomaly_score > 0.7 else "MEDIUM" if anomaly_score > 0.4 else "LOW"
        
        return f"[{severity} RISK - Autoencoder] " + "; ".join(explanations) + "."
    
    def get_risk_level(self, anomaly_score: float) -> str:
        """Convert anomaly score to risk level."""
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
        
        if TF_AVAILABLE and self.model is not None:
            self.model.save(path + '_keras')
        
        import joblib
        joblib.dump({
            'scaler': self.scaler,
            'threshold': self.threshold,
            'input_dim': self.input_dim,
            'encoding_dim': self.encoding_dim
        }, path + '_meta.joblib')
    
    def load(self, path: str):
        """Load model from disk."""
        import joblib
        
        if TF_AVAILABLE and os.path.exists(path + '_keras'):
            self.model = keras.models.load_model(path + '_keras')
        
        meta = joblib.load(path + '_meta.joblib')
        self.scaler = meta['scaler']
        self.threshold = meta['threshold']
        self.input_dim = meta['input_dim']
        self.encoding_dim = meta['encoding_dim']
        self.is_fitted = True
