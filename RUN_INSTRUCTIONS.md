# DualWell — Run in 3 Commands

Prerequisites: **Python 3.10+**, **Node.js 18+**, **npm**.

```bash
# 1. Create the backend virtual environment and install Python dependencies
python -m venv backend/venv && backend/venv/Scripts/pip install -r backend/requirements.txt

# 2. Start the API on http://localhost:8000
#    (first run creates and seeds backend/dualwell.db automatically)
cd backend && ./venv/Scripts/python -m uvicorn app.main:app --port 8000

# 3. Install frontend dependencies and start the UI on http://localhost:5173
cd frontend && npm install && npm run dev
```

Then open **http://localhost:5173** and click **"One-Click Login as Alex Morgan"**
(demo account: `alex.morgan@dualwell.edu` / `DualWell2026!` — seeded demonstration
data, not a real credential).

Swagger docs: http://localhost:8000/docs · Health check: `curl http://localhost:8000/api/health`

### Platform notes
- **macOS / Linux:** replace `Scripts/` with `bin/` in step 1 (`backend/venv/bin/pip`)
  and use `./venv/bin/python` in step 2; use `python3` if `python` is not available.
- **Windows PowerShell:** `backend\venv\Scripts\pip install -r backend\requirements.txt`,
  then `cd backend; venv\Scripts\python -m uvicorn app.main:app --port 8000`.

### Optional checks
```bash
cd backend && ./venv/Scripts/python -m pytest -q   # 59 tests
cd frontend && npm run build                       # production bundle to frontend/dist
```

Configuration lives in `backend/.env` (see `backend/.env.example` for the template;
the root `.env.example` is kept for reference). No real secrets ship with this archive.
