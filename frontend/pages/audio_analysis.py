import streamlit as st
import speech_recognition as sr

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

def render_audio_analysis():
    st.header("🎤 Audio Analysis")
    st.info("You can record your voice and transcribe it in real time below.")

    if st.button("🎙️ Record Voice"):
        text = record_voice_input()
        if text:
            st.text_area("Transcribed Text", value=text, height=100)