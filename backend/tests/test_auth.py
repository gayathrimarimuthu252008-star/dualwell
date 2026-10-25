def test_user_registration(client):
    response = client.post("/api/auth/register", json={
        "email": "new.athlete@dualwell.edu",
        "password": "StrongPassword123!",
        "full_name": "Taylor Swift"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new.athlete@dualwell.edu"
    assert data["user"]["full_name"] == "Taylor Swift"

def test_duplicate_registration_rejected(client):
    payload = {
        "email": "duplicate.test@dualwell.edu",
        "password": "Password123!",
        "full_name": "Dupe User"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_invalid_login_credentials(client):
    response = client.post("/api/auth/login", json={
        "email": "student.test@dualwell.edu",
        "password": "WrongPassword999!"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_protected_me_endpoint(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student.test@dualwell.edu"
    assert data["full_name"] == "Jordan Lee"

def test_unauthorized_access_rejected(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_student_profile_update(client, auth_headers):
    # Fetch profile
    res1 = client.get("/api/auth/profile", headers=auth_headers)
    assert res1.status_code == 200

    # Update profile
    res2 = client.put("/api/auth/profile", headers=auth_headers, json={
        "major": "Biomedical Engineering",
        "daily_hydration_goal_ml": 3000,
        "usual_sleep_target_hours": 8.5
    })
    assert res2.status_code == 200
    updated = res2.json()
    assert updated["major"] == "Biomedical Engineering"
    assert updated["daily_hydration_goal_ml"] == 3000
    assert updated["usual_sleep_target_hours"] == 8.5
