import streamlit as st

from app.test_ui.components.helpers import (
    go_to_step,
)
from app.test_ui.components.layout import render_sidebar

SKILL_LABELS = {
    0: ("Xam - Chua dat", "⚫"),
    1: ("Do - Yeu", "🔴"),
    2: ("Vang - Trung binh", "🟡"),
    3: ("Xanh - Gioi", "🟢"),
}


def main() -> None:
    render_sidebar()
    st.title("Buoc 4: Ket qua quiz")

    result = st.session_state.get("quiz_result")
    if not result:
        st.warning("Chua co ket qua quiz.")
        if st.button("Quay lai Quiz"):
            go_to_step("quiz")
            st.rerun()
        return

    correct = result["correct_count"]
    total = result["total"]
    pct = int(correct / total * 100) if total > 0 else 0
    skill_level = result.get("skill_level", 0)

    color = "green" if pct >= 60 else ("orange" if pct >= 40 else "red")
    st.markdown(
        f"<h1 style='text-align:center; color:{color};'>"
        f"{correct}/{total} ({pct}%)</h1>",
        unsafe_allow_html=True,
    )

    label, emoji = SKILL_LABELS.get(skill_level, ("Khong ro", "?"))
    st.markdown(
        f"<p style='text-align:center; font-size:1.2em;'>"
        f"Skill level: {emoji} {label} (Level {skill_level}/3)</p>",
        unsafe_allow_html=True,
    )

    st.markdown(f"**Feedback:** {result.get('feedback', '-')}")

    st.divider()
    st.subheader("Chi tiet tung cau")
    for item in result.get("results", []):
        icon = "✅" if item["is_correct"] else "❌"
        with st.expander(f"{icon} {item['question_text'][:80]}..."):
            st.markdown(f"**Cau hoi:** {item['question_text']}")
            st.markdown(f"**Tra loi cua ban:** {item['user_answer']}")
            if not item["is_correct"]:
                st.markdown(f"**Dap an dung:** {item['correct_answer']}")
            expl = item.get("explanation")
            if expl:
                st.markdown(f"**Giai thich:** {expl}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lam lai Quiz", use_container_width=True):
            st.session_state["quiz_id"] = None
            st.session_state["questions"] = []
            st.session_state["current_q_idx"] = 0
            st.session_state["answers"] = {}
            st.session_state["submitted"] = False
            go_to_step("quiz")
            st.rerun()
    with col2:
        if st.button("Xem lo trinh hoc", type="primary", use_container_width=True):
            go_to_step("path")
            st.rerun()


main()