"""Patient dashboard data models for MongoDB operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId


class Patient:
    """Patient model for MongoDB operations."""
    
    def __init__(
        self,
        patient_id: str,
        first_name: str,
        last_name: str,
        date_of_birth: datetime,
        gender: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Patient":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["date_of_birth"],
            gender=data["gender"],
            email=data.get("email"),
            phone=data.get("phone"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class HeartRate:
    """Heart rate vital signs model."""
    
    def __init__(
        self,
        patient_id: str,
        heart_rate: int,
        status: str,  # e.g., "resting", "active", "elevated"
        timestamp: datetime,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.heart_rate = heart_rate
        self.status = status
        self.timestamp = timestamp
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "heart_rate": self.heart_rate,
            "status": self.status,
            "timestamp": self.timestamp,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HeartRate":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            heart_rate=data["heart_rate"],
            status=data["status"],
            timestamp=data["timestamp"],
            created_at=data.get("created_at")
        )


class BloodPressure:
    """Blood pressure vital signs model."""
    
    def __init__(
        self,
        patient_id: str,
        systolic: int,
        diastolic: int,
        status: str,  # e.g., "normal", "elevated", "high"
        timestamp: datetime,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.systolic = systolic
        self.diastolic = diastolic
        self.status = status
        self.timestamp = timestamp
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "systolic": self.systolic,
            "diastolic": self.diastolic,
            "status": self.status,
            "timestamp": self.timestamp,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BloodPressure":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            systolic=data["systolic"],
            diastolic=data["diastolic"],
            status=data["status"],
            timestamp=data["timestamp"],
            created_at=data.get("created_at")
        )


class BMI:
    """BMI measurement model."""
    
    def __init__(
        self,
        patient_id: str,
        bmi_value: float,
        trend: str,  # e.g., "increase", "decrease", "stable"
        timestamp: datetime,
        weight: Optional[float] = None,
        height: Optional[float] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.bmi_value = bmi_value
        self.trend = trend
        self.timestamp = timestamp
        self.weight = weight
        self.height = height
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "bmi_value": self.bmi_value,
            "trend": self.trend,
            "timestamp": self.timestamp,
            "weight": self.weight,
            "height": self.height,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BMI":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            bmi_value=data["bmi_value"],
            trend=data["trend"],
            timestamp=data["timestamp"],
            weight=data.get("weight"),
            height=data.get("height"),
            created_at=data.get("created_at")
        )


class SpO2:
    """Oxygen saturation model."""
    
    def __init__(
        self,
        patient_id: str,
        oxygen_saturation: float,
        status: str,  # e.g., "normal", "low", "critical"
        timestamp: datetime,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.oxygen_saturation = oxygen_saturation
        self.status = status
        self.timestamp = timestamp
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "oxygen_saturation": self.oxygen_saturation,
            "status": self.status,
            "timestamp": self.timestamp,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpO2":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            oxygen_saturation=data["oxygen_saturation"],
            status=data["status"],
            timestamp=data["timestamp"],
            created_at=data.get("created_at")
        )


class Temperature:
    """Temperature measurement model."""
    
    def __init__(
        self,
        patient_id: str,
        temperature_f: float,
        temperature_c: float,
        status: str,  # e.g., "normal", "fever", "hypothermia"
        timestamp: datetime,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.temperature_f = temperature_f
        self.temperature_c = temperature_c
        self.status = status
        self.timestamp = timestamp
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "temperature_f": self.temperature_f,
            "temperature_c": self.temperature_c,
            "status": self.status,
            "timestamp": self.timestamp,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Temperature":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            temperature_f=data["temperature_f"],
            temperature_c=data["temperature_c"],
            status=data["status"],
            timestamp=data["timestamp"],
            created_at=data.get("created_at")
        )


class BloodSugar:
    """Blood sugar/glucose level model."""
    
    def __init__(
        self,
        patient_id: str,
        glucose_level: float,
        trend: str,  # e.g., "stable", "spike", "drop"
        timestamp: datetime,
        measurement_type: Optional[str] = None,  # e.g., "fasting", "random", "post-meal"
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.glucose_level = glucose_level
        self.trend = trend
        self.timestamp = timestamp
        self.measurement_type = measurement_type
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "glucose_level": self.glucose_level,
            "trend": self.trend,
            "timestamp": self.timestamp,
            "measurement_type": self.measurement_type,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BloodSugar":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            glucose_level=data["glucose_level"],
            trend=data["trend"],
            timestamp=data["timestamp"],
            measurement_type=data.get("measurement_type"),
            created_at=data.get("created_at")
        )


class RecoveryTracker:
    """Recovery progress tracking model."""
    
    def __init__(
        self,
        patient_id: str,
        recovery_score: float,  # 0-100 scale
        date: datetime,
        notes: Optional[str] = None,
        recovery_type: Optional[str] = None,  # e.g., "post-surgery", "injury", "illness"
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id
        self.patient_id = patient_id
        self.recovery_score = recovery_score
        self.date = date
        self.notes = notes
        self.recovery_type = recovery_type
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "patient_id": self.patient_id,
            "recovery_score": self.recovery_score,
            "date": self.date,
            "notes": self.notes,
            "recovery_type": self.recovery_type,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecoveryTracker":
        """Create model instance from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            patient_id=data["patient_id"],
            recovery_score=data["recovery_score"],
            date=data["date"],
            notes=data.get("notes"),
            recovery_type=data.get("recovery_type"),
            created_at=data.get("created_at")
        )
