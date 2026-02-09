"""
SQLAlchemy ORM models for PowerGuard database.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Meter(Base):
    """Smart meter entity."""
    __tablename__ = "meters"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), unique=True, index=True, nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    readings = relationship("Reading", back_populates="meter", cascade="all, delete-orphan")
    anomaly_results = relationship("AnomalyResult", back_populates="meter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Meter(id={self.id}, meter_id='{self.meter_id}')>"


class Reading(Base):
    """Hourly electricity consumption reading."""
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), ForeignKey("meters.meter_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    consumption_kwh = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meter = relationship("Meter", back_populates="readings")
    
    def __repr__(self):
        return f"<Reading(meter_id='{self.meter_id}', timestamp={self.timestamp}, kwh={self.consumption_kwh})>"


class AnomalyResult(Base):
    """ML anomaly detection results for each meter."""
    __tablename__ = "anomaly_results"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), ForeignKey("meters.meter_id"), nullable=False, index=True)
    
    # Anomaly detection results
    anomaly_score = Column(Float, nullable=False)  # 0-1 score
    is_suspicious = Column(Boolean, default=False)
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    
    # Feature values used for detection
    hourly_avg = Column(Float, nullable=True)
    daily_variance = Column(Float, nullable=True)
    night_ratio = Column(Float, nullable=True)
    
    # Explainability
    explanation = Column(Text, nullable=True)
    
    # Model info
    model_used = Column(String(50), default="isolation_forest")
    detection_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meter = relationship("Meter", back_populates="anomaly_results")
    
    def __repr__(self):
        return f"<AnomalyResult(meter_id='{self.meter_id}', score={self.anomaly_score}, suspicious={self.is_suspicious})>"
