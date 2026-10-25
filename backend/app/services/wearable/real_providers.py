from typing import Dict, Any, List, Optional
from app.services.wearable.base import BaseWearableProvider
from app.config import settings

class FitbitWearableProvider(BaseWearableProvider):
    """
    Fitbit Web API Adapter (OAuth 2.0 PKCE / Authorization Code Flow).
    Connects to official Fitbit Cloud Web API.
    """

    @property
    def provider_id(self) -> str:
        return "fitbit"

    @property
    def display_name(self) -> str:
        return "Fitbit Cloud Web API"

    @property
    def availability(self) -> str:
        # The OAuth2 authorization-code flow is not implemented yet; the
        # provider is announced in the UI but cannot be connected.
        return "coming_soon"

    def get_auth_url(self, user_id: int, redirect_uri: str) -> Optional[str]:
        if not settings.FITBIT_CLIENT_ID:
            return None
        
        scopes = "activity heartrate sleep profile"
        auth_url = (
            f"https://www.fitbit.com/oauth2/authorize"
            f"?response_type=code"
            f"&client_id={settings.FITBIT_CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes.replace(' ', '%20')}"
            f"&state={user_id}"
        )
        return auth_url

    def sync_data(self, user_id: int, auth_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # When genuine access token is stored in auth_data, this calls api.fitbit.com
        # If credentials are not configured, raises informative exception or returns empty
        if not auth_data or not auth_data.get("access_token"):
            raise ValueError(
                "Fitbit credentials not configured. Please set FITBIT_CLIENT_ID and "
                "complete OAuth2 authorization in Settings."
            )
        
        # Real integration queries:
        # GET https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json
        # GET https://api.fitbit.com/1/user/-/sleep/date/today.json
        return []

    def get_supported_metrics(self) -> List[str]:
        return ["heart_rate", "resting_hr", "hrv", "steps", "sleep_duration"]

    def get_technical_requirements(self) -> Dict[str, Any]:
        return {
            "type": "Cloud OAuth2 REST API",
            "requirements": "Requires developer registration at https://dev.fitbit.com/apps",
            "authorization": "User web authorization with OAuth2 access and refresh tokens",
            "platform": "Cloud-to-Cloud backend connection",
            "setup_steps": [
                "1. Register app at https://dev.fitbit.com (Application Type: Personal or Server)",
                "2. Set Callback URL to http://localhost:8000/api/wearable/fitbit/callback",
                "3. Set FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET in backend/.env",
                "4. Click 'Connect Fitbit' in Wearable Monitoring to initiate OAuth flow."
            ]
        }


class AppleHealthWearableProvider(BaseWearableProvider):
    """
    Apple Health / Apple Watch (HealthKit) Integration Adapter.
    Architectural reality: A browser sandbox cannot communicate directly with Apple HealthKit.
    DualWell provides an authenticated REST ingestion bridge for the DualWell iOS companion app.
    """

    @property
    def provider_id(self) -> str:
        return "apple_health"

    @property
    def display_name(self) -> str:
        return "Apple Watch / Apple HealthKit"

    def get_auth_url(self, user_id: int, redirect_uri: str) -> Optional[str]:
        return None  # Native iOS authorization modal in Swift app

    def sync_data(self, user_id: int, auth_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    def get_supported_metrics(self) -> List[str]:
        return ["heart_rate", "hrv", "resting_hr", "steps", "sleep_duration", "active_minutes"]

    def get_technical_requirements(self) -> Dict[str, Any]:
        return {
            "type": "Native iOS HealthKit Bridge",
            "requirements": "iOS device (iPhone) running iOS 15+ paired with Apple Watch Series 4+",
            "authorization": "HealthKit explicit on-device permissions (HKQuantityTypeIdentifierHeartRate, etc.)",
            "platform": "Native iOS App -> DualWell Secure Ingestion API",
            "setup_steps": [
                "1. Build iOS companion target with HealthKit capability enabled in Xcode.",
                "2. User grants permission in Apple Health prompt for HR, HRV, Steps, and Sleep.",
                "3. Background observer query automatically POSTs telemetry batches to /api/wearable/observations.",
                "4. All synced records are marked with data_source='WEARABLE_LIVE'."
            ]
        }


class HealthConnectWearableProvider(BaseWearableProvider):
    """
    Wear OS / Android Health Connect Adapter.
    Supports Samsung Galaxy Watch, Pixel Watch, and Wear OS 3+ devices via Google Health Connect.
    """

    @property
    def provider_id(self) -> str:
        return "health_connect"

    @property
    def display_name(self) -> str:
        return "Wear OS (Google Health Connect)"

    def get_auth_url(self, user_id: int, redirect_uri: str) -> Optional[str]:
        return None  # Android Permission Manager dialog

    def sync_data(self, user_id: int, auth_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    def get_supported_metrics(self) -> List[str]:
        return ["heart_rate", "resting_hr", "steps", "sleep_duration", "active_minutes"]

    def get_technical_requirements(self) -> Dict[str, Any]:
        return {
            "type": "Android Jetpack Health Connect API",
            "requirements": "Android 14+ (or Android 9+ with Health Connect app) + Wear OS smartwatch",
            "authorization": "Android runtime permissions for androidx.health.connect.client",
            "platform": "Android Mobile Companion -> DualWell REST API",
            "setup_steps": [
                "1. User installs DualWell companion on Android phone.",
                "2. App requests HealthConnectClient permissions.",
                "3. Periodic WorkManager sync pushes aggregated records to /api/wearable/observations.",
                "4. Records persist with data_source='WEARABLE_LIVE'."
            ]
        }
