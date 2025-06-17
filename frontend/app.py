import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
import time

# Import page modules
from pages.text_analysis import render_text_analysis
from pages.audio_analysis import render_audio_analysis
from pages.history import render_history
from api_client import check_api_health, analyze_text_api

# --- Page config and CSS ---
st.set_page_config(
    page_title="Hate Speech Detection System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .classification-safe {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    .classification-hate {
        background: linear-gradient(90deg, #f44336, #d32f2f);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    .classification-offensive {
        background: linear-gradient(90deg, #ff9800, #f57c00);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    .policy-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .reasoning-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .action-box {
        background: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Session state ---
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# --- Sidebar Navigation ---
# --- Sidebar Beautification and Decluttering ---
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.3rem;font-weight:700;color:#667eea;margin-bottom:0.5rem;"> Hate Speech Detection</div>',
        unsafe_allow_html=True
    )

    # Navigation in expander
    with st.expander("📄 Navigation", expanded=True):
        page = st.radio(
            "Go to page:",
            ["Text Analysis", "Audio Analysis", "History"],
            index=0,
            label_visibility="collapsed"
        )

    # API Config in expander
    with st.expander("🔗 API Settings", expanded=False):
        API_BASE_URL = st.text_input(
            "API Base URL",
            value="http://localhost:8000",
            help="Enter the base URL of your hate speech detection API"
        )
        api_status = check_api_health(API_BASE_URL)
        if api_status:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
            st.warning("Please ensure your API server is running")

    # Analysis Settings only for analysis pages
    if page == "Text Analysis" or page == "Audio Analysis":
        with st.expander("⚙️ Analysis Settings", expanded=False):
            include_policies = st.checkbox("📋 Include Policy Retrieval", value=True, key="text_policy1")
            include_reasoning = st.checkbox("🧠 Include AI Reasoning", value=True, key="text_reasoning1")
            auto_analyze = st.checkbox("⚡ Auto-analyze on input", value=False, key="text_auto1")
    else:
        include_policies = True
        include_reasoning = True
        auto_analyze = False

    # History controls only for history page
    if page == "History":
        with st.expander("📊 History Controls", expanded=False):
            if st.button("🗑️ Clear History"):
                st.session_state.analysis_history = []
                st.experimental_rerun()
            if st.session_state.analysis_history:
                st.write(f"Total analyses: {len(st.session_state.analysis_history)}")

def get_classification_style(label: str) -> str:
    if label.lower() in ['safe', 'not a hate speech']:
        return "classification-safe"
    elif label.lower() in ['hate speech', 'hate']:
        return "classification-hate"
    else:
        return "classification-offensive"

def create_confidence_chart(classification_data):
    if 'confidence' in classification_data:
        confidence = classification_data['confidence']
        label = classification_data.get('label', 'Unknown')
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = confidence * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Confidence Score<br><span style='font-size:0.8em;color:gray'>{label}</span>"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        return fig
    return None

# --- Main Header ---
st.markdown("""
<div class="main-header">
    <h1> Hate Speech Detection System</h1>
    <p>Advanced AI-powered content moderation and policy compliance analysis</p>
</div>
""", unsafe_allow_html=True)

# --- Page Routing ---
if page == "Text Analysis":
    render_text_analysis(
        api_status, include_policies, include_reasoning, auto_analyze,
        analyze_text_api,  # Pass the function, not a string
        API_BASE_URL, get_classification_style, create_confidence_chart
    )
elif page == "Audio Analysis":
    render_audio_analysis()
elif page == "History":
    render_history()

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p> Hate Speech Detection System | Built with Streamlit & FastAPI</p>
    <p>Powered by advanced AI for content moderation and policy compliance</p>
</div>
""", unsafe_allow_html=True)