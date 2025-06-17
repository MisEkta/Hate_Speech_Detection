import streamlit as st
import time
from datetime import datetime

def render_text_analysis(
    api_status, include_policies, include_reasoning, auto_analyze,
    analyze_text, API_BASE_URL, get_classification_style, create_confidence_chart
):
    """
    Renders the Text Analysis page.
    Allows users to input text, analyze it for hate speech, and view results and statistics.
    """
    st.header("📝 Text Analysis")
    col1, col2 = st.columns([2, 1])

    # --- Text input and analyze button ---
    with col1:
        text_input = st.text_area(
            "Enter text to analyze:",
            height=150,
            placeholder="Type or paste the text you want to analyze for hate speech...",
            help="Enter any text content for analysis. The system will classify it and provide detailed insights."
        )
        analyze_button = st.button("🔍 Analyze Text", type="primary", disabled=not api_status)
        # Optionally auto-analyze if enabled and text is long enough
        if auto_analyze and text_input and len(text_input.strip()) > 10:
            analyze_button = True
            time.sleep(0.5)

    # --- Quick stats column ---
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
        else:
            st.info("No analysis history yet. Start by analyzing some text!")

    # --- Analysis logic and result display ---
    if analyze_button and text_input and api_status:
        with st.spinner("🔄 Analyzing text..."):
            result = analyze_text(API_BASE_URL, text_input, include_policies, include_reasoning)
        if result["success"]:
            data = result["data"]
            # Store analysis in session history for download/history page
            st.session_state.analysis_history.append({
                "text": text_input[:100] + "..." if len(text_input) > 100 else text_input,
                "timestamp": datetime.now().isoformat(),
                "classification": data["classification"],
                "source": "Text"  # Mark as text analysis
            })
            st.header("🎯 Analysis Results")
            classification = data["classification"]
            label = classification.get("label", "Unknown")
            confidence = classification.get("confidence", 0)
            style_class = get_classification_style(label)
            # Show classification result with colored bar
            st.markdown(f"""
            <div class="{style_class}">
                <h3>Classification: {label}</h3>
                <p>Confidence: {confidence:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            # Show confidence chart if available
            confidence_chart = create_confidence_chart(classification)
            if confidence_chart:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.plotly_chart(confidence_chart, use_container_width=True)
            # Show classification details if available
            if "details" in classification:
                with st.expander("📋 Classification Details"):
                    st.json(classification["details"])
            # Show relevant policies if available
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
            # Show AI reasoning if available
            if "reasoning" in data and data["reasoning"]:
                st.header("🧠 AI Reasoning")
                st.markdown(f"""
                <div class="reasoning-box">
                    {data["reasoning"]}
                </div>
                """, unsafe_allow_html=True)
            # Show recommended actions if available
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
            # Show analysis metadata
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