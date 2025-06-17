import streamlit as st
import speech_recognition as sr
from api_client import analyze_text_api
from datetime import datetime
# from app import get_classification_style, create_confidence_chart  # Make sure to import these

def record_voice_input() -> str:
    """Record and transcribe voice input"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.write("🎤 Listening... (speak into your microphone)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            try:
                st.info("Processing your speech...")
                text = recognizer.recognize_google(audio)
                st.success(f"Recognized text: {text}")
                return text
            except sr.UnknownValueError:
                st.warning("🔊 Could not understand audio. Please try again.")
            except sr.RequestError as e:
                st.error(f"🚫 Error with speech recognition service: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error accessing microphone: {str(e)}")
    return None

def get_classification_style(label: str) -> str:
    if label.lower() in ['safe', 'not a hate speech']:
        return "classification-safe"
    elif label.lower() in ['hate speech', 'hate']:
        return "classification-hate"
    else:
        return "classification-offensive"

def create_confidence_chart(classification_data):
    import plotly.graph_objects as go
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

def render_audio_analysis():
    st.header("🎤 Audio Analysis")
    st.info("You can record your voice and transcribe it in real time below.")

    API_BASE_URL = st.session_state.get("API_BASE_URL", "http://localhost:8000")
    include_policies = st.session_state.get("include_policies", True)
    include_reasoning = st.session_state.get("include_reasoning", True)

    if st.button("🎙️ Record Voice"):
        text = record_voice_input()
        if text:
            st.session_state["audio_transcribed_text"] = text

    transcribed = st.session_state.get("audio_transcribed_text", "")
    if transcribed:
        st.text_area("Transcribed Text", value=transcribed, height=100)
        if st.button("🔍 Analyze Transcribed Text"):
            with st.spinner("Analyzing..."):
                result = analyze_text_api(API_BASE_URL, transcribed, include_policies, include_reasoning)
            if result["success"]:
                data = result["data"]
                classification = data["classification"]
                label = classification.get("label", "Unknown")
                confidence = classification.get("confidence", 0)
                style_class = get_classification_style(label)
                st.header("🎯 Analysis Results")
                st.markdown(f"""
                <div class="{style_class}">
                    <h3>Classification: {label}</h3>
                    <p>Confidence: {confidence:.1%}</p>
                </div>
                """, unsafe_allow_html=True)

                # Confidence chart
                confidence_chart = create_confidence_chart(classification)
                if confidence_chart:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.plotly_chart(confidence_chart, use_container_width=True)

                # Classification details
                if "details" in classification:
                    with st.expander("📋 Classification Details"):
                        st.json(classification["details"])

                # Policies
                if "retrieved_policies" in data and data["retrieved_policies"]:
                    st.header("📚 Relevant Policies")
                    for i, policy in enumerate(data["retrieved_policies"], 1):
                        policy_title = policy.get('source', 'Untitled')
                        policy_content = policy.get('text', 'No content available')
                        policy_score = policy.get('score', 'N/A')
                        with st.expander(f"Policy {i}: {policy_title}"):
                            st.markdown(f"""
                            <div class="policy-card">
                                <strong>Content:</strong><br>
                                {policy_content}
                                <br><br>
                                <strong>Relevance Score:</strong> {policy_score}
                            </div>
                            """, unsafe_allow_html=True)

                # Reasoning
                if "reasoning" in data and data["reasoning"]:
                    st.header("🧠 AI Reasoning")
                    st.markdown(f"""
                    <div class="reasoning-box">
                        {data["reasoning"]}
                    </div>
                    """, unsafe_allow_html=True)

                # Recommended actions
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

                # Metadata
                with st.expander("ℹ️ Analysis Metadata"):
                    st.write(f"**Timestamp:** {data['timestamp']}")
                    st.write(f"**Text Length:** {len(transcribed)} characters")
                    st.write(f"**Policies Retrieved:** {'Yes' if include_policies else 'No'}")
                    st.write(f"**Reasoning Generated:** {'Yes' if include_reasoning else 'No'}")

                # --- Store in history ---
                if "analysis_history" not in st.session_state:
                    st.session_state.analysis_history = []
                st.session_state.analysis_history.append({
                    "text": transcribed[:100] + "..." if len(transcribed) > 100 else transcribed,
                    "timestamp": datetime.now().isoformat(),
                    "classification": classification,
                    "source": "Audio"
                })
            else:
                st.error(f"❌ Analysis failed: {result['error']}")