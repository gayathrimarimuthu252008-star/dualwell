from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseWearableProvider(ABC):
    """
    Abstract interface for wearable device providers in DualWell.
    Ensures modular, vendor-agnostic integration across:
    - Smartwatch live telemetry (Apple Watch, Wear OS, Garmin, Fitbit)
    - Simulated realistic demo streams
    - Mobile health aggregators (HealthKit, Health Connect)
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier (e.g., 'demo', 'fitbit', 'apple_health', 'health_connect')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider label."""
        pass

    @abstractmethod
    def get_auth_url(self, user_id: int, redirect_uri: str) -> Optional[str]:
        """Returns OAuth2 authorization URL or instructions where applicable."""
        pass

    @abstractmethod
    def sync_data(self, user_id: int, auth_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Synchronizes wearable observations.
        Returns standardized observation dictionaries:
        {
            'metric_type': 'heart_rate' | 'hrv' | 'steps' | 'resting_hr' | 'sleep_duration' | 'recovery_score',
            'value': float,
            'unit': str,
            'recorded_at': datetime,
            'data_source': 'WEARABLE_LIVE' | 'SIMULATED_DEMO',
            'extra_metadata': str (JSON or description)
        }
        """
        pass

    @abstractmethod
    def get_supported_metrics(self) -> List[str]:
        """Returns list of metrics supported by this provider."""
        pass

    @abstractmethod
    def get_technical_requirements(self) -> Dict[str, Any]:
        """
        Explains genuine platform requirements, authorization scopes, native bridges,
        or hardware prerequisites for real device syncing.
        """
        pass
