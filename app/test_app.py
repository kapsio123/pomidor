from app import app


def client():
    app.testing = True
    return app.test_client()


def test_health():
    c = client()
    response = c.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_add_task_and_list():
    c = client()
    response = c.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 201
    response = c.get("/tasks")
    titles = [t["title"] for t in response.json["tasks"]]
    assert "Test Task" in titles


def test_add_task_without_title():
    c = client()
    resp = c.post("/tasks", json={})
    assert resp.status_code == 400


def test_complete_task():
    c = client()
    resp = c.post("/tasks", json={"title": "read book"})
    task_id = resp.get_json()["task"]["id"]
    resp = c.post(f"/tasks/{task_id}/complete")
    assert resp.status_code == 200
    assert resp.get_json()["task"]["done"] is True


def test_start_pomodoro_focus_session():
    c = client()
    resp = c.post("/pomodoro/start", json={"type": "focus"})
    assert resp.status_code == 201
    data = resp.get_json()["session"]
    assert data["duration_seconds"] == 25 * 60


def test_start_pomodoro_invalid_type():
    c = client()
    resp = c.post("/pomodoro/start", json={"type": "nap"})
    assert resp.status_code == 400


def test_complete_pomodoro_increments_task_count():
    c = client()
    task_resp = c.post("/tasks", json={"title": "study terraform"})
    task_id = task_resp.get_json()["task"]["id"]

    session_resp = c.post(
        "/pomodoro/start",
        json={
            "type": "focus",
            "task_id": task_id})
    session_id = session_resp.get_json()["session"]["id"]

    c.post(f"/pomodoro/{session_id}/complete")

    tasks_resp = c.get("/tasks")
    task = [t for t in tasks_resp.get_json()["tasks"] if t["id"] == task_id][0]
    assert task["pomodoros"] == 1
