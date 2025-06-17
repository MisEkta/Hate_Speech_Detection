import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

def render_history():
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
                "Confidence": item["classification"].get("confidence", 0),
                "Source": item.get("source", "Text")  # <-- Add this line, default to Text
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
                - **Source:** {item.get('source', 'Text')}
                - **Text:** {item['text']}
                - **Classification:** {item['classification'].get('label', 'Unknown')}
                - **Confidence:** {item['classification'].get('confidence', 0):.1%}
                ---
                """)
    else:
        st.info("No analysis history yet. Analyze some text or audio to get started!")