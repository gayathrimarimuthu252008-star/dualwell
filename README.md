# DualWell: Smart Student Wellness and Academic Performance System

DualWell is an intelligent, full-stack, locally runnable web application engineered for collegiate student-athletes and active scholars. It harmonizes smartwatch physiological telemetry with academic course commitments to identify acute cognitive overload, protect restorative sleep, and deliver actionable schedule and recovery interventions.

---

## 1. Quick Start (Windows)

### Prerequisites
- **Python 3.10+** (tested on Python 3.13)
- **Node.js 18+** (tested on Node v24)
- **npm** (tested on npm 11+)

### One-Click Launch
Double-click `start.bat` or run in PowerShell:
```powershell
.\start.bat
```
`start.bat` automatically:
1. Validates Python and Node.js prerequisites.
2. Creates the Python virtual environment (`backend/venv`) and installs dependencies.
3. Initializes the SQLite database (`backend/dualwell.db`) and seeds demonstration data.
4. Installs frontend npm dependencies if missing.
5. Launches the FastAPI backend at **http://localhost:8000**.
6. Launches the Vite React frontend at **http://localhost:5173**.

### Service URLs
- **Frontend Web Application:** [http://localhost:5173](http://localhost:5173)
- **Backend REST API:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Redoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Stopping Services
Double-click `stop.bat` or run:
```powershell
.\stop.bat
```

### Database Migrations (Alembic)
Schema changes are versioned with Alembic in `backend/migrations/`. The
initial revision (`59aeca45b084`) creates all 15 application tables and
matches `app/models` exactly on both SQLite and PostgreSQL.
```powershell
python manage.py migrate          # alembic upgrade head (SQLite dev DB by default)
python manage.py migrate --to base  # roll back to an empty schema
```
Advanced flows (run from `backend/`):
```powershell
.\venv\Scripts\python -m alembic revision --autogenerate -m "describe change"
.\venv\Scripts\python -m alembic check     # fails if models drifted from the schema
.\venv\Scripts\python -m alembic stamp head  # claim an existing create_all DB
```
The URL always comes from `DATABASE_URL` via `app.config`, so the same
commands target PostgreSQL simply by pointing it there:
```powershell
$env:DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/dualwell"
python manage.py migrate
```

---

## 2. Demonstration Student Account

DualWell includes a pre-seeded student-athlete persona:
- **Student:** Alex Morgan
- **Major:** Computer Science & Bioengineering
- **Sport:** Collegiate Rowing / Middle-Distance Running
- **Email:** `alex.morgan@dualwell.edu`
- **Password:** `DualWell2026!`

> **Tip:** On the login page, you can click the **"One-Click Login as Alex Morgan"** button to log in instantly without typing.

---

## 3. Technology Stack

### Frontend
- **Framework:** React 19 with Vite & TypeScript
- **Styling:** Tailwind CSS with custom light-theme palette
- **Data Visualization:** Recharts
- **Iconography:** Lucide React
- **HTTP Client:** Axios interceptors: auto-refreshing 15-minute JWT access tokens + Bearer auth

### Backend
- **Framework:** Python FastAPI
- **Validation:** Pydantic v2
- **ORM & Database:** SQLAlchemy with persistent SQLite (`dualwell.db`), architected for easy migration to PostgreSQL
- **Migrations:** Alembic (initial revision matches all 15 models; `DATABASE_URL` selects SQLite or PostgreSQL)
- **Security:** 15-minute PyJWT access tokens with a 30-day refresh flow (`POST /api/auth/refresh`), failed-login rate limiting (5 attempts / 5 min → 429 with `Retry-After`), 12-character password minimum, password-confirmed account deletion (HTTP 429/422/403 hardening), salted Bcrypt hashing, and startup refusal of placeholder `SECRET_KEY` outside development
- **Testing:** Pytest & HTTPX test client

---

## 4. UI Design & Palette

DualWell adheres strictly to the required student-friendly light theme:
- **Main Background:** `#F7F8FC`
- **Card Background:** `#FFFFFF`
- **Primary Blue:** `#4F7DF3`
- **Soft Blue Accent:** `#EAF0FF`
- **Mint Green (Optimal Recovery):** `#DDF7E8` / `#239B68`
- **Warm Cream (Elevated Load):** `#FFF4DF` / `#E6A23C`
- **Coral Red (Overload Triage):** `#E05252`
- **Primary Text:** `#263247`
- **Secondary Text:** `#748096`
- **Borders:** `#E5E9F2`

---

## 5. Navigation & Implemented Modules

1. **Dashboard:** Real-time dual-load risk score, Academic Load (0-100), Athletic Load (0-100), Recovery Readiness (0-100), 7-day trend chart, today's schedule timeline, hydration quick tracker, and priority triage trigger.
2. **Wearable Monitoring:** Smartwatch provider hubs (DualWell Athlete Simulator, Apple HealthKit, Wear OS Health Connect, Fitbit), manual sync action, duplicate deduplication, telemetry charts (HR, HRV, steps, sleep stages), and provenance tags (`[WEARABLE LIVE]`, `[SIMULATED DEMO]`, `[MANUAL ENTRY]`).
3. **Academic Calendar:** Coursework management, exam priorities, study sessions, conflict detection against athletic sessions, and standard RFC 5545 iCalendar (`.ics`) export.
4. **Smart Scheduler:** AI-driven timetable recommendation engine. Automatically detects time clashes and sleep window encroachments, proposes non-destructive adjustments, and requires student confirmation before applying.
5. **Nutrition & Hydration:** Daily water intake ring, quick-add (+250 mL, +500 mL), timestamped logging, meal tracker with macronutrient estimation, and contextual suggestions.
6. **Sleep & Recovery:** Circadian bedtime and wind-down planner, next-day academic/training demand preview, 7-day sleep duration charts, and sleep stage architecture analysis.
7. **Recovery Guide:** Gentle mobility routines (Thoracic reset, Hip flexor release, Parasympathetic downregulation), warm-up/cool-down protocols, fatigue self-check modal, energy-aware study modes, and medical disclaimers.
8. **Priority Rescue Mode:** 60-second cognitive triage breakdown: **DO NOW** (single sprint), **DO NEXT**, **SAFELY POSTPONE**, training modification advice, and fuel/fluid directives.
9. **Weekly Insights:** 7-day analytics across academic hours, training volume, sleep consistency, hydration streaks, and risk-tier distribution (Green, Yellow, Red days).
10. **Privacy & Settings:** Biometric telemetry consent toggles, quiet hours configuration, student baseline targets, complete data portability (structured JSON export), and account deletion.

---

## 6. Dual-Load Calculation Formulas

- **Academic Load ($0 \le S_{acad} \le 100$):** Weighted hours of classes, assignments, and study sessions, augmented by exam proximity within 48 hours ($+18$ to $+35$ pts) and penalties for consecutive study blocks exceeding 3.5 hours.
- **Athletic Load ($0 \le S_{ath} \le 100$):** Session duration multiplied by exertion tier (`all_out` $1.2\times$, `high` $0.9\times$, `moderate` $0.5\times$, `light` $0.3\times$) plus 7-day training frequency bonuses.
- **Recovery Score ($10 \le S_{rec} \le 100$):** $55\%$ sleep duration relative to configured target $+ 45\%$ nocturnal HRV rMSSD baseline minus subjective muscle soreness/mental fatigue penalties.
- **Combined Dual-Load Risk ($0 \le R \le 100$):**
  $$R = \min\left(100, \, \left(\frac{0.45 \times S_{acad} + 0.40 \times S_{ath}}{85.0} \times 100\right) \times \left(\frac{1.0 + \frac{100 - S_{rec}}{100} \times 0.50}{1.25}\right)\right)$$
- **Tiers:**
  - **GREEN ($R < 42.0$):** Optimal physiological balance.
  - **YELLOW ($42.0 \le R < 70.0$):** Elevated strain; proactive schedule adjustments advised.
  - **RED ($R \ge 70.0$):** High overload risk; activate Priority Rescue Mode.

---

## 7. Automated Test Verification

DualWell includes comprehensive automated test suites located in `backend/tests/`:
```powershell
cd backend
.\venv\Scripts\python -m pytest -v
```
The suite defaults to an isolated throwaway SQLite file. To run it against a
**dedicated** PostgreSQL test database instead, set `DATABASE_URL` first
(the session drops all tables in that database when it finishes):
```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres@localhost:5432/dualwell_test"
.\venv\Scripts\python -m pytest -v
```

### Verified Test Results:
- **`tests/test_auth.py`**
  - `test_user_registration`: PASSED
  - `test_duplicate_registration_rejected`: PASSED
  - `test_invalid_login_credentials`: PASSED
  - `test_protected_me_endpoint`: PASSED
  - `test_unauthorized_access_rejected`: PASSED
  - `test_student_profile_update`: PASSED
- **`tests/test_wearable.py`**
  - `test_wearable_status_endpoint`: PASSED
  - `test_wearable_demo_sync_and_duplicate_prevention`: PASSED
  - `test_wearable_providers_documentation`: PASSED
- **`tests/test_load_risk.py`**
  - `test_missing_wearable_metrics_graceful_handling`: PASSED
  - `test_high_academic_and_athletic_load_triggers_risk`: PASSED
  - `test_risk_recalculation_api`: PASSED
- **`tests/test_scheduler.py`**
  - `test_calendar_conflicts_detection`: PASSED
  - `test_dynamic_scheduler_recommendations_and_apply`: PASSED
- **`tests/test_lifestyle.py`**
  - `test_meal_logging`: PASSED
  - `test_hydration_logging_and_quick_add`: PASSED
  - `test_sleep_and_personalized_planner`: PASSED
  - `test_recovery_checkin`: PASSED
- **`tests/test_privacy.py`**
  - `test_privacy_settings_update`: PASSED
  - `test_student_data_export`: PASSED
  - `test_student_data_isolation`: PASSED
  - `test_weekly_insights`: PASSED

**Result:** `22 passed in 13.7s (100% pass rate)`

---

## 8. Smartwatch Hardware Connection Guide

Please refer to `docs/WEARABLE_INTEGRATION_GUIDE.md` for complete architectural instructions on linking physical Apple Watch, Wear OS, and Fitbit devices with DualWell.
