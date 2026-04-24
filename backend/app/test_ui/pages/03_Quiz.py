import streamlit as st

from app.test_ui.components.helpers import (
    fetch_quiz,
    go_to_step,
    submit_quiz_answers,
)
from app.test_ui.components.layout import render_sidebar


def main() -> None:
    render_sidebar()
    st.title("Buoc 3: Lam Quiz")

    topic_id = st.session_state.get("selected_topic_id")
    if not topic_id:
        st.warning("Chua chon topic. Vui long chon topic truoc.")
        if st.button("Quay lai Topics"):
            go_to_step("topics")
            st.rerun()
        return

    topic_name = st.session_state.get("selected_topic_name", topic_id)
    st.caption(f"Topic: **{topic_name}**")

    if not st.session_state.get("questions"):
        if st.session_state.get("submitted"):
            pass
        else:
            with st.spinner("Dang tao quiz..."):
                try:
                    quiz_data = fetch_quiz(topic_id)
                    st.session_state["quiz_id"] = quiz_data["quiz_id"]
                    st.session_state["questions"] = quiz_data["questions"]
                    st.session_state["current_q_idx"] = 0
                    st.session_state["answers"] = {}
                    st.session_state["submitted"] = False
                except RuntimeError as exc:
                    st.error(f"Khong tao duoc quiz: {exc}")
                    return
                except Exception as exc:
                    st.error(f"Loi khong xac dinh: {exc}")
                    return

    questions = st.session_state.get("questions", [])
    if not questions:
        st.info("Khong co cau hoi nao trong quiz.")
        return

    current_idx = st.session_state.get("current_q_idx", 0)
    total = len(questions)
    current_q = questions[current_idx]

    progress_text = f"Cau {current_idx + 1} / {total}"
    st.progress(current_idx / total, text=progress_text)

    with st.container():
        st.subheader(f"Cau hoi {current_idx + 1}")
        st.markdown(f"**{current_q['text']}**")

        options = current_q.get("options", [])
        saved_answer = st.session_state["answers"].get(current_q["id"])

        selected = st.radio(
            "Chon dap an:",
            options=options,
            index=options.index(saved_answer) if saved_answer in options else 0,
            key=f"q_{current_idx}",
        )
        st.session_state["answers"][current_q["id"]] = selected

    col_prev, col_next, col_submit = st.columns(3)
    with col_prev:
        st.button(
            "Cau truoc",
            disabled=(current_idx == 0),
            use_container_width=True,
            on_click=lambda: _navigate(current_idx - 1),
        )
    with col_next:
        st.button(
            "Cau tiep",
            disabled=(current_idx == total - 1),
            use_container_width=True,
            on_click=lambda: _navigate(current_idx + 1),
        )
    with col_submit:
        st.button(
            "Nop bai",
            type="primary",
            use_container_width=True,
            on_click=_submit,
        )

    if st.button("Quay lai Topics"):
        go_to_step("topics")
        st.rerun()


def _navigate(new_idx: int) -> None:
    st.session_state["current_q_idx"] = new_idx


def _submit() -> None:
    quiz_id = st.session_state.get("quiz_id")
    answers = st.session_state.get("answers", {})
    if not quiz_id or not answers:
        st.warning("Vui long tra loi tat ca cau hoi truoc khi nop.")
        return

    with st.spinner("Dang cham diem..."):
        try:
            result = submit_quiz_answers(quiz_id, answers)
            st.session_state["quiz_result"] = result
            st.session_state["submitted"] = True
            go_to_step("result")
            st.rerun()
        except RuntimeError as exc:
            st.error(f"Nop bai that bai: {exc}")
        except Exception as exc:
            st.error(f"Loi khong xac dinh: {exc}")


main()