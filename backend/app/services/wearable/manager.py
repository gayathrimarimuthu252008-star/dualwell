from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.services.wearable.base import BaseWearableProvider
from app.services.wearable.demo_provider import DemoWearableProvider
from app.services.wearable.real_providers import FitbitWearableProvider, AppleHealthWearableProvider, HealthConnectWearableProvider
from app.models.wearable import WearableConnection, WearableObservation
from app.services.risk_prediction import risk_predictor

class WearableManager:
    """
    Central coordinator for wearable devices, synchronizations,
    and duplicate observation prevention.
    """

    def __init__(self):
        self._providers: Dict[str, BaseWearableProvider] = {}
        # Register default supported providers
        self.register_provider(DemoWearableProvider())
        self.register_provider(FitbitWearableProvider())
        self.register_provider(AppleHealthWearableProvider())
        self.register_provider(HealthConnectWearableProvider())

    def register_provider(self, provider: BaseWearableProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[BaseWearableProvider]:
        return self._providers.get(provider_id)

    def list_available_providers(self) -> List[Dict[str, Any]]:
        results = []
        for pid, provider in self._providers.items():
            results.append({
                "provider_id": pid,
                "display_name": provider.display_name,
                "supported_metrics": provider.get_supported_metrics(),
                "technical_details": provider.get_technical_requirements()
            })
        return results

    def sync_provider(self, db: Session, user_id: int, provider_id: str) -> Dict[str, Any]:
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider '{provider_id}' is not recognized.")

        conn = db.query(WearableConnection).filter(
            WearableConnection.user_id == user_id,
            WearableConnection.provider == provider_id
        ).first()

        if not conn:
            conn = WearableConnection(
                user_id=user_id,
                provider=provider_id,
                display_name=provider.display_name,
                is_connected=True,
                sync_status="syncing"
            )
            db.add(conn)
            db.commit()
            db.refresh(conn)
        else:
            conn.sync_status = "syncing"
            conn.is_connected = True
            db.commit()

        try:
            records = provider.sync_data(user_id=user_id)
            inserted_count = 0
            duplicates_skipped = 0

            for rec in records:
                existing = db.query(WearableObservation).filter(
                    WearableObservation.user_id == user_id,
                    WearableObservation.metric_type == rec["metric_type"],
                    WearableObservation.recorded_at == rec["recorded_at"],
                    WearableObservation.data_source == rec["data_source"]
                ).first()

                if existing:
                    # Update value and metadata to avoid duplicates
                    existing.value = rec["value"]
                    existing.unit = rec["unit"]
                    existing.extra_metadata = rec.get("extra_metadata")
                    duplicates_skipped += 1
                else:
                    obs = WearableObservation(
                        user_id=user_id,
                        provider=provider_id,
                        metric_type=rec["metric_type"],
                        value=rec["value"],
                        unit=rec["unit"],
                        recorded_at=rec["recorded_at"],
                        data_source=rec["data_source"],
                        extra_metadata=rec.get("extra_metadata")
                    )
                    db.add(obs)
                    inserted_count += 1

            conn.last_synced_at = datetime.utcnow()
            conn.sync_status = "success"
            conn.error_message = None
            db.commit()

            # Recalculate risk automatically upon receiving fresh telemetry (NFR2)
            risk_predictor.predict_risk(db, user_id)

            return {
                "provider": provider_id,
                "status": "success",
                "observations_ingested": inserted_count,
                "duplicates_prevented": duplicates_skipped,
                "synced_at": conn.last_synced_at
            }

        except Exception as e:
            conn.sync_status = "error"
            conn.error_message = str(e)
            db.commit()
            raise e

wearable_manager = WearableManager()
