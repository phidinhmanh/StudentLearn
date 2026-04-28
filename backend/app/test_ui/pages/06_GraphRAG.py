import streamlit as st
import requests
import json
from app.test_ui.config import config

st.set_page_config(page_title="GraphRAG Chat", page_icon="🧬")

st.title("🧬 GraphRAG Knowledge Explorer")
st.markdown("""
This tool allows you to query the **StudentLearn Knowledge Graph** using a hybrid RAG approach:
- **Neo4j**: Fetches structured relationships from the graph.
- **Web Search**: Complements with real-time genetic/scientific information.
- **Gemini**: Synthesizes a professional, evidence-based answer.
""")

# Initialize session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar options
with st.sidebar:
    st.header("Settings")
    session_id = st.text_input("Session ID", value="demo-user-session")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.markdown("""
    ### Example Questions:
    - What diseases are related to the BSG gene?
    - Find genes associated with diabetes.
    - Which proteins interact with BSG?
    - What is the relationship between insulin and glucose?
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a scientific question..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend API
    with st.chat_message("assistant"):
        with st.spinner("Analyzing knowledge graph and searching web..."):
            try:
                url = f"{config.backend_base_url}/api/v1/graph-rag/query"
                payload = {
                    "query": prompt,
                    "session_id": session_id
                }
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
