import streamlit as st
from pathlib import Path
from pyvis.network import Network
import tempfile
import os

from app.test_ui.components.helpers import (
    fetch_graph_visualization,
    initialize_session_state,
    go_to_step,
)
from app.test_ui.components.layout import render_sidebar

_pages_dir = Path(__file__).parent

COLOR_MAP = {
    0: "#9e9e9e",  # Gray - Locked
    1: "#f44336",  # Red - Hổng/Đỏ
    2: "#ffc107",  # Gold - Khá/Vàng
    3: "#4caf50",  # Green - Tốt/Xanh lá
}

LEVEL_LABELS = {
    0: "Khoá (Locked)",
    1: "Chưa biết (Đỏ)",
    2: "Cần ôn (Vàng)",
    3: "Đã thành thạo (Xanh)",
}


def main() -> None:
    initialize_session_state()
    st.session_state["active_step"] = "graph"
    render_sidebar()
    st.title("Đồ thị tri thức")

    doc_id = st.session_state.get("uploaded_doc_id")
    if not doc_id:
        st.warning("Chưa có tài liệu. Vui lòng upload tài liệu trước.")
        if st.button("Quay lại Upload"):
            go_to_step("upload")
            st.switch_page(str(_pages_dir / "01_Upload.py"))
        return

    graph_data = st.session_state.get("graph_data")
    if graph_data is None:
        with st.spinner("Đang tải đồ thị tri thức..."):
            try:
                graph_data = fetch_graph_visualization(doc_id)
                st.session_state["graph_data"] = graph_data
            except RuntimeError as exc:
                st.error(f"Không lấy được đồ thị: {exc}")
                return
            except Exception as exc:
                st.error(f"Lỗi không xác định: {exc}")
                return

    nodes = graph_data.get("nodes", [])
    links = graph_data.get("links", [])

    if not nodes:
        st.info("Chưa có topics nào được trích xuất từ tài liệu này.")
        if st.button("Quay lại Topics"):
            go_to_step("topics")
            st.switch_page(str(_pages_dir / "02_Topics.py"))
        return

    st.write(f"**{len(nodes)}** chủ đề, **{len(links)}** mối quan hệ")

    with st.expander("Xem chú giải màu sắc", expanded=True):
        for level, color in COLOR_MAP.items():
            st.markdown(
                f'<span style="display:inline-block;width:16px;height:16px;'
                f'background-color:{color};border-radius:50%;margin-right:8px;"></span>'
                f"**{LEVEL_LABELS[level]}**",
                unsafe_allow_html=True,
            )

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333")
    net.force_id_atlas = False

    for node in nodes:
        level = node.get("skill_level", 1)
        color = COLOR_MAP.get(level, COLOR_MAP[1])
        label = node.get("label", node["id"])
        node_type = node.get("type", "concept")
        title = f"{label}\nLoại: {node_type}\nTrình độ: {LEVEL_LABELS.get(level, 'Không rõ')}"
        net.add_node(
            node["id"],
            label=label,
            color=color,
            title=title,
        )

    for link in links:
        net.add_edge(
            link["source"],
            link["target"],
            title=link.get("type", "relatedTo"),
        )

    net.options = {
        "nodes": {
            "shape": "dot",
            "size": 20,
            "font": {"size": 14, "face": "arial"},
            "borderWidth": 2,
        },
        "edges": {
            "color": {"inherit": "both"},
            "smooth": {"type": "continuous"},
        },
        "physics": {
            "forceAtlas2Based": {"gravitationalConstant": -50, "springLength": 150},
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 100},
        },
        "interaction": {"hover": True, "tooltipDelay": 100},
    }

    tmp_path = tempfile.mktemp(suffix=".html")
    try:
        net.save_graph(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    st.components.v1.html(html_content, height=610)

    st.divider()
    st.caption("Tương tác: Kéo thả các nút để di chuyển, cuộn chuột để phóng to/thu nhỏ, di chuột qua nút để xem chi tiết.")


main()