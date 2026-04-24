import sys
from pathlib import Path

# Add backend/ directory to sys.path so 'app' package is found
_backend_dir = Path(__file__).resolve().parents[2]
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Determine relative path from current file to pages directory
_pages_dir = Path(__file__).parent / "pages"

def _get_relative_path(target: str) -> str:
    """Get relative path from the main script's directory to target page."""
    target_path = Path(target)
    try:
        return str(target_path.relative_to(_pages_dir))
    except ValueError:
        return target

from app.test_ui.components.helpers import initialize_session_state
from app.test_ui.components.layout import render_sidebar

st.set_page_config(
    page_title="StudentLearn Test UI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
render_sidebar()

st.title("Module Streamlit test học sinh lớp 10")
st.write(
    "Dùng sidebar để đăng nhập tài khoản demo và đi lần lượt qua các bước upload tài liệu, chọn topic, làm quiz và xem lộ trình học."
)

if not st.session_state.get("logged_in"):
    st.info("Hãy đăng nhập tài khoản demo ở sidebar để bắt đầu.")
else:
    active_step = st.session_state.get("active_step", "upload")
    if active_step == "upload":
        st.switch_page(str(_pages_dir / "01_Upload.py"))
    elif active_step == "topics":
        st.switch_page(str(_pages_dir / "02_Topics.py"))
    elif active_step == "quiz":
        st.switch_page(str(_pages_dir / "03_Quiz.py"))
    elif active_step == "result":
        st.switch_page(str(_pages_dir / "04_Result.py"))
    elif active_step == "path":
        st.switch_page(str(_pages_dir / "05_Learning_Path.py"))
