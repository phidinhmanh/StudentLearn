import streamlit as st

from app.test_ui.components.helpers import (
    fetch_learning_path,
    go_to_step,
)
from app.test_ui.components.layout import render_sidebar

STATUS_CONFIG = {
    "ready": ("Sẵn sàng học", "🟢", "green"),
    "review": ("Can on tap", "🟡", "orange"),
    "locked": ("Khoa", "⚫", "gray"),
}


def main() -> None:
    render_sidebar()
    st.title("Buoc 5: Lo trinh hoc ca nhan")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Chua dang nhap.")
        return

    learning_path = st.session_state.get("learning_path")
    if learning_path is None:
        with st.spinner("Dang tao lo trinh hoc..."):
            try:
                learning_path = fetch_learning_path(user_id)
                st.session_state["learning_path"] = learning_path
            except RuntimeError as exc:
                st.error(f"Khong lay duoc lo trinh hoc: {exc}")
                return
            except Exception as exc:
                st.error(f"Loi khong xac dinh: {exc}")
                return

    path_items = learning_path.get("path", [])
    summary = learning_path.get("summary")
    if not path_items:
        st.info("Chua co lo trinh hoc nao. Hay lam quiz truoc.")
        if st.button("Quay lai Quiz"):
            go_to_step("quiz")
            st.rerun()
        return

    st.write(f"**{len(path_items)} topics** trong lo trinh hoc cua ban")
    if summary:
        st.caption(summary)

    st.divider()
    for idx, item in enumerate(path_items, 1):
        status = item.get("status", "ready")
        label, emoji, color = STATUS_CONFIG.get(status, ("Khong ro", "❓", "gray"))

        with st.container():
            col_icon, col_info = st.columns([1, 9])
            with col_icon:
                st.markdown(f"### {emoji}")
            with col_info:
                st.markdown(f"**{idx}. {item['name']}**")
                st.caption(f"Priority: {item.get('priority', '-')} | Status: **{label}**")
                st.caption(f"Ly do: {item.get('reason', '-')}")
                st.caption(f"Thoi gian uoc tinh: {item.get('estimated_time', '-')}")
            st.divider()


main()