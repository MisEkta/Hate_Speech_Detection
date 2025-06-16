import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
import time

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
        api_status = False
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            api_status = response.status_code == 200
        except:
            api_status = False
        if api_status:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
            st.warning("Please ensure your API server is running")

    # Analysis Settings only for analysis pages
    # Define checkboxes ONCE here and use their values in the main logic
    if page == "Text Analysis" or page == "Audio Analysis":
        with st.expander("⚙️ Analysis Settings", expanded=False):
            include_policies = st.checkbox("📋 Include Policy Retrieval", value=True, key="text_policy1")
            include_reasoning = st.checkbox("🧠 Include AI Reasoning", value=True, key="text_reasoning1")
            auto_analyze = st.checkbox("⚡ Auto-analyze on input", value=False, key="text_auto1")
    
    # History controls only for history page
    if page == "History":
        with st.expander("📊 History Controls", expanded=False):
            if st.button("🗑️ Clear History"):
                st.session_state.analysis_history = []
                st.experimental_rerun()
            if st.session_state.analysis_history:
                st.write(f"Total analyses: {len(st.session_state.analysis_history)}")

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except:
        return False

def get_classification_style(label: str) -> str:
    if label.lower() in ['safe', 'not hate speech']:
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

def analyze_text(text, include_policies, include_reasoning):
    try:
        payload = {
            "text": text,
            "include_policies": include_policies,
            "include_reasoning": include_reasoning
        }
        response = requests.post(f"{API_BASE_URL}/analyze", json=payload)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected Error: {str(e)}"}

def analyze_audio(audio_bytes, include_policies, include_reasoning):
    try:
        files = {"file": audio_bytes}
        params = {
            "include_policies": str(include_policies).lower(),
            "include_reasoning": str(include_reasoning).lower()
        }
        response = requests.post(f"{API_BASE_URL}/analyze_audio", files=files, params=params)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected Error: {str(e)}"}

# --- Main Header ---
st.markdown("""
<div class="main-header">
    <h1> Hate Speech Detection System</h1>
    <p>Advanced AI-powered content moderation and policy compliance analysis</p>
</div>
""", unsafe_allow_html=True)

# # --- API Status ---
# api_status = check_api_health()
# if api_status:
#     st.sidebar.success("🟢 API Connected")
# else:
#     st.sidebar.error("🔴 API Disconnected")
#     st.sidebar.warning("Please ensure your API server is running")

# --- Page 1: Text Analysis ---
if page == "Text Analysis":
    st.header("📝 Text Analysis")
    # include_policies = st.sidebar.checkbox("📋 Include Policy Retrieval", value=True, key="text_policy2")
    # include_reasoning = st.sidebar.checkbox("🧠 Include AI Reasoning", value=True, key="text_reasoning2")
    # auto_analyze = st.sidebar.checkbox("⚡ Auto-analyze on input", value=False, key="text_auto2")

    col1, col2 = st.columns([2, 1])
    with col1:
        text_input = st.text_area(
            "Enter text to analyze:",
            height=150,
            placeholder="Type or paste the text you want to analyze for hate speech...",
            help="Enter any text content for analysis. The system will classify it and provide detailed insights."
        )
        analyze_button = st.button("🔍 Analyze Text", type="primary", disabled=not api_status)
        if auto_analyze and text_input and len(text_input.strip()) > 10:
            analyze_button = True
            time.sleep(0.5)
    with col2:
        st.header("📈 Quick Stats")
        if st.session_state.analysis_history:
            total_analyses = len(st.session_state.analysis_history)
            hate_count = sum(1 for item in st.session_state.analysis_history 
                            if 'hate' in item.get('classification', {}).get('label', '').lower())
            safe_count = sum(1 for item in st.session_state.analysis_history 
                            if 'safe' in item.get('classification', {}).get('label', '').lower())
            st.metric("Total Analyses", total_analyses)
            st.metric("Hate Speech Detected", hate_count, delta=f"{hate_count/total_analyses*100:.1f}%")
            st.metric("Safe Content", safe_count, delta=f"{safe_count/total_analyses*100:.1f}%")
        else:
            st.info("No analysis history yet. Start by analyzing some text!")

    if analyze_button and text_input and api_status:
        with st.spinner("🔄 Analyzing text..."):
            result = analyze_text(text_input, include_policies, include_reasoning)
        if result["success"]:
            data = result["data"]
            st.session_state.analysis_history.append({
                "text": text_input[:100] + "..." if len(text_input) > 100 else text_input,
                "timestamp": datetime.now().isoformat(),
                "classification": data["classification"]
            })
            st.header("🎯 Analysis Results")
            classification = data["classification"]
            label = classification.get("label", "Unknown")
            confidence = classification.get("confidence", 0)
            style_class = get_classification_style(label)
            st.markdown(f"""
            <div class="{style_class}">
                <h3>Classification: {label}</h3>
                <p>Confidence: {confidence:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            confidence_chart = create_confidence_chart(classification)
            if confidence_chart:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.plotly_chart(confidence_chart, use_container_width=True)
            if "details" in classification:
                with st.expander("📋 Classification Details"):
                    st.json(classification["details"])
            if "retrieved_policies" in data and data["retrieved_policies"]:
                st.header("📚 Relevant Policies")
                for i, policy in enumerate(data["retrieved_policies"], 1):
                    with st.expander(f"Policy {i}: {policy.get('title', 'Untitled')}"):
                        st.markdown(f"""
                        <div class="policy-card">
                            <strong>Content:</strong><br>
                            {policy.get('content', 'No content available')}
                            <br><br>
                            <strong>Relevance Score:</strong> {policy.get('score', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
            if "reasoning" in data and data["reasoning"]:
                st.header("🧠 AI Reasoning")
                st.markdown(f"""
                <div class="reasoning-box">
                    {data["reasoning"]}
                </div>
                """, unsafe_allow_html=True)
            if "recommended_action" in data and data["recommended_action"]:
                st.header("⚡ Recommended Actions")
                action_data = data["recommended_action"]
                st.markdown(f"""
                <div class="action-box">
                    <strong>Action:</strong> {action_data.get('action', 'No action specified')}<br>
                    <strong>Severity:</strong> {action_data.get('severity', 'Unknown')}<br>
                    <strong>Confidence:</strong> {action_data.get('confidence', 0):.1%}
                </div>
                """, unsafe_allow_html=True)
                if "details" in action_data:
                    with st.expander("Action Details"):
                        st.write(action_data["details"])
            with st.expander("ℹ️ Analysis Metadata"):
                st.write(f"**Timestamp:** {data['timestamp']}")
                st.write(f"**Text Length:** {len(text_input)} characters")
                st.write(f"**Policies Retrieved:** {'Yes' if include_policies else 'No'}")
                st.write(f"**Reasoning Generated:** {'Yes' if include_reasoning else 'No'}")
        else:
            st.error(f"❌ Analysis failed: {result['error']}")
    elif analyze_button and not text_input:
        st.warning("⚠️ Please enter some text to analyze")
    elif analyze_button and not api_status:
        st.error("❌ Cannot analyze: API is not connected")

# --- Page 2: Audio Analysis ---
elif page == "Audio Analysis":
    st.header("🎤 Audio Analysis")
    st.info("Audio analysis is currently disabled.")
    # include_policies = st.sidebar.checkbox("📋 Include Policy Retrieval", value=True, key="audio_policy")
    # include_reasoning = st.sidebar.checkbox("🧠 Include AI Reasoning", value=True, key="audio_reasoning")
    # st.info("Upload a WAV or MP3 audio file to transcribe and analyze for hate speech.")
    # audio_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])
    # analyze_audio_button = st.button("🔍 Analyze Audio", disabled=not (api_status and audio_file))
    # if analyze_audio_button and audio_file and api_status:
    #     with st.spinner("🔄 Transcribing and analyzing audio..."):
    #         audio_bytes = audio_file.read()
    #         result = analyze_audio(("audio." + audio_file.type.split('/')[-1], audio_bytes), include_policies, include_reasoning)
    #     if result["success"]:
    #         data = result["data"]
    #         st.session_state.analysis_history.append({
    #             "text": data.get("transcription", "[Audio transcription]"),
    #             "timestamp": datetime.now().isoformat(),
    #             "classification": data["classification"]
    #         })
    #         st.header("🎯 Analysis Results")
    #         classification = data["classification"]
    #         label = classification.get("label", "Unknown")
    #         confidence = classification.get("confidence", 0)
    #         style_class = get_classification_style(label)
    #         st.markdown(f"""
    #         <div class="{style_class}">
    #             <h3>Classification: {label}</h3>
    #             <p>Confidence: {confidence:.1%}</p>
    #         </div>
    #         """, unsafe_allow_html=True)
    #         confidence_chart = create_confidence_chart(classification)
    #         if confidence_chart:
    #             col1, col2, col3 = st.columns([1, 2, 1])
    #             with col2:
    #                 st.plotly_chart(confidence_chart, use_container_width=True)
    #         if "transcription" in data:
    #             with st.expander("📝 Transcription"):
    #                 st.write(data["transcription"])
    #         if "details" in classification:
    #             with st.expander("📋 Classification Details"):
    #                 st.json(classification["details"])
    #         if "retrieved_policies" in data and data["retrieved_policies"]:
    #             st.header("📚 Relevant Policies")
    #             for i, policy in enumerate(data["retrieved_policies"], 1):
    #                 with st.expander(f"Policy {i}: {policy.get('title', 'Untitled')}"):
    #                     st.markdown(f"""
    #                     <div class="policy-card">
    #                         <strong>Content:</strong><br>
    #                         {policy.get('content', 'No content available')}
    #                         <br><br>
    #                         <strong>Relevance Score:</strong> {policy.get('score', 'N/A')}
    #                     </div>
    #                     """, unsafe_allow_html=True)
    #         if "reasoning" in data and data["reasoning"]:
    #             st.header("🧠 AI Reasoning")
    #             st.markdown(f"""
    #             <div class="reasoning-box">
    #                 {data["reasoning"]}
    #             </div>
    #             """, unsafe_allow_html=True)
    #         if "recommended_action" in data and data["recommended_action"]:
    #             st.header("⚡ Recommended Actions")
    #             action_data = data["recommended_action"]
    #             st.markdown(f"""
    #             <div class="action-box">
    #                 <strong>Action:</strong> {action_data.get('action', 'No action specified')}<br>
    #                 <strong>Severity:</strong> {action_data.get('severity', 'Unknown')}<br>
    #                 <strong>Confidence:</strong> {action_data.get('confidence', 0):.1%}
    #             </div>
    #             """, unsafe_allow_html=True)
    #             if "details" in action_data:
    #                 with st.expander("Action Details"):
    #                     st.write(action_data["details"])
    #         with st.expander("ℹ️ Analysis Metadata"):
    #             st.write(f"**Timestamp:** {data['timestamp']}")
    #             st.write(f"**Audio Filename:** {audio_file.name}")
    #             st.write(f"**Policies Retrieved:** {'Yes' if include_policies else 'No'}")
    #             st.write(f"**Reasoning Generated:** {'Yes' if include_reasoning else 'No'}")
    #     else:
    #         st.error(f"❌ Analysis failed: {result['error']}")
    # elif analyze_audio_button and not audio_file:
    #     st.warning("⚠️ Please upload an audio file to analyze")
    # elif analyze_audio_button and not api_status:
    #     st.error("❌ Cannot analyze: API is not connected")

# --- Page 3: History ---
elif page == "History":
    st.header("📊 Analysis History")
    if st.session_state.analysis_history:
        labels = [item['classification'].get('label', 'Unknown') for item in st.session_state.analysis_history]
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        if label_counts:
            fig = px.pie(
                values=list(label_counts.values()),
                names=list(label_counts.keys()),
                title="Classification Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        df = pd.DataFrame([
            {
                "Timestamp": item["timestamp"],
                "Text": item["text"],
                "Classification": item["classification"].get("label", "Unknown"),
                "Confidence": item["classification"].get("confidence", 0)
            }
            for item in st.session_state.analysis_history
        ])
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download Analysis History as CSV",
            data=csv_buffer.getvalue(),
            file_name="analysis_history.csv",
            mime="text/csv"
        )
        if st.button("🗑️ Clear History", key="History"):
            st.session_state.analysis_history = []
            st.experimental_rerun()
        with st.expander("📜 Detailed History"):
            for i, item in enumerate(reversed(st.session_state.analysis_history[-10:]), 1):
                st.markdown(f"""
                **Analysis {i}** - {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
                - **Text:** {item['text']}
                - **Classification:** {item['classification'].get('label', 'Unknown')}
                - **Confidence:** {item['classification'].get('confidence', 0):.1%}
                ---
                """)
    else:
        st.info("No analysis history yet. Analyze some text or audio to get started!")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p> Hate Speech Detection System | Built with Streamlit & FastAPI</p>
    <p>Powered by advanced AI for content moderation and policy compliance</p>
</div>
""", unsafe_allow_html=True)