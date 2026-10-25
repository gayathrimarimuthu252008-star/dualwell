from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional
from app.services.wearable.base import BaseWearableProvider

class DemoWearableProvider(BaseWearableProvider):
    """
    High-fidelity simulated wearable provider.
    Models physiological responses of a collegiate student-athlete.
    All outputs are explicitly labeled as SIMULATED_DEMO.
    """

    @property
    def provider_id(self) -> str:
        return "demo"

    @property
    def display_name(self) -> str:
        return "DualWell Athlete Simulator (Demo Engine)"

    def get_auth_url(self, user_id: int, redirect_uri: str) -> Optional[str]:
        return None

    def sync_data(self, user_id: int, auth_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Stable per-day anchors: every sync on the same UTC calendar day emits
        # identical recorded_at values, so the uq_user_observation unique
        # constraint (user_id, metric_type, recorded_at, data_source) matches
        # re-syncs as duplicates instead of inserting a fresh set per sync.
        anchor_day = datetime.utcnow().date()

        def slot(hour: int, minute: int = 0, days_ago: int = 0) -> datetime:
            return datetime.combine(anchor_day - timedelta(days=days_ago), time(hour, minute))

        records: List[Dict[str, Any]] = []

        # 1. Heart rate samples across the stable morning window
        for t in [slot(4, 0), slot(4, 30), slot(5, 0), slot(5, 30), slot(5, 45), slot(6, 0)]:
            hr_val = 68.0
            records.append({
                "metric_type": "heart_rate",
                "value": hr_val,
                "unit": "bpm",
                "recorded_at": t,
                "data_source": "SIMULATED_DEMO",
                "extra_metadata": "Sampled during light academic study"
            })

        # 2. HRV (rMSSD in ms)
        records.append({
            "metric_type": "hrv",
            "value": 62.5,
            "unit": "ms",
            "recorded_at": slot(3, 0),
            "data_source": "SIMULATED_DEMO",
            "extra_metadata": "Nighttime rMSSD baseline calculation"
        })

        # 3. Resting Heart Rate
        records.append({
            "metric_type": "resting_hr",
            "value": 54.0,
            "unit": "bpm",
            "recorded_at": slot(2, 0),
            "data_source": "SIMULATED_DEMO",
            "extra_metadata": "Overnight lowest 10-minute average"
        })

        # 4. Daily steps cumulative
        records.append({
            "metric_type": "steps",
            "value": 9650.0,
            "unit": "count",
            "recorded_at": slot(6, 0),
            "data_source": "SIMULATED_DEMO",
            "extra_metadata": "Campus walking + warm-up activity"
        })

        # 5. Sleep duration (recorded at last night's wind-down time)
        records.append({
            "metric_type": "sleep_duration",
            "value": 7.6,
            "unit": "hours",
            "recorded_at": slot(23, 0, days_ago=1),
            "data_source": "SIMULATED_DEMO",
            "extra_metadata": "Deep: 1.8h, REM: 1.9h, Light: 3.8h"
        })

        # 6. Readiness / Recovery Score
        records.append({
            "metric_type": "recovery_score",
            "value": 82.0,
            "unit": "score",
            "recorded_at": slot(3, 0),
            "data_source": "SIMULATED_DEMO",
            "extra_metadata": "Synthesized readiness based on autonomic recovery"
        })

        return records

    def get_supported_metrics(self) -> List[str]:
        return ["heart_rate", "hrv", "steps", "resting_hr", "sleep_duration", "recovery_score"]

    def get_technical_requirements(self) -> Dict[str, Any]:
        return {
            "type": "Local Virtual Simulator",
            "requirements": "Zero external dependencies or hardware required.",
            "authorization": "Granted instantly in local development mode.",
            "platform": "Cross-platform (Runs everywhere)."
        }
