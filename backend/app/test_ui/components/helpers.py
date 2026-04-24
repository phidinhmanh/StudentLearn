from __future__ import annotations

from typing import Any

HealthStatus = dict[str, Any]

import requests
import streamlit as st
from jose import jwt

from app.config import get_settings
from app.test_ui.config import config

settings = get_settings()
API_PREFIX = "/api/v1"
STEP_KEYS = ["upload", "topics", "quiz", "result", "path"]


def initialize_session_state() -> None:
    defaults = {
        "token": None,
        "user_id": None,
        "user_email": None,
        "logged_in": False,
        "active_step": "upload",
        "uploaded_doc_id": None,
        "uploaded_filename": None,
        "topics": [],
        "selected_topic_id": None,
        "selected_topic_name": None,
        "quiz_id": None,
        "questions": [],
        "current_q_idx": 0,
        "answers": {},
        "submitted": False,
        "quiz_result": None,
        "learning_path": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def get_headers() -> dict[str, str]:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def build_api_url(path: str) -> str:
    return f"{config.backend_base_url}{API_PREFIX}{path}"


def _extract_payload(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def set_login_state(token: str) -> None:
    payload = _extract_payload(token)
    st.session_state["token"] = token
    st.session_state["user_id"] = payload.get("sub")
    st.session_state["user_email"] = payload.get("email")
    st.session_state["logged_in"] = True


def clear_learning_flow() -> None:
    st.session_state["active_step"] = "upload"
    st.session_state["uploaded_doc_id"] = None
    st.session_state["uploaded_filename"] = None
    st.session_state["topics"] = []
    st.session_state["selected_topic_id"] = None
    st.session_state["selected_topic_name"] = None
    st.session_state["quiz_id"] = None
    st.session_state["questions"] = []
    st.session_state["current_q_idx"] = 0
    st.session_state["answers"] = {}
    st.session_state["submitted"] = False
    st.session_state["quiz_result"] = None
    st.session_state["learning_path"] = None


def logout() -> None:
    clear_learning_flow()
    st.session_state["token"] = None
    st.session_state["user_id"] = None
    st.session_state["user_email"] = None
    st.session_state["logged_in"] = False


def request_json(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    use_auth: bool = True,
    timeout: int = 120,
) -> Any:
    headers = get_headers() if use_auth else {}
    response = requests.request(
        method=method,
        url=build_api_url(path),
        headers=headers,
        json=json,
        params=params,
        files=files,
        data=data,
        timeout=timeout,
    )
    if response.ok:
        if response.content:
            return response.json()
        return None

    detail = f"HTTP {response.status_code}"
    try:
        body = response.json()
        detail = body.get("detail", detail)
    except ValueError:
        if response.text:
            detail = response.text
    raise RuntimeError(detail)


def ensure_demo_account() -> None:
    try:
        request_json(
            "POST",
            "/auth/register",
            json={
                "email": config.demo_email,
                "password": config.demo_password,
                "name": config.demo_name,
            },
            use_auth=False,
        )
    except RuntimeError as exc:
        if "Email already registered" not in str(exc):
            raise


def login_demo_user() -> None:
    ensure_demo_account()
    token_response = request_json(
        "POST",
        "/auth/login",
        json={
            "email": config.demo_email,
            "password": config.demo_password,
        },
        use_auth=False,
    )
    set_login_state(token_response["access_token"])


def go_to_step(step: str) -> None:
    if step in STEP_KEYS:
        st.session_state["active_step"] = step


def can_access_step(step: str) -> bool:
    if not st.session_state.get("logged_in"):
        return step == "upload"

    if step == "upload":
        return True
    if step == "topics":
        return bool(st.session_state.get("uploaded_doc_id"))
    if step == "quiz":
        return bool(st.session_state.get("selected_topic_id"))
    if step == "result":
        return st.session_state.get("quiz_result") is not None
    if step == "path":
        return st.session_state.get("quiz_result") is not None
    return False


def fetch_health_status() -> HealthStatus:
    response = requests.get(build_api_url("/health"), timeout=15)
    response.raise_for_status()
    payload = response.json()
    return {
        "status": payload.get("status", "unknown"),
        "service": payload.get("service"),
        "neo4j": payload.get("neo4j") or {},
    }


def fetch_topics(doc_id: str) -> list[dict[str, Any]]:
    return request_json("GET", f"/documents/{doc_id}/topics")


def fetch_quiz(topic_id: str) -> dict[str, Any]:
    return request_json("GET", f"/quiz/{topic_id}")


def submit_quiz_answers(quiz_id: str, answers: dict[str, str]) -> dict[str, Any]:
    payload = {
        "quiz_id": quiz_id,
        "answers": [
            {"question_id": question_id, "answer": answer}
            for question_id, answer in answers.items()
        ],
    }
    return request_json("POST", "/quiz/submit", json=payload)


def fetch_learning_path(user_id: str) -> dict[str, Any]:
    return request_json(
        "GET",
        f"/learning-path/{user_id}",
        params={"goal": config.default_goal},
    )


def ingest_document(file_name: str, file_bytes: bytes, subject: str) -> dict[str, Any]:
    return request_json(
        "POST",
        "/documents/ingest",
        files={"file": (file_name, file_bytes)},
        data={"subject": subject},
    )
