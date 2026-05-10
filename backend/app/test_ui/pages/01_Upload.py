import streamlit as st
import time
from pathlib import Path

from app.test_ui.components.helpers import (
    initialize_session_state,
    go_to_step,
    ingest_document,
    get_task_status,
    get_task_detail,
    request_json,
)
from app.test_ui.components.layout import render_sidebar

st.set_page_config(layout="wide")

_pages_dir = Path(__file__).parent

SUBJECTS = ["general", "Toan", "Vat ly", "Hoa hoc", "Sinh hoc"]


def render_diagnostic_section() -> None:
    """Render a diagnostic health check section."""
    with st.expander("🔍 Kiểm tra trạng thái hệ thống", expanded=False):
        if st.button("Chạy Diagnostic", key="run_diag", use_container_width=True):
            with st.spinner("Đang kiểm tra..."):
                try:
                    res = request_json("GET", "/health/diagnostic")
                    if res:
                        st.subheader(f"Trạng thái tổng quát: {res.get('overall_status', 'unknown').upper()}")
                        for check in res.get("checks", []):
                            status_icon = "✅" if check.get("status") else "❌"
                            st.write(f"{status_icon} **{check.get('name')}**: {check.get('message')}")
                            if check.get("details"):
                                st.json(check.get("details"))
                except Exception as e:
                    st.error(f"Lỗi khi chạy diagnostic: {e}")


def _poll_with_progress(task_id: str) -> dict:
    """Poll task status until completion/failure."""
    max_retries = 240
    poll_interval = 5
    last_progress = 0
    last_message = ""
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    log_placeholder = st.empty()
    log_lines: list[str] = []
    MAX_LOG_LINES = 12

    def append_log(line: str) -> None:
        if not log_lines or log_lines[-1] != line:
            log_lines.append(line)
            if len(log_lines) > MAX_LOG_LINES:
                log_lines.pop(0)
            log_placeholder.code("\n".join(log_lines), language=None)

    for _ in range(max_retries):
        task = get_task_detail(task_id)
        status = task.get("status", "pending")
        progress = task.get("progress", 0)
        message = task.get("message", "Processing...")

        if progress > last_progress:
            step = max(1, (progress - last_progress) // 2)
            while last_progress < progress:
                last_progress = min(last_progress + step, progress)
                progress_bar.progress(last_progress / 100.0)
                status_placeholder.caption(f"⏳ {message} ({last_progress}%)")
                time.sleep(0.05)
            last_progress = progress
        elif status == "failed":
            progress_bar.progress(0)
        else:
            progress_bar.progress(max(last_progress, progress) / 100.0)
            status_placeholder.caption(f"⏳ {message} ({max(last_progress, progress)}%)")

        if message != last_message:
            ts = time.strftime('%H:%M:%S')
            append_log(f"[{ts}] {message}")
            last_message = message

        if status == "completed":
            progress_bar.progress(1.0)
            status_placeholder.caption("✅ Hoàn tất!")
            append_log(f"[{time.strftime('%H:%M:%S')}] ✅ Xử lý hoàn tất!")
            return task

        if status == "failed":
            progress_bar.progress(0)
            status_placeholder.caption("❌ Thất bại")
            append_log(f"[{time.strftime('%H:%M:%S')}] ❌ Thất bại: {message}")
            return task

        time.sleep(poll_interval)

    progress_bar.progress(last_progress / 100.0)
    status_placeholder.caption("⏰ Quá thời gian chờ")
    append_log(f"[{time.strftime('%H:%M:%S')}] ⏰ Quá thời gian chờ (10 phút)")
    return get_task_detail(task_id)


def main() -> None:
    initialize_session_state()
    render_sidebar()
    st.title("Buoc 1: Upload tai lieu")

    render_diagnostic_section()
    st.divider()

    if st.session_state.get("uploaded_doc_id"):
        st.success(
            f"Da upload thanh cong: {st.session_state.get('uploaded_filename', 'file')}"
        )
        if st.button("Di den Buoc 2: Chon Topic"):
            go_to_step("topics")
            st.switch_page(str(_pages_dir / "02_Topics.py"))
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
        try:
            file_bytes = uploaded_file.getvalue()
            ingest_res = ingest_document(
                file_name=uploaded_file.name,
                file_bytes=file_bytes,
                subject=subject,
            )

            task_id = ingest_res.get("task_id")
            if not task_id:
                st.error("Không nhận được Task ID từ Backend.")
                return

            st.info("Đang tải tài liệu và AI đang xây dựng đồ thị tri thức...")
            st.divider()

            task = _poll_with_progress(task_id)
            status = task.get("status")

            if status == "completed":
                result = task.get("result", {})
                st.session_state["uploaded_doc_id"] = result.get("doc_id")
                st.session_state["uploaded_filename"] = result.get("filename", uploaded_file.name)
                st.session_state["topics"] = []

                topics_count = result.get("topics_extracted", 0)
                edges_count = result.get("edges_created", 0)

                st.success(
                    f"Xử lý hoàn tất! Trích xuất được {topics_count} topics, "
                    f"{edges_count} edges."
                )
                st.rerun()

            elif status == "failed":
                error_data = task.get("error")
                if isinstance(error_data, dict):
                    error_code = error_data.get("error_code", "UNKNOWN")
                    detail = error_data.get("detail", "")
                    recoverable = error_data.get("recoverable", True)
                    log_id = error_data.get("log_id", "")

                    badge = "🔄" if recoverable else "🚨"
                    st.error(
                        f"{badge} Xử lý thất bại [{error_code}]: {task.get('message', 'Lỗi không xác định')}"
                    )
                    if detail:
                        st.caption(f"Chi tiết: {detail}")
                    if log_id:
                        st.caption(f"Mã log: `{log_id}` (dùng để báo cáo lỗi cho admin)")
                elif error_data:
                    st.error(f"Xử lý thất bại: {error_data}")
                else:
                    st.error(f"Xử lý thất bại: {task.get('message', 'Lỗi không xác định')}")

            else:
                st.warning("Quá trình xử lý mất quá nhiều thời gian. Vui lòng kiểm tra lại sau.")

        except RuntimeError as exc:
            st.error(f"Upload thất bại: {exc}")
        except Exception as exc:
            st.error(f"Lỗi không xác định: {exc}")


main()