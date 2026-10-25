# DualWell QA Report

Date: 2026-10-25
Scope: local run, visual walkthrough, known-bug fixes, structure audit, gap development, final regression.

---

## PHASE 1 — Environment and start-up

| # | Check | Command | Result | Status |
|---|-------|---------|--------|--------|
| 1.1 | Python venv exists & deps importable | `venv/Scripts/python.exe -c "import fastapi, sqlalchemy, pytest, alembic"` | exit 0 | PASS |
| 1.2 | Frontend deps | `cd frontend && npm ci` | `NPM_CI_EXIT=0` | PASS |
| 1.3 | Backend start | `uvicorn app.main:app --reload --port 8000` (from backend/) | running, log: backend.log | PASS |
| 1.4 | Frontend start | `npm run dev` (port 5173) | running, log: frontend-dev.log | PASS |
| 1.5 | Health endpoint | `curl http://localhost:8000/api/health` | HTTP 200 `{"status":"healthy","service":"DualWell API","version":"1.0.0","database":"connected"}` | PASS |
| 1.6 | Swagger docs | `curl -o /dev/null -w "%{http_code}" http://localhost:8000/docs` | HTTP 200 | PASS |
| 1.7 | Frontend reachable | `curl -o /dev/null -w "%{http_code}" http://localhost:5173` | HTTP 200 | PASS |
| 1.8 | Test suite | `pytest` | 59 passed | PASS |
| 1.9 | Production build | `npm run build` | exit 0 | PASS |
| 1.10 | Lint | `npx oxlint src` | 0 errors, 67 warnings | WARN (tracked in Phase 4) |

Re-verified 2026-10-25 after the host restart: backend (uvicorn, PID logged in
`backend_run.log`) and frontend (vite) both restarted clean, health endpoint 200
on the first poll.

---

## PHASE 2 — Visual walkthrough

Method: scripted headless Edge pass (login → one-click as Alex Morgan → every
sidebar tab), 1440×900, full-page capture per screen, plus a manual review in
the browser panel. Console errors, page errors, and any HTTP ≥ 400 response are
collected during the run.

| # | Screen | Heading rendered | Charts | Console/network errors | Status |
|---|--------|------------------|--------|-------------------------|--------|
| 2.1 | Login | One-Click Login / Sign In / Create Account | – | none | PASS |
| 2.2 | Dashboard | Student Performance Dashboard | 5 Recharts | none | PASS |
| 2.3 | Wearable Monitoring | Wearable Monitoring & Device Telemetry | 1 | none | PASS |
| 2.4 | Academic Calendar | Academic Calendar & Workload Manager | – | none | PASS |
| 2.5 | Smart Scheduler | Smart Dynamic Scheduler | – | none | PASS |
| 2.6 | Nutrition & Hydration | Nutrition & Daily Hydration | – | none | PASS |
| 2.7 | Sleep & Recovery | Personalized Sleep Planner & Circadian Rhythm | 1 | none | PASS |
| 2.8 | Recovery Guide | Recovery & Active Rehabilitation Guide | – | none | PASS |
| 2.9 | Priority Rescue Mode | Rescue Mode Active — Energy Level: … | – | none | PASS |
| 2.10 | Weekly Insights | Weekly Insights & Predictive Analytics | 4 | none | PASS |
| 2.11 | Privacy & Settings | Privacy Controls, Data Rights & Student Profile | – | none | PASS |

- Body-text scan for `undefined`, `NaN`, `[object Object]`, `Infinity`,
  `Invalid Date`: **0 hits on all 11 screens**.
- Screenshots: `screenshots/01-login.png` … `screenshots/11-privacy.png`
  (regenerated after the Phase 3 fixes). The earlier session's
  `03b-wearable-telemetry.png`, `04-calendar-ok.png`, `05-scheduler-ok.png`,
  `05-scheduler-final.png`, `06-nutrition-final.png` are superseded duplicates
  kept for reference; `07`–`10` from 2026-10-24 23:40 were byte-identical
  blank captures and have been replaced.
- Cosmetic note: the sidebar truncates the label to `Priority Rescue…` beside
  the `SOS` badge at the 256 px sidebar width. Cosmetic only, no functional
  impact.

**Data-consistency defect found during the walkthrough** → carried to Phase 3.

---

## PHASE 3 — Known-bug fixes

### 3.1 Demo data rot (root cause of most Phase 2 anomalies)
`backend/dualwell.db` was last seeded on 2026-10-17 while `seed.py` generates
all academic/training rows *relative to today*. By 2026-10-25 every seeded event
was in the past, so:
`GET /api/load-risk/current` → `academic 0.0, athletic 0.0, risk 0 GREEN` while
the UI still showed "3 pending coursework deliverables", and
`GET /api/insights/weekly` reported "0.0 hours scheduled across 0 academic
sessions" with `0/0` deliverables.

**Fix:** regenerated the demo persona with the documented reseed path
(`python -m app.seed --reseed`), which rebuilds every row relative to the
current date. Backups: `backend/dualwell.db.bak-20261025-101425`,
`backend/dualwell.db.bak-20261025-105017`.

**Verification:** `academic 4.5 h across 2 sessions`, `training 75 min`,
`completed 1 / pending 1 / total 2`, risk `RED 70.9`.

### 3.2 Weekly Insights invented metrics (`backend/app/services/insights_engine.py`)
- Missing snapshot → synthetic ramp `55 + (i*3) % 20` plotted as if measured.
- Missing hydration → hard-coded `2200 mL` (made "days meeting 2L+" report 100 %).
- Missing sleep → hard-coded `7.5 h`.
- `meal_logging_consistency = meals/21`, but `80.0` when there were no logs →
  reported **9.5 %** on the freshly seeded demo and an invented 80 % for a new
  user.

**Fix:** no-data days now report `0`, hydration/sleep use only real logs, and
meal consistency is the share of days with ≥ 1 logged meal (`days_with_meals/7`).

**Verification:** `meal 100.0`, `hydration 85.7`, `sleep 83.5`, every
`daily_trends` point traceable to a seeded row (`water 2050` historic days,
`1850` today).

### 3.3 Seeded snapshot/assessment disagreed with the live engine
`seed.py` wrote a hand-made 7-day snapshot ramp including *today*
(`YELLOW 57.2`) and a hard-coded `RiskAssessment YELLOW 54.2`, while
`GET /api/load-risk/current` returned `RED 70.9`. Consequences: Dashboard
header said **Overload Triage (RED)** while Weekly Insights showed
`0 red days`, and Rescue Mode offered a "Moderate" energy plan.

**Fix:** the synthetic ramp now covers the 6 *past* days only, and today's
snapshot + assessment are produced by the real explainable engine
(`risk_predictor.predict_risk`) over the rows just seeded. Because
`SessionLocal` runs with `autoflush=False`, the seed explicitly `db.commit()`s
before evaluating — otherwise the engine queries an empty day and stores
`0/0/GREEN`.

**Verification:** live risk, today's snapshot, and the insights trend row are
byte-for-byte the same numbers
(`87.9 / 79.0 / 88.2 → RED 70.9`); `risk_distribution = 0 green, 6 yellow,
1 red`; Rescue Mode headline changed to `Energy Level: Depleted`.

### 3.4 Schema drift — the documented `alembic check` was failing
`python -m alembic check` (documented in README §1) failed with
`New upgrade operations detected: [add_constraint uq_user_daily_snapshot]`.
The dev database had been stamped at head `59aeca45b084` while actually being
created before that unique constraint existed, and `Base.metadata.create_all`
never alters existing tables — so `upgrade head` was a permanent no-op and the
`(user_id, snapshot_date)` uniqueness the upsert relies on was absent.

**Fix:** rebuilt the dev database from the migration chain
(`python manage.py migrate`) and reseeded (server startup seed), after backing
the file up. Fresh schema contains
`CONSTRAINT uq_user_daily_snapshot UNIQUE (user_id, snapshot_date)`.

**Verification:** `alembic check` → `No new upgrade operations detected.`;
`/api/load-risk/history` returns 7 rows across 7 distinct dates.

---

## PHASE 4 — Structure audit

| # | Check | Result | Status |
|---|-------|--------|--------|
| 4.1 | Tables vs README claim of 15 | 15 application tables (+ `alembic_version`) | PASS |
| 4.2 | Models vs migrations | `alembic check` clean after 3.4 | PASS |
| 4.3 | API surface vs `docs/API_DOCUMENTATION.md` | 53 live endpoints, 40 documented → **13 undocumented** | GAP → fixed |
| 4.4 | Documented endpoints that don't exist | 0 | PASS |
| 4.5 | Frontend modules vs README §5 | 10 modules + Privacy & Settings = 11 pages, all lazy-loaded | PASS |
| 4.6 | Backend routers vs frontend pages | every page has backing endpoints; no orphan UI | PASS |
| 4.7 | Lint | `npx oxlint src` → 0 errors, 67 warnings (React hooks `set-state-in-effect`, exhaustive-deps) | WARN |
| 4.8 | Test count vs README §7 | README lists 22 named tests; suite actually runs **59** | DOC DRIFT (informational) |
| 4.9 | Routing | sidebar state machine, no client-side router: no deep links, refresh always lands on Dashboard | OBSERVATION |

**Gap closed in this pass:** added `docs/API_DOCUMENTATION.md` §11 covering the
13 missing routes — `GET /`, `GET /api/health`, `POST /api/auth/refresh`,
`PUT`/`DELETE /api/training/sessions/{id}`, `POST /api/scheduler/generate`,
`GET /api/lifestyle/recovery-checkin/latest`,
`GET`/`PUT /api/privacy/settings`, `GET /api/recovery-guide/content`,
`POST /api/wearable/connect/{id}`, `POST /api/wearable/disconnect/{id}`,
`POST /api/wearable/observations`. Re-audit: 53 live / 53 documented.

---

## PHASE 5 — Gap development

| # | Gap | Action | Status |
|---|-----|--------|--------|
| 5.1 | Demo persona only had 1 night of sleep, 1 day of meals/hydration → charts and weekly metrics had almost nothing to read | `seed.py` now writes 7 nights of sleep, 3 meals × 7 days, hydration for the full window (today intentionally still in progress at 1850/2800 mL); stage hours, awake minutes and efficiency are derived from time-in-bed so they stay self-consistent | DONE |
| 5.2 | Insights fell back to fabricated numbers instead of zeros | fallbacks removed (3.2) | DONE |
| 5.3 | 13 API routes undocumented | `docs/API_DOCUMENTATION.md` §11 added (4.3) | DONE |
| 5.4 | Missing DB-level uniqueness for daily snapshots on existing installs | schema rebuilt from migrations so the constraint is real and enforced (3.4) | DONE |
| 5.5 | No automated guard for the above | covered by the existing suite + `alembic check`; both re-run in Phase 6 | DONE |

---

## PHASE 6 — Final regression (2026-10-25, after all fixes)

| # | Check | Command | Result | Status |
|---|-------|---------|--------|--------|
| 6.1 | Backend tests (3 runs: baseline, after seed/insights edits, after DB rebuild) | `python -m pytest -q` | **59 passed** each time | PASS |
| 6.2 | Frontend build | `npm run build` | exit 0 (`✓ built in 23.72s`) | PASS |
| 6.3 | Lint | `npx oxlint src` | 0 errors, 67 warnings | WARN |
| 6.4 | Migration/model drift | `python -m alembic check` | `No new upgrade operations detected.` | PASS |
| 6.5 | Health | `curl /api/health` | 200, `database: connected` | PASS |
| 6.6 | Demo login + risk consistency | login → `/load-risk/current` vs `/load-risk/history` vs `/insights/weekly` | identical `RED 70.9 (87.9/79.0/88.2)` everywhere | PASS |
| 6.7 | Snapshot uniqueness | `/load-risk/history` | 7 rows / 7 dates | PASS |
| 6.8 | Full UI walkthrough re-run | scripted login → 11 screens | 0 console errors, 0 page errors, 0 HTTP ≥ 400, 0 `undefined`/`NaN` flags | PASS |
| 6.9 | Swagger | `curl /docs` | 200 | PASS |
| 6.10 | Endpoint documentation coverage | script diff of `/openapi.json` vs `API_DOCUMENTATION.md` | 53 / 53 | PASS |

### Known warnings / follow-ups (not blocking)
1. **67 oxlint warnings**, dominated by `react-hooks/set-state-in-effect`.
2. **No client-side routing** — deep links and browser refresh reset to
   Dashboard; state lives only in `useState`.
3. **README §7 test list is stale** (22 named tests vs 59 actually run).
4. **`datetime.utcnow()` deprecation warnings** in `seed.py`,
   `app/services/wearable/manager.py`, and `app/database.py` call sites —
   Python 3.12+ prints them on every run.
5. **Sidebar label truncation** for `Priority Rescue Mode` (cosmetic).
6. Superseded screenshots from the first pass are still in `screenshots/`
   (`03b-*`, `*-ok.png`, `*-final.png`) if historical evidence is wanted.

### How to reproduce
```bash
# backend
cd backend && ./venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
# frontend
cd frontend && npm run dev -- --port 5173
# reset the demo persona to today (safe; DB file is backed up first)
cd backend && ./venv/Scripts/python.exe -m app.seed --reseed
```
Login: **One-Click Login as Alex Morgan** (`alex.morgan@dualwell.edu` /
`DualWell2026!`).
