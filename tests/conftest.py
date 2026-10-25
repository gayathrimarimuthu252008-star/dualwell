import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User, StudentProfile, PrivacyPreference

TEST_DATABASE_URL = "sqlite:///./test_dualwell.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db():
    connection = test_engine.connect()
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
