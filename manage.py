#!/usr/bin/env python3
"""DualWell cross-platform task runner (Windows, macOS, Linux).

Usage:
    python manage.py setup              Create the venv and install backend + frontend deps
    python manage.py seed [--reseed]    Seed the demo persona (add --reseed to regenerate)
    python manage.py migrate [--to REV] Apply DB migrations (default: upgrade to head)
    python manage.py test [pytest args] Run the backend pytest suite
    python manage.py build              Production frontend build (tsc + vite)
    python manage.py run                Start backend (:8000) and frontend (:5173)
    python manage.py stop               Stop whatever is listening on :8000 / :5173

Only Python 3.10+ and Node.js 18+ need to be on PATH; everything else is
created inside the project (backend/venv, frontend/node_modules).
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / "venv"
_SCRIPTS = "Scripts" if os.name == "nt" else "bin"
PY = VENV / _SCRIPTS / ("python.exe" if os.name == "nt" else "python")


def sh(cmd: str, cwd: Path, env: dict = None) -> int:
    print(f"» {cmd}   (in {cwd})")
    return subprocess.run(cmd, cwd=str(cwd), shell=True, env=env).returncode


def sh_checked(cmd: str, cwd: Path, env: dict = None) -> None:
    code = sh(cmd, cwd, env)
    if code != 0:
        sys.exit(f"[manage.py] command failed with exit code {code}: {cmd}")


def cmd_setup(_args) -> None:
    if not PY.exists():
        sh_checked(f'"{sys.executable}" -m venv "{VENV}"', ROOT)
    sh_checked(f'"{PY}" -m pip install -r requirements.txt', BACKEND)
    sh_checked("npm install", FRONTEND)
    print("[manage.py] setup complete. Demo login: alex.morgan@dualwell.edu / DualWell2026!")


def cmd_seed(args) -> None:
    flag = " --reseed" if args.reseed else ""
    sh_checked(f'"{PY}" -m app.seed{flag}', BACKEND)


def cmd_test(args) -> None:
    extra = " ".join(args.pytest_args)
    sh_checked(f'"{PY}" -m pytest {extra}'.rstrip(), ROOT)


def cmd_migrate(args) -> None:
    """Run Alembic against whatever DATABASE_URL app.config resolves."""
    sh_checked(f'"{PY}" -m alembic upgrade {args.to}', BACKEND)


def cmd_build(_args) -> None:
    sh_checked("npm run build", FRONTEND)


def _kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            proc.terminate()


def cmd_run(args) -> None:
    procs = []
    popen_kwargs = {} if os.name == "nt" else {"start_new_session": True}

    if not args.frontend_only:
        backend_env = dict(os.environ)
        backend_env["PYTHONPATH"] = str(BACKEND) + os.pathsep + backend_env.get("PYTHONPATH", "")
        # Launched from the repo root on purpose: app.config anchors the
        # SQLite database and .env to backend/ regardless of the CWD.
        procs.append(("backend", subprocess.Popen(
            f'"{PY}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000',
            cwd=str(ROOT), shell=True, env=backend_env, **popen_kwargs
        )))

    if not args.backend_only:
        procs.append(("frontend", subprocess.Popen(
            "npm run dev -- --port 5173",
            cwd=str(FRONTEND), shell=True, **popen_kwargs
        )))

    print("[manage.py] backend  -> http://localhost:8000  (docs: /docs)")
    print("[manage.py] frontend -> http://localhost:5173")
    print("[manage.py] Ctrl+C to stop both.")
    try:
        while procs:
            for entry in list(procs):
                name, proc = entry
                code = proc.poll()
                if code is not None:
                    print(f"[manage.py] {name} exited with code {code}")
                    procs.remove(entry)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[manage.py] stopping servers...")
    finally:
        for _name, proc in procs:
            _kill_tree(proc)
    print("[manage.py] stopped.")


def cmd_stop(_args) -> None:
    for port in (8000, 5173):
        if os.name == "nt":
            out = subprocess.run(
                f'netstat -ano | findstr ":{port}" | findstr LISTENING',
                shell=True, capture_output=True, text=True
            ).stdout
            pids = sorted({line.split()[-1] for line in out.strip().splitlines() if line.strip()})
            for pid in pids:
                subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
        else:
            out = subprocess.run(
                f"lsof -ti tcp:{port}", shell=True, capture_output=True, text=True
            ).stdout
            pids = sorted(set(out.split()))
            for pid in pids:
                subprocess.run(["kill", pid], capture_output=True)
        print(f"[manage.py] port {port}: stopped {len(pids)} process(es)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="create venv and install backend + frontend deps").set_defaults(func=cmd_setup)

    p_seed = sub.add_parser("seed", help="seed the demo persona (idempotent)")
    p_seed.add_argument("--reseed", action="store_true", help="wipe and regenerate demo data relative to today")
    p_seed.set_defaults(func=cmd_seed)

    p_test = sub.add_parser("test", help="run the backend pytest suite")
    p_test.add_argument("pytest_args", nargs="*", help="extra args passed through to pytest")
    p_test.set_defaults(func=cmd_test)

    p_mig = sub.add_parser("migrate", help="apply database migrations (default: upgrade to head)")
    p_mig.add_argument("--to", metavar="REV", default="head",
                       help="target revision (default: head; e.g. 'base' to roll back, "
                            "or a revision id to stop at)")
    p_mig.set_defaults(func=cmd_migrate)

    sub.add_parser("build", help="production frontend build").set_defaults(func=cmd_build)

    p_run = sub.add_parser("run", help="start backend + frontend (Ctrl+C stops both)")
    p_run.add_argument("--backend-only", action="store_true")
    p_run.add_argument("--frontend-only", action="store_true")
    p_run.set_defaults(func=cmd_run)

    sub.add_parser("stop", help="stop whatever listens on :8000 / :5173").set_defaults(func=cmd_stop)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
