from flask import Flask, jsonify, request
import os
import socket
import time
import uuid

app = Flask(__name__)

tasks = []
sessions = []

POMODORO_DURATION = 25 * 60  # 25 minutes
SHORT_BREAK_DURATION = 5 * 60  # 5 minutes
LONG_BREAK_DURATION = 15 * 60  # 15 minutes


@app.route("/health")
def health():
    return jsonify(status="ok", hostname=socket.gethostname())


@app.route("/")
def index():
    return jsonify(
        message="pomidor - pomodoro timer",
        version=os.environ.get("APP_VERSION", "dev0"),
    )


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks=tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(force=True)
    title = data.get("title")
    if not title:
        return jsonify(error="title is required"), 400
    task = {
        "id": str(
            uuid.uuid4()),
        "title": title,
        "done": False,
        "pomodoros": 0}
    tasks.append(task)
    return jsonify(task=task), 201


@app.route("/tasks/<task_id>/complete", methods=["POST"])
def complete_task(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            return jsonify(task=t)
    return jsonify(error="task not found"), 404


# ---- Pomodoro sessions ----

@app.route("/pomodoro/start", methods=["POST"])
def start_pomodoro():
    data = request.get_json(force=True)
    task_id = data.get("task_id")
    # focus | short_break | long_break
    session_type = data.get("type", "focus")

    duration_map = {
        "focus": POMODORO_DURATION,
        "short_break": SHORT_BREAK_DURATION,
        "long_break": LONG_BREAK_DURATION,
    }
    if session_type not in duration_map:
        return jsonify(error="invalid session type"), 400

    session = {
        "id": str(uuid.uuid4()),
        "task_id": task_id,
        "type": session_type,
        "duration_seconds": duration_map[session_type],
        "started_at": time.time(),
        "completed": False,
    }
    sessions.append(session)
    return jsonify(session=session), 201


@app.route("/pomodoro/<session_id>/complete", methods=["POST"])
def complete_pomodoro(session_id):
    for s in sessions:
        if s["id"] == session_id:
            s["completed"] = True
            if s["type"] == "focus" and s["task_id"]:
                for t in tasks:
                    if t["id"] == s["task_id"]:
                        t["pomodoros"] += 1
            return jsonify(session=s)
    return jsonify(error="session not found"), 404


@app.route("/pomodoro", methods=["GET"])
def list_sessions():
    return jsonify(sessions=sessions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
