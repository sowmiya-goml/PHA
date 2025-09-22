"""SQLAlchemy database models for patient dashboard functionality."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Patient(Base):
    """Patient model for storing patient information."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)  # External patient ID
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_type = Column(String(10), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    heart_rates = relationship("HeartRate", back_populates="patient", cascade="all, delete-orphan")
    blood_pressures = relationship("BloodPressure", back_populates="patient", cascade="all, delete-orphan")
    bmis = relationship("BMI", back_populates="patient", cascade="all, delete-orphan")
    spo2_readings = relationship("SpO2", back_populates="patient", cascade="all, delete-orphan")
    temperatures = relationship("Temperature", back_populates="patient", cascade="all, delete-orphan")
    blood_sugars = relationship("BloodSugar", back_populates="patient", cascade="all, delete-orphan")
    recovery_records = relationship("RecoveryTracker", back_populates="patient", cascade="all, delete-orphan")


class HeartRate(Base):
    """Heart rate measurements for patients."""
    __tablename__ = "heart_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    heart_rate = Column(Integer, nullable=False)  # BPM
    status = Column(String(20), default="normal")  # normal, high, low, resting
    measurement_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationship
    patient = relationship("Patient", back_populates="heart_rates")


class BloodPressure(Base):
    """Blood pressure measurements for patients."""
    __tablename__ = "blood_pressures"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    systolic = Column(Integer, nullable=False)  # mmHg
    diastolic = Column(Integer, nullable=False)  # mmHg
    status = Column(String(20), default="normal")  # normal, high, low, hypertensive
    measurement_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationship
    patient = relationship("Patient", back_populates="blood_pressures")


class BMI(Base):
    """BMI calculations and tracking for patients."""
    __tablename__ = "bmis"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    height = Column(Float, nullable=False)  # cm
    weight = Column(Float, nullable=False)  # kg
    bmi_value = Column(Float, nullable=False)  # calculated BMI
    trend = Column(String(20), default="stable")  # increase, decrease, stable
    measurement_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationship
    patient = relationship("Patient", back_populates="bmis")


class SpO2(Base):
    """SpO2 (blood oxygen saturation) measurements."""
    __tablename__ = "spo2_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    spo2_percentage = Column(Float, nullable=False)  # percentage
    status = Column(String(20), default="normal")  # normal, low, critical
    measurement_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationship
    patient = relationship("Patient", back_populates="spo2_readings")


class Temperature(Base):
    """Body temperature measurements."""
    __tablename__ = "temperatures"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    temperature_celsius = Column(Float, nullable=False)  # Celsius
    temperature_fahrenheit = Column(Float, nullable=False)  # Fahrenheit
    status = Column(String(20), default="normal")  # normal, fever, hypothermia
    measurement_time = Column(DateTime, default=datetime.utcnow)
    measurement_site = Column(String(20), default="oral")  # oral, rectal, axillary, ear
    notes = Column(Text, nullable=True)
    
    # Relationship
    patient = relationship("Patient", back_populates="temperatures")


class BloodSugar(Base):
    """Blood glucose level measurements."""
    __tablename__ = "blood_sugars"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    glucose_level = Column(Float, nullable=False)  # mg/dL
    trend = Column(String(20), default="stable")  # stable, spike, drop
    measurement_time = Column(DateTime, default=datetime.utcnow)
    measurement_type = Column(String(20), default="random")  # fasting, random, post_meal
    notes = Column(Text, nullable=True)
    
    # Relationship
    patient = relationship("Patient", back_populates="blood_sugars")


class RecoveryTracker(Base):
    """Recovery progress tracking with timeseries data."""
    __tablename__ = "recovery_trackers"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_internal_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    recovery_score = Column(Float, nullable=False)  # 0-100 scale
    recovery_stage = Column(String(50), nullable=True)  # acute, recovery, maintenance
    measurement_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Additional recovery metrics
    mobility_score = Column(Float, nullable=True)  # 0-100
    pain_level = Column(Integer, nullable=True)  # 0-10 scale
    activity_level = Column(String(20), nullable=True)  # low, moderate, high
    
    # Relationship
    patient = relationship("Patient", back_populates="recovery_records")