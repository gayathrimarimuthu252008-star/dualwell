# DualWell: Smartwatch Hardware & Companion Integration Guide

This guide details the technical requirements, permissions, and architectural steps required to synchronize real smartwatch hardware with DualWell.

---

## 1. Fundamental Integration Architecture

Web browsers operate inside security sandboxes and **cannot open raw Bluetooth LE or USB sockets** to arbitrary smartwatches directly. Smartwatch manufacturers therefore support two genuine integration pathways:

1. **Cloud-to-Cloud OAuth 2.0 Web APIs** (e.g., Fitbit, Garmin Connect, Oura, Whoop).
2. **Mobile Health Aggregator Ingestion Bridges** (Apple HealthKit on iOS, Google Health Connect on Android / Wear OS).

DualWell supports both paradigms through its modular `BaseWearableProvider` architecture.

---

## 2. Connecting Real Wearable Ecosystems

### 2.1. Apple Watch & Apple HealthKit (iOS)
- **Required Hardware:** Apple Watch Series 4+ paired with iPhone running iOS 15+.
- **Mechanism:** HealthKit is strictly restricted to on-device Swift/Objective-C frameworks (`HealthKit.framework`).
- **Authorization Flow:**
  1. The student installs the DualWell iOS companion app.
  2. The app requests user authorization for the following HealthKit sample types:
     - `HKQuantityTypeIdentifierHeartRate` (BPM)
     - `HKQuantityTypeIdentifierHeartRateVariabilitySDNN` (HRV ms)
     - `HKQuantityTypeIdentifierStepCount` (Daily steps)
     - `HKCategoryTypeIdentifierSleepAnalysis` (Sleep intervals)
  3. The iOS companion app sets up an `HKObserverQuery` with background delivery enabled.
  4. Upon new background observations, the app sends an authenticated batch POST to DualWell:
     ```http
     POST /api/wearable/observations
     Authorization: Bearer <STUDENT_JWT_TOKEN>
     Content-Type: application/json

     {
       "metric_type": "heart_rate",
       "value": 72.0,
       "unit": "bpm",
       "recorded_at": "2026-10-15T18:30:00Z",
       "data_source": "WEARABLE_LIVE",
       "extra_metadata": "Apple Watch Series 9 HealthKit sync"
     }
     ```
  5. DualWell validates timestamps, prevents duplicate ingestion, and triggers load recalculation.

---

### 2.2. Wear OS (Samsung Galaxy Watch, Google Pixel Watch) & Health Connect
- **Required Hardware:** Wear OS 3+ smartwatch paired with Android device running Android 9+ (Android 14+ has Health Connect built into system settings).
- **Mechanism:** Android Jetpack `androidx.health.connect.client.HealthConnectClient`.
- **Authorization Flow:**
  1. Student grants permissions in the Android Permission Manager dialog:
     - `android.permission.health.READ_HEART_RATE`
     - `android.permission.health.READ_STEPS`
     - `android.permission.health.READ_SLEEP`
  2. DualWell Android companion invokes `WorkManager` periodic background synchronization (every 15–30 minutes).
  3. Pushes telemetry to `/api/wearable/observations` with `data_source: "WEARABLE_LIVE"`.

---

### 2.3. Fitbit Cloud Web API
- **Required Hardware:** Fitbit Sense, Versa, Charge, or Inspire series.
- **Mechanism:** Official Fitbit Web API (OAuth 2.0 Authorization Code flow).
- **Setup Steps:**
  1. Navigate to [Fitbit Developer Portal](https://dev.fitbit.com/apps) and register an application:
     - **OAuth 2.0 Application Type:** Personal or Server
     - **Callback URL:** `http://localhost:8000/api/wearable/fitbit/callback`
     - **Default Access Type:** Read-Only
  2. Copy your **Client ID** and **Client Secret**.
  3. Add them to your `backend/.env` file:
     ```env
     FITBIT_CLIENT_ID=your_fitbit_client_id_here
     FITBIT_CLIENT_SECRET=your_fitbit_client_secret_here
     ```
  4. In the DualWell web application, navigate to **Wearable Monitoring** and click **Connect Fitbit Cloud Web API**.
  5. The student is redirected to Fitbit's official consent portal to authorize access to `activity`, `heartrate`, and `sleep`.
  6. Upon callback, DualWell securely stores the access token and polls telemetry in the background.

---

## 3. Data Provenance & Integrity Standards

To preserve scientific and ethical transparency, DualWell permanently tags all physiological observations:
- `WEARABLE_LIVE`: Authenticated, verified real-time device telemetry.
- `SIMULATED_DEMO`: High-fidelity student-athlete simulation used when hardware or credentials are not yet connected.
- `MANUAL_ENTRY`: Student self-reported logs.

DualWell's database schema enforces a unique constraint on `(user_id, metric_type, recorded_at, data_source)` to prevent duplicate observations from skewing load estimates.
