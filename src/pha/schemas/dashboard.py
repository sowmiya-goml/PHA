"""Patient dashboard schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HeartRateResponse(BaseModel):
    """Schema for heart rate response."""
    heart_rate: int = Field(..., description="Heart rate in beats per minute")
    status: str = Field(..., description="Heart rate status (e.g., resting, active, elevated)")
    timestamp: datetime = Field(..., description="Timestamp when measurement was taken")


class BloodPressureResponse(BaseModel):
    """Schema for blood pressure response."""
    systolic: int = Field(..., description="Systolic blood pressure")
    diastolic: int = Field(..., description="Diastolic blood pressure")
    status: str = Field(..., description="Blood pressure status (e.g., normal, elevated, high)")
    timestamp: datetime = Field(..., description="Timestamp when measurement was taken")


class BMIResponse(BaseModel):
    """Schema for BMI response."""
    bmi_value: float = Field(..., description="BMI value")
    trend: str = Field(..., description="BMI trend (increase, decrease, stable)")
    timestamp: datetime = Field(..., description="Timestamp when measurement was taken")
    weight: Optional[float] = Field(None, description="Weight in kg")
    height: Optional[float] = Field(None, description="Height in cm")


class SpO2Response(BaseModel):
    """Schema for oxygen saturation response."""
    oxygen_saturation: float = Field(..., description="Oxygen saturation percentage")
    status: str = Field(..., description="SpO2 status (e.g., normal, low, critical)")
    timestamp: datetime = Field(..., description="Timestamp when measurement was taken")


class TemperatureResponse(BaseModel):
    """Schema for temperature response."""
    temperature_f: float = Field(..., description="Temperature in Fahrenheit")
    temperature_c: float = Field(..., description="Temperature in Celsius")
    status: str = Field(..., description="Temperature status (e.g., normal, fever, hypothermia)")
    timestamp: datetime = Field(..., description="Timestamp when measurement was taken")


class BloodSugarResponse(BaseModel):
    """Schema for blood sugar response."""
    glucose_level: float = Field(..., description="Blood glucose level in mg/dL")
    trend: str = Field(..., description="Blood sugar trend (stable, spike, drop)")
    timestamp: datetime = Field(..., description="Timestamp when measurement was taken")
    measurement_type: Optional[str] = Field(None, description="Type of measurement (fasting, random, post-meal)")


class RecoveryDataPoint(BaseModel):
    """Schema for a single recovery data point."""
    date: datetime = Field(..., description="Date of recovery measurement")
    recovery_score: float = Field(..., description="Recovery score (0-100 scale)")
    notes: Optional[str] = Field(None, description="Additional notes about recovery")
    recovery_type: Optional[str] = Field(None, description="Type of recovery (post-surgery, injury, illness)")


class RecoveryTrackerResponse(BaseModel):
    """Schema for recovery tracker response with timeseries data."""
    patient_id: str = Field(..., description="Patient ID")
    recovery_data: List[RecoveryDataPoint] = Field(..., description="List of recovery data points over time")
    latest_score: Optional[float] = Field(None, description="Latest recovery score")
    trend: Optional[str] = Field(None, description="Overall recovery trend")


class DashboardErrorResponse(BaseModel):
    """Schema for dashboard error responses."""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: datetime = Field(..., description="Timestamp when error occurred")


class PatientNotFoundResponse(BaseModel):
    """Schema for patient not found responses."""
    error: str = Field(..., description="Patient not found error message")
    patient_id: str = Field(..., description="Patient ID that was not found")
    timestamp: datetime = Field(..., description="Timestamp when error occurred")


# Mock data response schemas (when no real data exists)
class MockHeartRateResponse(BaseModel):
    """Schema for mock heart rate response."""
    heart_rate: int = Field(..., description="Mock heart rate in beats per minute")
    status: str = Field(..., description="Mock heart rate status")
    timestamp: datetime = Field(..., description="Mock timestamp")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")


class MockBloodPressureResponse(BaseModel):
    """Schema for mock blood pressure response."""
    systolic: int = Field(..., description="Mock systolic blood pressure")
    diastolic: int = Field(..., description="Mock diastolic blood pressure")
    status: str = Field(..., description="Mock blood pressure status")
    timestamp: datetime = Field(..., description="Mock timestamp")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")


class MockBMIResponse(BaseModel):
    """Schema for mock BMI response."""
    bmi_value: float = Field(..., description="Mock BMI value")
    trend: str = Field(..., description="Mock BMI trend")
    timestamp: datetime = Field(..., description="Mock timestamp")
    weight: Optional[float] = Field(None, description="Mock weight in kg")
    height: Optional[float] = Field(None, description="Mock height in cm")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")


class MockSpO2Response(BaseModel):
    """Schema for mock oxygen saturation response."""
    oxygen_saturation: float = Field(..., description="Mock oxygen saturation percentage")
    status: str = Field(..., description="Mock SpO2 status")
    timestamp: datetime = Field(..., description="Mock timestamp")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")


class MockTemperatureResponse(BaseModel):
    """Schema for mock temperature response."""
    temperature_f: float = Field(..., description="Mock temperature in Fahrenheit")
    temperature_c: float = Field(..., description="Mock temperature in Celsius")
    status: str = Field(..., description="Mock temperature status")
    timestamp: datetime = Field(..., description="Mock timestamp")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")


class MockBloodSugarResponse(BaseModel):
    """Schema for mock blood sugar response."""
    glucose_level: float = Field(..., description="Mock blood glucose level in mg/dL")
    trend: str = Field(..., description="Mock blood sugar trend")
    timestamp: datetime = Field(..., description="Mock timestamp")
    measurement_type: Optional[str] = Field(None, description="Mock measurement type")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")


class MockRecoveryTrackerResponse(BaseModel):
    """Schema for mock recovery tracker response."""
    patient_id: str = Field(..., description="Patient ID")
    recovery_data: List[RecoveryDataPoint] = Field(..., description="Mock recovery data points")
    latest_score: Optional[float] = Field(None, description="Mock latest recovery score")
    trend: Optional[str] = Field(None, description="Mock recovery trend")
    is_mock_data: bool = Field(True, description="Indicates this is mock data")