# DualWell: REST API Documentation

Base URL: `http://localhost:8000/api`  
Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`  
Interactive ReDoc: `http://localhost:8000/redoc`

---

## 1. Authentication & Student Profile (`/auth`)

### `POST /api/auth/register`
- **Description:** Registers a new student account. Automatically creates default `StudentProfile` and `PrivacyPreference`.
- **Request Body:**
  ```json
  {
    "email": "student@university.edu",
    "password": "Password123!",
    "full_name": "Jordan Lee"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "student@university.edu",
      "full_name": "Jordan Lee",
      "is_active": true
    }
  }
  ```

### `POST /api/auth/login`
- **Description:** Verifies student credentials and returns a signed JWT access token.
- **Request Body:**
  ```json
  {
    "email": "student@university.edu",
    "password": "Password123!"
  }
  ```

### `GET /api/auth/me`
- **Description:** Returns the currently authenticated user's account details.
- **Headers:** `Authorization: Bearer <TOKEN>`

### `GET /api/auth/profile` / `PUT /api/auth/profile`
- **Description:** Retrieves or updates student profile targets (major, sport, sleep hours, bedtime, wake time, hydration goal).

---

## 2. Wearable Telemetry & Providers (`/wearable`)

### `GET /api/wearable/status`
- **Description:** Current connection status, active provider, last sync timestamp, and telemetry summary.

### `GET /api/wearable/providers`
- **Description:** Supported provider specifications (Demo Simulator, Apple HealthKit, Wear OS Health Connect, Fitbit).

### `POST /api/wearable/sync`
- **Description:** Triggers synchronization from provider. Automatically deduplicates observations and recalculates risk.
- **Request Body:** `{"provider": "demo"}`

### `GET /api/wearable/observations`
- **Query Parameters:** `metric_type` (`heart_rate`, `hrv`, `steps`, `resting_hr`, `sleep_duration`, `recovery_score`), `limit` (default 50).
- **Provenance Tags:** Each observation contains `data_source` (`WEARABLE_LIVE`, `SIMULATED_DEMO`, `MANUAL_ENTRY`).

---

## 3. Academic Calendar & Timetable (`/academic`)

### `GET /api/academic/events` / `POST /api/academic/events`
- **Description:** Lists or creates academic events (`exam`, `deadline`, `assignment`, `class`, `study_session`).
- **Fields:** `title`, `event_type`, `course_name`, `start_time`, `end_time`, `priority`, `estimated_workload_hours`, `is_fixed`, `is_completed`.

### `PUT /api/academic/events/{id}` / `DELETE /api/academic/events/{id}`
- **Description:** Modifies or deletes an academic event.

### `GET /api/academic/conflicts`
- **Description:** Detects overlaps between coursework and workouts, and flags high-intensity training preceding exams.

### `GET /api/academic/export-ics`
- **Description:** Exports the student's schedule as a standard RFC 5545 `.ics` file.

---

## 4. Athletic Training Sessions (`/training`)

### `GET /api/training/sessions` / `POST /api/training/sessions`
- **Description:** Lists or logs workouts.
- **Fields:** `title`, `activity_type` (running, rowing, strength, hiit, etc.), `start_time`, `end_time`, `duration_minutes`, `intensity`, `avg_heart_rate`, `is_flexible`.

---

## 5. Dual-Load & Risk Prediction Engine (`/load-risk`)

### `GET /api/load-risk/current`
- **Description:** Calculates real-time Academic Load ($0\text{--}100$), Athletic Load ($0\text{--}100$), Recovery Score ($0\text{--}100$), and Dual-Load Risk Score ($0\text{--}100$), along with risk tier (`GREEN`, `YELLOW`, `RED`) and transparent factor explanations.

### `POST /api/load-risk/recalculate`
- **Description:** Forces an immediate re-evaluation of physiological load and persists a `DailyLoadSnapshot`.

### `GET /api/load-risk/history`
- **Description:** Chronological historical snapshots for the trailing 7 days.

---

## 6. Smart Dynamic Scheduler (`/scheduler`)

### `GET /api/scheduler/recommendations`
- **Description:** Returns pending schedule adjustments generated to resolve timetable clashes and sleep window conflicts.

### `POST /api/scheduler/apply/{id}`
- **Description:** Applies proposed schedule adjustment upon student confirmation.

### `POST /api/scheduler/reject/{id}`
- **Description:** Dismisses proposed schedule adjustment.

---

## 7. Lifestyle: Nutrition, Hydration & Sleep (`/lifestyle`)

### `GET /api/lifestyle/meals` / `POST /api/lifestyle/meals`
- **Description:** Retrieves or logs meals with macronutrients.

### `GET /api/lifestyle/hydration` / `POST /api/lifestyle/hydration` / `POST /api/lifestyle/hydration/quick-add`
- **Description:** Logs water consumption in mL; quick-add endpoint adds default 250 mL and returns updated daily percentage.

### `GET /api/lifestyle/sleep` / `POST /api/lifestyle/sleep`
- **Description:** Retrieves or records sleep duration and stage architecture (Deep, REM, Light).

### `GET /api/lifestyle/sleep-plan`
- **Description:** Returns personalized wind-down and bedtime recommendations based on tomorrow's academic and training commitments.

### `POST /api/lifestyle/recovery-checkin`
- **Description:** Logs daily subjective fatigue self-check (muscle soreness, mental fatigue, pain warning flag).

---

## 8. Smart Reminders & In-App Alarms (`/notifications`)

### `GET /api/notifications/reminders`
- **Description:** Returns in-app reminders; respects quiet hours window.

### `POST /api/notifications/reminders/{id}/read`
- **Description:** Marks a reminder as read.

### `POST /api/notifications/reminders/{id}/dismiss`
- **Description:** Dismisses a reminder.

---

## 9. Priority Rescue Mode (`/rescue`)

### `GET /api/rescue/plan` / `POST /api/rescue/regenerate`
- **Description:** Synthesizes an immediate cognitive triage action list: DO NOW (35-min sprint), DO NEXT, POSTPONE, training modulation, and hydration directives.

---

## 10. Weekly Insights & Privacy (`/insights`, `/privacy`)

### `GET /api/insights/weekly`
- **Description:** 7-day multi-factorial analytics across academic hours, training volume, sleep consistency, and risk distribution.

### `GET /api/privacy/export-data`
- **Description:** Downloads complete personal data archive as structured JSON.

### `DELETE /api/privacy/delete-account`
- **Description:** Permanently purges student account and all linked records.
