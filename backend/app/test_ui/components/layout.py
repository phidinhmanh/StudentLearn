import streamlit as st

from app.test_ui.config import config
from app.test_ui.components.helpers import (
    can_access_step,
    fetch_health_status,
    go_to_step,
    login_demo_user,
    logout,
)

STEP_ITEMS = [
    ("upload", "1. Upload"),
    ("topics", "2. Topics"),
    ("quiz", "3. Quiz"),
    ("result", "4. Result"),
    ("path", "5. Learning Path"),
]


def render_sidebar() -> None:
    with st.sidebar:
        st.title("StudentLearn Test UI")
        st.caption("Demo cho học sinh lớp 10")
        st.caption(f"Backend: {config.backend_base_url}")

        try:
            health = fetch_health_status()
            neo4j = health.get("neo4j", {})
            neo4j_error = neo4j.get("error")
            if health.get("status") == "ok":
                st.success("Backend đang hoạt động")
            elif health.get("status") == "degraded":
                st.warning("Backend đang chạy nhưng Neo4j chưa sẵn sàng")
                if neo4j_error:
                    st.caption(f"Neo4j: {neo4j_error}")
            else:
                st.error("Backend trả về trạng thái không xác định")
        except Exception as exc:
            st.error(f"Không kết nối được backend: {exc}")

        st.divider()
        if st.session_state.get("logged_in"):
            st.write(f"Email: {st.session_state['user_email']}")
            if st.button("Đăng xuất", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.write("Tài khoản demo cố định")
            st.code(
                f"email={config.demo_email}\npassword={config.demo_password}",
                language="text",
            )
            if st.button("Đăng nhập tài khoản demo", use_container_width=True):
                try:
                    login_demo_user()
                except Exception as exc:
                    st.error(f"Đăng nhập thất bại: {exc}")
                else:
                    st.success("Đăng nhập thành công")
                    st.rerun()

        st.divider()
        st.subheader("Tiến trình")
        for step_key, step_label in STEP_ITEMS:
            disabled = not can_access_step(step_key)
            current = st.session_state.get("active_step") == step_key
            button_label = f"→ {step_label}" if current else step_label
            if st.button(button_label, key=f"nav_{step_key}", disabled=disabled, use_container_width=True):
                go_to_step(step_key)
                st.rerun()
