import streamlit as st
from pathlib import Path

from app.test_ui.components.helpers import (
    fetch_topics,
    fetch_recent_documents,
    go_to_step,
    initialize_session_state,
)
from app.test_ui.components.layout import render_sidebar

_pages_dir = Path(__file__).parent


def main() -> None:
    initialize_session_state()
    st.session_state["active_step"] = "topics"
    render_sidebar()
    st.title("Buoc 2: Chon Topic")

    doc_id = st.session_state.get("uploaded_doc_id")
    if not doc_id:
        try:
            docs = fetch_recent_documents()
            if docs:
                doc_id = docs[0]["id"]
                st.session_state["uploaded_doc_id"] = doc_id
                st.session_state["uploaded_filename"] = docs[0].get("filename", "file")
                st.rerun()
        except Exception:
            pass

    if not doc_id:
        st.warning("Chua co tai lieu. Vui long upload tai lieu truoc.")
        if st.button("Quay lai Upload"):
            go_to_step("upload")
            st.switch_page(str(_pages_dir / "01_Upload.py"))
        return

    topics = st.session_state.get("topics", [])
    if not topics:
        with st.spinner("Dang tai danh sach topics..."):
            try:
                topics = fetch_topics(doc_id)
                st.session_state["topics"] = topics
            except RuntimeError as exc:
                st.error(f"Khong lay duoc topics: {exc}")
                return
            except Exception as exc:
                st.error(f"Loi khong xac dinh: {exc}")
                return

    if not topics:
        st.info("Khong co topic nao duoc trich xuat tu tai lieu.")
        return

    st.write(f"**{len(topics)} topics** duoc trich xuat tu tai lieu. Chon mot topic de lam quiz.")

    selected_name = st.radio(
        "Chon topic:",
        options=[t["name"] for t in topics],
        captions=[
            f"Description: {t.get('description', '-') or '-'}"
            f"  |  Difficulty: {t.get('difficulty', '-') or '-'}"
            for t in topics
        ],
        index=None,
    )

    if st.button("Bat dau Quiz", type="primary", disabled=selected_name is None):
        chosen = next(t for t in topics if t["name"] == selected_name)
        st.session_state["selected_topic_id"] = chosen["id"]
        st.session_state["selected_topic_name"] = chosen["name"]
        st.session_state["quiz_id"] = None
        st.session_state["questions"] = []
        st.session_state["current_q_idx"] = 0
        st.session_state["answers"] = {}
        st.session_state["submitted"] = False
        st.session_state["quiz_result"] = None
        go_to_step("quiz")
        st.switch_page(str(_pages_dir / "03_Quiz.py"))

    if st.button("Quay lai Upload"):
        go_to_step("upload")
        st.switch_page(str(_pages_dir / "01_Upload.py"))


main()