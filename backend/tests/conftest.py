import os
import shutil
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Isolated test database. This MUST run before any `app.*` import so the
# application engine binds to a throwaway database instead of the dev one,
# and startup seeding is disabled so tests never populate the app's demo
# persona behind their back.
#
# Two modes:
#   * default          -> throwaway SQLite file (normal local runs)
#   * DATABASE_URL set to a postgres://... URL before pytest starts
#     -> that PostgreSQL database is used instead, e.g.
#        DATABASE_URL=postgresql+psycopg2://postgres@127.0.0.1:5433/dualwell_test pytest
#     CAUTION: point this at a DEDICATED test database -- the session teardown
#     drops every table (including alembic_version) to leave it pristine.
# ---------------------------------------------------------------------------
_POSTGRES_PREFIXES = ("postgres://", "postgresql://", "postgresql+")

_TEST_DB_DIR = None
if not os.environ.get("DATABASE_URL", "").startswith(_POSTGRES_PREFIXES):
    _TEST_DB_DIR = tempfile.mkdtemp(prefix="dualwell-test-")
    _TEST_DB_PATH = Path(_TEST_DB_DIR) / "test_dualwell.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"
os.environ["SEED_ON_STARTUP"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, engine, get_db
from app.core.security import hash_password
from app.models.user import User, StudentProfile, PrivacyPreference

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if not _TEST_DB_DIR:
        # PostgreSQL run: also drop Alembic's bookkeeping table so the test
        # database returns to "empty & unversioned" (a fresh
        # `alembic upgrade head` rebuilds it from scratch).
        with engine.connect() as conn:
            conn.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
            conn.commit()
    engine.dispose()
    if _TEST_DB_DIR:
        shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    user = User(
        email="student.test@dualwell.edu",
        hashed_password=hash_password("StudentPass123!"),
        full_name="Jordan Lee",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = StudentProfile(user_id=user.id)
    privacy = PrivacyPreference(user_id=user.id)
    db.add(profile)
    db.add(privacy)
    db.commit()

    return user

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "student.test@dualwell.edu",
        "password": "StudentPass123!"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
