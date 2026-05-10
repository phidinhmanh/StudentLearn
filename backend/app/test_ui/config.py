from dataclasses import dataclass
import os


@dataclass(frozen=True)
class StreamlitConfig:
    backend_base_url: str = os.getenv("STREAMLIT_BACKEND_URL", "http://127.0.0.1:7000")
    demo_email: str = os.getenv("STREAMLIT_DEMO_EMAIL", "student10.demo@example.com")
    demo_password: str = os.getenv("STREAMLIT_DEMO_PASSWORD", "student10demo")
    demo_name: str = os.getenv("STREAMLIT_DEMO_NAME", "Hoc sinh lop 10")
    default_goal: str = os.getenv("STREAMLIT_DEFAULT_GOAL", "master_all")


config = StreamlitConfig()
