import streamlit as st

from app.test_ui.components.helpers import (
    go_to_step,
    ingest_document,
)
from app.test_ui.components.layout import render_sidebar

st.set_page_config(layout="wide")

SUBJECTS = ["general", "Toan", "Vat ly", "Hoa hoc", "Sinh hoc"]


def main() -> None:
    render_sidebar()
    st.title("Buoc 1: Upload tai lieu")

    if st.session_state.get("uploaded_doc_id"):
        st.success(
            f"Da upload thanh cong: {st.session_state.get('uploaded_filename', 'file')}"
        )
        if st.button("Di den Buoc 2: Chon Topic"):
            go_to_step("topics")
            st.rerun()
        return

    st.write("Tai len tai lieu (PDF, DOCX, TXT) de he thong trich xuat knowledge graph.")
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Chon file tai lieu",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=False,
        )
    with col2:
        subject = st.selectbox("Mon hoc", SUBJECTS, index=0)

    if uploaded_file and st.button("Upload & Extract", type="primary", use_container_width=True):
        with st.spinner("Dang upload va trich xuat graph..."):
            try:
                file_bytes = uploaded_file.getvalue()
                result = ingest_document(
                    file_name=uploaded_file.name,
                    file_bytes=file_bytes,
                    subject=subject,
                )
                st.session_state["uploaded_doc_id"] = result["doc_id"]
                st.session_state["uploaded_filename"] = result["filename"]
                st.session_state["topics"] = []
                st.success(
                    f"Upload thanh cong! Trich xuat duoc {result['topics_extracted']} topics, "
                    f"{result['edges_created']} edges."
                )
                if st.button("Di den Buoc 2: Chon Topic"):
                    go_to_step("topics")
                    st.rerun()
            except RuntimeError as exc:
                st.error(f"Upload that bai: {exc}")
            except Exception as exc:
                st.error(f"Loi khong xac dinh: {exc}")


main()